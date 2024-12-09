import numpy as np
from typing import TypedDict, List, Tuple, Dict, Generator, Any
from abc import ABC, abstractmethod
import asyncio
from transitions import Machine
DEBUG = True
import logging, logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
})

class Game:

    def __init__(self, players = [1,2]):
        self.board = None
        self.unplaced_pieces = {}
        self.dead_units = {}
        self.api = None
        self.rules = None
        self.game_sequence = None
        self.players = players
        self.active_player = None
        self.logger = logging.getLogger('game logger')


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

    def set_rules(self, rules: 'RuleSystem'):
        self.rules = rules

    async def start_game(self):
        print('Game Started')
        assert self.rules is not None, 'No rules set for the game.'
        await self.rules.game_sequence()

def make_id():
    i = 0
    while True:
        yield f'p{i}'
        i += 1
id_generator = make_id() 


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
        self.id = next(id_generator)
        self.game = game
        self.rules = game.rules
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



# General unit class
class Unit(Piece,ABC):
    
    def __init__(self, game: Game, name: str, player:int, position = None,  img = None):
        super().__init__(game, name=name,position=position)

        self.health = None
        self.actions = []
        self.reactions = []
        self.abilities = []
        self.movement = 0
        self.clickable = True
        self.player = player

        


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
    game: Game
    api: 'API'
    def __init__(self, game: 'Game'):
        game.set_rules(self)
        self.game = game
        self.game_turn = 0
        self.controlled_unit = None

    @abstractmethod
    async def game_sequence(self) -> Generator[Any, None, None]:
        """
        A generator that defines the sequence of steps in the game.
        Yields the next step in the game.
        """
        pass

    @abstractmethod
    def check_game_over(self) -> bool:
        pass

    @abstractmethod
    def get_available_actions(self, api):
        pass

    def set_api(self, api: 'API'):
        self.api = api

    async def get_unit_selection(self, selectable_units: list[Unit]):
        self.api.select_unit(selectable_units)
        await self.wait_for_input(selectable_units)

    async def get_option_selection(self, options: list[str]):
        self.api.select_option(options)
        await self.wait_for_input(options)

    async def get_tile_selection(self, tile_options: list[tuple[int, int]]):
        self.api.select_tile(tile_options)
        await self.wait_for_input(tile_options)

    async def wait_for_input(self, options):
        """
        Waits for input from the user.
        """
        print('Waiting for input')
        while not self.api.state == "game_running":
            await asyncio.sleep(0.1)

        # 
        if self.api.selection not in options:
            print(f'Invalid selection: {self.api.selection}. We shall try this again!')
            match type(options[0]):
                case str():
                    self.api.select_option(options)
                case tuple():
                    self.api.select_tile(options)
                case Unit():
                    self.api.select_unit(options)
            print(f'Invalid selection: {self.api.selection}')


        return True

class API():
    rules: RuleSystem
    game: Game
    board: Board
    states = ['game_running', 'wait_for_option_sel',
               'wait_for_unit_sel', 'wait_for_tile_sel']
    def __init__(self, game: 'Game', rules: RuleSystem):
        self.game = game
        self.rules = rules
        self.board = game.board
        self.current_options = []
        self.selection = None

        # Some double pointers
        self.game.api = self
        self.rules.set_api(self)


        self.machine = Machine(model=self, states=API.states, initial='game_running')

        # self.machine.add_transition(trigger='back', source='*', dest='wait_for_options')
        # self.machine.add_transition(trigger='next_game_step', source='*', dest='wait_for_options', before='next_game_step')
        
        # The game requests an input from the UI
        self.machine.add_transition(trigger='select_option', source='game_running', dest='wait_for_option_sel', before='set_options')
        self.machine.add_transition(trigger='select_unit', source='game_running', dest='wait_for_unit_sel', before='set_options')
        self.machine.add_transition(trigger='select_tile', source='game_running', dest='wait_for_tile_sel', before='set_options')
        # The UI has provided the requested input and the game continures
        self.machine.add_transition(trigger='selection_done', source=['wait_for_option_sel','wait_for_unit_sel','wait_for_tile_sel'],
                                     dest='game_running', before='set_selection')


    def set_options(self, options):
        if options == []:
            raise ValueError('No options provided')
        if options == 'do_not_set':
            return
        self.current_options = options
    
    def set_selection(self, selection):
        print(f'Selection made: {selection} of type {type(selection)}')
        self.selection = selection

    def set_active_player(self, player):
        self.game.active_player = player
    def get_active_player(self):
        return self.game.active_player