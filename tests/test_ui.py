# tests/test_ui.py

import unittest
from gameUI import UI
import engine
import onepagerules as opr

class TestUI(unittest.TestCase):
    
    def setUp(self):
        self.game = engine.Game()
        self.opr_rules = opr.OPR_Firefight(self.game)
        self.board = engine.Board(size=(10, 10), game=self.game)
        self.api = engine.GameAPI(self.game, self.opr_rules)
        self.ui = UI(self.board, self.api)

    def test_highlight_square(self):
        # Test the highlight_square logic for grid positioning
        self.ui.highlight_square((3, 3), color=(255, 0, 0))
        # Here, you'd test if the rect is created or stored correctly
        # You may mock Pygame's drawing function if needed
    
    def test_draw_text(self):
        # Test if the draw_text method renders correctly
        self.ui.draw_text("Test", (100, 100))
        # You can check if the method runs without errors and behaves as expected

    def test_move_piece(self):
        #TODO: Implement this test
        pass

    
    def test_remove_piece(self):
        # Test the remove_piece method
        piece = opr.OPRUnit(self.game, name="Soldier")

        self.assertIn(piece, self.game.unplaced_pieces.values())
        piece.place((1, 1))
        self.assertNotIn(piece, self.game.unplaced_pieces.values())
        self.assertIn(piece, self.board.pieces.values())

        piece.remove()
        self.assertNotIn(piece, self.board.pieces.values())
        self.assertIn(piece, self.game.dead_units.values())


if __name__ == '__main__':
    unittest.main()
