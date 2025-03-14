
import engine
from typing import Generator, Any
import random
DEBUG = True

class OPR_Firefight(engine.RuleSystem):
    ## A turn is done when all units on the board have taken their unit_turn
    ## The player turn and the unit_turn switch when the current unit has taken its turn
    
    async def game_sequence(self):
        """
        Implements the OnePageRules game flow as a generator.
        Yields each step to be processed by the game engine or API.
        """
        print("Game sequence started")
        # Determine initiative at the start of the game
        self.determine_initiative()

        while not self.check_game_over():
            self.game_turn += 1
            print(f"Game turn {self.game_turn} begins")

            # Handle unit activations during the game turn
            while not self.all_units_activated():

                yet_to_act_units = [unit for unit in self.game.board.pieces.values() \
                                    if (unit.player == self.game.active_player) and not unit.activated]
                
                if len(yet_to_act_units) > 0:
                    await self.get_unit_selection(yet_to_act_units)
                    while not self.api.selection in yet_to_act_units:
                        print(f"Selected unit ({self.api.selection}) not in list of available units: {yet_to_act_units}")
                        await self.get_unit_selection(yet_to_act_units)
                    self.controlled_unit = self.api.selection

                    await self.unit_turn(self.controlled_unit)
                else:
                    print(f"No units left to activate for player {self.game.active_player}")
                print(f"Unit {self.controlled_unit} turn completed")

                self.next_player()

        print(f"Game turn {self.game_turn} ends")

    async def unit_turn(self, unit: engine.Unit):
        """
        Handles the actions for a unit during its turn.
        """
        action_options = ["Hold", "Advance", "Rush", "Charge"]

        await self.get_option_selection(action_options)

        assert self.api.selection in action_options, f"Invalid action selected: {self.api.selection}"

        match self.api.selection:
            case "Hold":
                print(f"{unit} will hold position.")
                await unit.hold()

            case "Advance":
                print(f"{unit} advances.")
                await unit.advance()

            case "Rush":
                print(f"{unit} rushes.")
                await unit.rush()

            case "Charge":
                print(f"{unit} charges.")
                await unit.charge()

            case _:
                raise ValueError(f"Unknown action: {self.api.selection}")


    def determine_initiative(self) -> int:
        """
        Determines which player has the initiative.
        For now, we'll just return Player 1 for simplicity.
        """
        active_player = random.choice(self.game.players)
        self.game.api.set_active_player(active_player)
        print(f"Initiative determined: Player {self.game.active_player} goes first")

    def next_player(self) -> int:
        """ Sets the next player in the sequence. """
        self.game.active_player = (self.game.active_player % len(self.game.players)) + 1

    def all_units_activated(self) -> bool:
        """
        Returns True if all units have been activated this turn.
        """
        return all(unit.activated for unit in self.game.board.pieces.values())

    def check_game_over(self) -> bool:
        """
        Checks if the game is over, based on some condition.
        """
        # For now, the game is over after 4 turns
        return self.game_turn > 3

    def get_available_actions(self, api):
        """
        Return available actions based on the current game state.
        """
        
        assert api.controlled_unit
        # If a unit is activated, show actions for the unit
        actions = ["Hold", "Advance", "Rush", "Charge"]
 


        

        
class OPRWeapon:
    def __init__(self, name: str, range: int, attacks: int, damage: int):
        self.name = name
        self.range = range
        self.attacks = attacks
        self.damage = damage

    def __str__(self):
        return f"{self.name} (Range: {self.range}, Attacks: {self.attacks}, Damage: {self.damage})"

class OPRUnit(engine.Unit):
    def __init__(self, game: 'engine.Game', name: str, player: int, position: list[int]=None):
        super().__init__(game, name, player, position)

        # State markers
        self.activated: bool = False  # Flag to track if the unit has been activated this turn
        self.fought: bool = False  # Flag to track if the unit has fought this turn
        self.shaken: bool = False

        # Default stats
        self.movement: int = 6  # Standard movement for all units
        self.movement_rush = self.movement * 2
        self.wounds: int = 1

        # Unit stats (must be edited)
        self.quality: int = None
        self.defense: int = None
        self.weapons: list[OPRWeapon] = []  # List to hold the unit's weapons

        self.special_rules: list[str] = []  # List to hold any special rules for the unit

    def set_movement(self, movement: int):
        self.movement = movement
        self.movement_rush = movement * 2
        
    def add_weapon(self, weapon: OPRWeapon):
        self.weapons.append(weapon)

    def __str__(self):
        weapons_str = ', '.join(str(weapon) for weapon in self.weapons)
        return f"{self.name} at {self.position} with weapons: {weapons_str}"
    
    async def shoot(self, target = None):
        all_ranged_weapons = [weapon for weapon in self.weapons if weapon.range > 1]
        weapon_shot = [False for _ in all_ranged_weapons]

        while not all(weapon_shot):
            await self.rules.select_option(all_ranged_weapons[~weapon_shot])
            weapon_choice = self.rules.api.selection
            assert weapon_choice in all_ranged_weapons

            available_targets = self.game.board.in_range(self.position, weapon_choice.range)
            target = await self.rules.select_unit(available_targets)
            assert target in available_targets
    
            print(f'{self} shoots at {target}.')
            #!TODO: Implement applying damage mechanics
    
    async def melee(self, target = None):
        if target is None:
            target = await self.game.api.select_unit()
        print(f'{self} attacks {target} in melee combat.')

    def get_fields_in_range(self, rangeparam='movement'):
        return self.game.board.in_range(self.position, self.__getattribute__(rangeparam))

    async def hold(self):
        await self.shoot()

    async def advance(self):

        self.interaction_range = self.movement

        # Get movement options
        movement_options = self.get_fields_in_range()
        move_target = None
        while (not move_target in movement_options) or (self.board.is_occupied(move_target, self.extent) ):
            await self.rules.get_tile_selection(tile_options=movement_options)
            move_target = self.rules.api.selection        

        self.place(move_target)

        # Shoot
        await self.shoot()

    async def rush(self):
        # Get movement options
        self.interaction_range = self.movement_rush
        movement_options = self.get_fields_in_range('movement_rush')
        move_target = None
        while (not move_target in movement_options) or (self.board.is_occupied(move_target, self.extent) ):
            await self.rules.get_tile_selection(tile_options=movement_options)
            move_target = self.rules.api.selection        

        self.place(move_target)

    async def charge(self):
        if DEBUG:     
            print(f"{self} charges. Select move target")

        # Movement choice
        self.interaction_range = self.movement_rush
        movement_options = self.get_fields_in_range('movement_rush')
        move_target = None
        while (not move_target in movement_options) or (self.board.is_occupied(move_target, self.extent) ):
            await self.rules.get_tile_selection(tile_options=movement_options)
            move_target = self.rules.api.selection        

        if DEBUG:
            print(f"Move target: {move_target}, selecting attack target")

        # Attack choice
        attack_target_options = self.game.board.in_range(move_target, 1.5)
        attack_target = None
        while not attack_target in attack_target_options:
            await self.rules.get_unit_selection(selectable_units=attack_target_options)
            attack_target = self.rules.api.selection

        if DEBUG:
            print(f"Attack target: {attack_target}, confirming charge")
    
        # Confirm choices
        await self.rules.api.select_option(options=['Confirm charge', 'Back'])
        match self.rules.api.selection:
            case 'Confirm charge':
                self.place(move_target)
                self.melee(attack_target)
            case 'Back':
                await self.charge()
            case _:
                raise ValueError(f"Invalid button selection: {self.rules.api.selection}")
