import numpy as np
from typing import TypedDict, List, Tuple, Dict, Generator, Any
from abc import ABC, abstractmethod
import asyncio
from transitions import Machine


class Game:

    def __init__(self):
        self.board = None
        self.unplaced_pieces = {}
        self.dead_units = {}
        self.api=None

    def add_piece(self, piece, position = None):
        """
        Adds a unit to the game.
        If position is not None, places the unit on the board.
        """
        piece.board = self.board

        if position is None:
            self.unplaced_pieces[piece.id] = piece
        else:
            piece.place(position)



class Piece:
    def __init__(self, game, name, position = None, height = 0, extent=[0,0]):
        """
        position: The position of the piece on the board
        height: The height of the piece
        extent: The extent of the piece, given a list of coordinates relative to the position
        """
        self.name = name
        self.position = position # for larger models, the position is the bottom left corner
        self.height = height
        self.extent = extent 
        self.id = Piece.make_id()
        self.game = game
        self.board = self.game.board
        self.clickable = False
        self.rect = None

        if position is not None:
            self.place(position)
        else:
            self.game.unplaced_pieces[self.id] = self
    def __repr__(self):
        return f'{self.__class__.__name__}({self.id})'
    

    def place(self, new_position: list[int]):
        assert not self.board.is_occupied(new_position, self.extent),\
        f'Coordinates {new_position} already occupied with {self.board.map[*new_position]}'
        self.position = new_position
        self.board.map[*new_position] = self
        self.board.pieces[self.id] = self
        self.game.unplaced_pieces.pop(self.id, None)

    def remove(self, kill=True):
        self.board.map[*self.position] = None
        self.board.pieces.pop(self.id)
        self.position = None
        if kill:
            self.game.dead_units[self.id] = self

    @staticmethod
    def make_id():
        i = 0
        while True:
            yield f'p{i}'
            i += 1
    

# General unit class
class Unit(Piece,ABC):
    
    def __init__(self, game: Game, name: str, position = None,  img = None):
        super().__init__(game, name=name,position=position)

        self.health = None
        self.actions = []
        self.reactions = []
        self.abilities = []
        self.movement = 0
        self.clickable = True
        


class Board:

    def __init__(self, size: list[str], game, gridsize = 1):
        """
        size: The size of the board, i.e. number of squares in each dimension
        game: The game the board is associated with
        gridsize: The size of the grid squares in the unit relevant for the game system. 
                  Defaults to 1, e.g. 1 inch
        """
        self.size = size
        self.game = game
        game.board = self
        self.gridsize = gridsize
        # A dict of all units on the board identified by their id
        self.pieces = {}

        # The coordinates, containing pointers to every piece on the board
        self.map = np.full(self.size, None, dtype=object)
        self.x = np.arange(0, self.size[0], 1)
        self.y = np.arange(0, self.size[1], 1)

    def is_occupied(self, position: list[int], extent: list[int]):
        """
        position: The position to check
        extent: The extent of the piece, given a list of coordinates relative to the position
        
        Returns True if the position is occupied, False otherwise
        """

        if extent == [0,0]:
            return self.map[*position] is not None
        else:
            for i in range(extent[0]):
                for j in range(extent[1]):
                    if self.map[position[0]+i, position[1]+j] is not None:
                        return True
            return False


    def in_range(self, origin, range, type_of_interest = 'Any'):
        """
        Returns a list of coordinates of pieces within range of the origin

        origin: The origin of the range
        range: The range of the origin
        type_of_interest: The type of pieces to consider. Can be 'Any', 'Unit', 'Piece'
        """
        def is_type_of_interest(piece):
            match type_of_interest:
                case 'Any':
                    return True
                case 'Unit':
                    return isinstance(piece, Unit)
                case 'Piece':
                    return isinstance(piece, Piece)

        # First, get the rectangular box around the origin
        x_range = self.x[(self.x >= origin[0] - range)&
                         (self.x<=origin[0] + range)]
        y_range = self.y[(self.y >= origin[1] - range)&
                            (self.y<=origin[1] + range)]
        
        # Then, check if the pieces in the box are within range
        in_range = []
        for x in x_range:
            for y in y_range:
                if is_type_of_interest(self.map[x,y]):
                    # omit self
                    if x == origin[0] and y == origin[1]:
                        continue
                    #calculate actual distance
                    distance = np.sqrt((x-origin[0])**2 + (y-origin[1])**2)
                    if distance <= range:
                        in_range.append((x,y))
        return in_range
        

class RuleSystem(ABC):
    def __init__(self, game: 'Game'):
        self.game = game
        self.game_turn = 0
        self.active_player = None

    @abstractmethod
    def game_sequence(self) -> Generator[Any, None, None]:
        """
        A generator that defines the sequence of steps in the game.
        Yields the next step in the game.
        """
        pass

    # @abstractmethod
    # def get_available_actions(self, unit) -> list:
    #     pass

    @abstractmethod
    def check_game_over(self) -> bool:
        pass

    @abstractmethod
    def get_available_actions(self, api):
        pass

class GameAPI:
    def __init__(self, game: 'Game', rule_system: RuleSystem):
        """
        Initializes the API that mediates interactions between the UI/AI and the game engine.
        
        Args:
            game (Game): The Game object that contains the current state of the game.
        """
        self.game = game
        self.game.api = self
        self.board = game.board
        self.controlled_unit = None
        self.rule_system = rule_system
        self.sequence = self.rule_system.game_sequence()  # Get the game sequence generator
    

        self.possible_states = ['select_unit', 'select_tile', 
                                'select_action', 'initializing', 'game_over']
        self.state = 'initializing'

    def select_piece(self, message):
        self.state = 'select_unit'
        # wait for the player to click on something
        print('select a unit please...')

    def select_tile(self, message, options=None):
        # options is a list of coordinates
        # wait for the player to click on something
        self.state = 'select_tile'
        print('select a tile please...')

    def set_controlled_unit(self, unit: Unit):
        """
        Sets the current controlled unit (either by the player or the AI).
        
        Args:
            unit (Unit): The unit to be controlled.
        """
        if isinstance(unit, Unit):
            self.controlled_unit = unit
        else:
            raise ValueError("The controlled unit must be a valid Unit object.")
    
    def get_available_actions(self, *args, **kwargs):
        return self.rule_system.get_available_actions(self, *args,**kwargs)

    def clear_controlled_unit(self):
        """
        Clears the currently controlled unit.
        """
        self.controlled_unit = None

    def next_step(self) -> str:
        """
        Advances the game by processing the next step in the sequence.
        """
        try:
            step = next(self.sequence)
            return step
        except StopIteration:
            return "Game finished"

class API():
    states = ['wait_for_options', 'wait_for_action_sel',
               'wait_for_unit_sel', 'wait_for_tile_sel']
    def __init__(self, game: 'Game', rule_system: RuleSystem):
        self.game = game
        self.game.api = self
        self.board = game.board
        self.rule_system = rule_system
        self.machine = Machine(model=self, states=API.states, initial='wait_for_options')

        self.machine.add_transition(trigger='ready', source='*', dest='wait_for_options')
        self.machine.add_transition(trigger='present_actions', source='wait_for_options', dest='wait_for_action_sel')
        self.machine.add_transition(trigger='select_unit', source='wait_for_options', dest='wait_for_unit_sel')
        self.machine.add_transition(trigger='select_tile', source='wait_for_options', dest='wait_for_tile_sel')