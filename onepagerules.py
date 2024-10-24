
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
                    self.api.select_unit(yet_to_act_units)
                    self.controlled_unit = self.api.selection
                    self.unit_turn(self.controlled_unit)
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

        await self.api.select_action(action_options)
        assert self.api.selection in action_options

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

    def add_weapon(self, weapon: OPRWeapon):
        self.weapons.append(weapon)

    def __str__(self):
        weapons_str = ', '.join(str(weapon) for weapon in self.weapons)
        return f"{self.name} at {self.position} with weapons: {weapons_str}"
    
    def shoot(self, target = None):
        if target is None:
            target = self.game.api.select_unit()
        print(f'{self} shoots at {target}.')
    
    def melee(self, target = None):
        if target is None:
            target = self.game.api.select_unit()
        print(f'{self} attacks {target} in melee combat.')

    def get_fields_in_range(self, rangeparam='movement'):
        return self.game.board.in_range(self.position, self.__getattribute__(rangeparam))

    async def hold(self):
        await self.shoot()

    async def advance(self):
        # Get movement options
        movement_options = self.get_fields_in_range()
        await self.api.select_tile(options=movement_options)
        move_target = self.api.selection

        # Confirm choice and apply movement
        assert move_target in movement_options
        self.place(move_target)

        # Shoot
        await self.shoot()

    async def rush(self):
        # Get movement options
        movement_options = self.get_fields_in_range('movement_rush')
        await self.api.select_tile(options=movement_options)
        assert  self.api.selection in movement_options
        move_target = self.api.selection

        self.place(move_target)

    async def charge(self):
        # Movement choice
        movement_options = self.get_fields_in_range('movement_rush')
        await self.api.select_tile(options=movement_options)
        assert self.api.selection in movement_options
        move_target = self.api.selection

        # Attack choice
        attack_target_options = self.game.board.in_range(move_target, 1.5)
        await self.game.api.select_tile(options=attack_target_options)
        assert self.api.selection in attack_target_options
        attack_target = self.api.selection

        # Confirm choices
        self.api.select_option(options=['Confirm charge', 'Back'])
        match self.api.selection:
            case 'Confirm charge':
                self.place(move_target)
                self.melee(attack_target)
            case 'Back':
                await self.charge()
