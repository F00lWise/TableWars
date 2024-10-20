# tests/test_engine.py

import unittest
import engine
import onepagerules as opr

class TestGameAPI(unittest.TestCase):
    
    def setUp(self):
        # Setup a simple board and API for testing
        self.game = engine.Game()
        self.opr_rules = opr.OPR_Firefight(self.game)
        self.board = engine.Board(size=(10, 10), game=self.game)
        self.api = engine.GameAPI(self.game, self.opr_rules)

if __name__ == '__main__':
    unittest.main()
