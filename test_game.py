import engine
import gameUI


game = engine.Game()
board= engine.Board([8,8], game)
ui = gameUI.UI(board)


dude = engine.Unit(game, 'Dude',[5,3])
dude.movement = 3

homo = engine.Unit(game, 'Homo', position=[2,3])

#homo.place([1,3])
ui.run()
