import engine
import gameUI
import asyncio
import onepagerules	as opr

game = engine.Game()
board= engine.Board([8,8], game)
opr_rules = opr.OPR_Firefight(game)
api = engine.API(game, opr_rules)
ui = gameUI.UI(board, api)

dude = opr.OPRUnit(game, 'Dude', player=1, position=[5,3])
dude.movement = 1.5

homo = opr.OPRUnit(game, 'Homo', player=2, position=[2,3])
homo.movement = 5


ui.run()
asyncio.run(game.start_game())