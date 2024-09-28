import engine
import gameUI

global board 
board= engine.Board([8,8])

ui = gameUI.UI(board)

dude = engine.Unit('Dude', board=board)
dude.place([0,1])

homo = engine.Unit('Dude')
# !TODO make the board global!
homo.place([1,3])
ui.run()