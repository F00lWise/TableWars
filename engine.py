import numpy as np
from typing import TypedDict


class Game:

    def __init__(self):
        self.board = None
        self.unplaced_pieces = {}
        self.dead_units = {}

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
    def __init__(self, game, position = None, height = 0, extent=[0,0]):
        """
        position: The position of the piece on the board
        height: The height of the piece
        extent: The extent of the piece, given a list of coordinates relative to the position
        """
        self.position = position
        self.height = height
        self.extent = extent 
        self.id = Piece.make_id()
        self.game = game
        self.board = self.game.board
        if position is not None:
            self.place(position)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id})'
    

    def place(self, new_position: list[int]):
        assert not self.board.is_occupied(new_position, self.extent),\
        f'Coordinates {new_position} already occupied with {self.board.map[*new_position]}'
        self.position = new_position
        self.board.map[*new_position] = self
        self.board.pieces[self.id] = self

    @staticmethod
    def make_id():
        i = 0
        while True:
            yield f'p{i}'
            i += 1

class UnitStatArray(TypedDict):
    game_system: str
    

# General unit class
class Unit(Piece):
    
    def __init__(self, game: Game, basemodel: str, position = None,  img = None):
        super().__init__(game, position=position)
        self.basemodel = basemodel

        self.health = None
        self.stats = UnitStatArray()
        self.actions = []
        self.reactions = []
        self.abilities = []


class Board:

    def __init__(self, size: list[str], game):
        self.size = size
        self.game = game
        game.board = self
        # A dict of all units on the board identified by their id
        self.pieces = {}

        # The coordinates, containing pointers to every piece on the board
        self.map = np.full(self.size, None, dtype=object)

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

