
import engine
from typing import Generator, Any

class OPR_Firefight(engine.RuleSystem):
    ## A turn is done when all units on the board have taken their unit_turn
    ## The player turn and the unit_turn switch when the current unit has taken its turn
    
    def game_sequence(self) -> Generator[Any, None, None]:
        """
        Implements the OnePageRules game flow as a generator.
        Yields each step to be processed by the game engine or API.
        """
        # Determine initiative at the start of the game
        self.active_player = self.determine_initiative()
        yield f"Initiative determined: Player {self.active_player} goes first"

        while not self.check_game_over():
            self.game_turn += 1
            yield f"Game turn {self.game_turn} begins"

            # Handle unit activations during the game turn
            while not self.all_units_activated():
                unit = self.select_unit_to_activate(self.active_player)
                yield f"Player {self.active_player} activates {unit}"

                # Handle the unit's actions during its turn
                self.unit_turn(unit)
                yield f"Unit {unit} turn completed"

                # Alternate player after each unit activation
                self.active_player = self.get_next_player()
            
            # After each game turn, check if the game is over
            if self.game_turn > 3:
                yield "Game over"
                break
            
            yield f"Game turn {self.game_turn} ends"

    def determine_initiative(self) -> int:
        """
        Determines which player has the initiative.
        For now, we'll just return Player 1 for simplicity.
        """
        return 1  # Player 1 wins initiative

    def select_unit_to_activate(self, player: int) -> 'engine.Unit':
        """
        Selects the next unit to activate for the player.
        """
        # For now, return the first non-activated unit
        for unit in self.game.board.pieces.values():
            if not unit.activated:
                unit.activated = True
                return unit
        return None

    def unit_turn(self, unit: 'engine.Unit'):
        """
        Handles the actions for a unit during its turn.
        """
        # For simplicity, we'll just print that the unit moved
        yield f"{unit} is moving"
        # You could also yield any other actions the unit performs here
    
    def all_units_activated(self) -> bool:
        """
        Returns True if all units have been activated this turn.
        """
        return all(unit.activated for unit in self.game.board.pieces.values())

    def get_next_player(self) -> int:
        """
        Switches to the next player.
        For now, we'll just alternate between Player 1 and 2.
        """
        return 1 if self.active_player == 2 else 2

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
        actions = []
        
        if api.controlled_unit:
            # If a unit is activated, show actions for the unit
            actions = ["Hold", "Advance", "Rush", "Charge"]
        else:
            # If no unit is selected or active, allow unit selection
            actions = ["Select Unit"]
        
        return actions
    

    def apply_action(self, action: str, target=None):
        """
        Apply the selected action to the controlled unit.
        """
        match action:
            case "Select Unit":
                # Logic for selecting a unit (e.g., from available ones)
                self.controlled_unit = self.select_unit_to_activate()

            case "Hold":
                print(f"{self.controlled_unit} holds position.")
                self.controlled_unit.hold()

            case "Advance":
                print(f"{self.controlled_unit} advances.")
                self.controlled_unit.advance()

            case "Rush":
                print(f"{self.controlled_unit} rushes.")
                self.controlled_unit.rush()

            case "Charge":
                print(f"{self.controlled_unit} charges.")
                self.controlled_unit.charge()

            case _:
                raise ValueError(f"Unknown action: {action}")
        

        
class OPRWeapon:
    def __init__(self, name: str, range: int, attacks: int, damage: int):
        self.name = name
        self.range = range
        self.attacks = attacks
        self.damage = damage

    def __str__(self):
        return f"{self.name} (Range: {self.range}, Attacks: {self.attacks}, Damage: {self.damage})"

class OPRUnit(engine.Unit):
    def __init__(self, game: 'engine.Game', name: str, position: list[int]=None):
        super().__init__(game, name, position)

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

    def hold(self):
        self.shoot()
        self.game.api.next_step()

    def advance(self):
        movement_options = self.get_fields_in_range()
        move_target = self.game.api.select_tile(options=movement_options)
        self.place(move_target)
        self.shoot()
        self.game.api.next_step()

    def rush(self):
        movement_options = self.get_fields_in_range('movement_rush')
        move_target = self.game.api.select_tile(options=movement_options)
        self.place(move_target)
        self.game.api.next_step()

    def charge(self):
        movement_options = self.get_fields_in_range('movement_rush')
        move_target = self.game.api.select_tile(options=movement_options)

        attack_target_options = self.game.board.in_range(move_target, 1.5)
        attack_target = self.game.api.select_tile(options=attack_target_options)

        self.place(move_target)
        self.melee(attack_target)
        self.game.api.next_step()