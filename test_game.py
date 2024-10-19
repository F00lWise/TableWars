import engine
import gameUI
import onepagerules	as opr

game = engine.Game()
board= engine.Board([8,8], game)
opr_rules = opr.OPR_Firefight(game)
api = engine.GameAPI(game, opr_rules)
ui = gameUI.UI(board, api)

dude = opr.OPRUnit(game, 'Dude',[5,3])
dude.movement = 1.5

homo = opr.OPRUnit(game, 'Homo', position=[2,3])
homo.movement = 5


ui.run()
