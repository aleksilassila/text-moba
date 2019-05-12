import curses, time, sys
from Game.game import Game

if len(sys.argv) <= 1:
  print('Host address is required (ip:port)')
  time.sleep(2)
  ip, port = ('192.168.10.64', '6999')
else:
  ip, port = sys.argv[1].split(":")

s = curses.initscr()
curses.curs_set(0)
curses.noecho()

game = Game(ip, int(port))
game.connect()

while game.game == {}:
  time.sleep(0.2)

game.draw()

while True:
  game.window.border(0) # Draw border
  key = game.window.getch()

  if key == 27: # Quit if esc
    break

  if key == 87 or key == 119: # w/W, Move
    game.move(0)
  elif key == 68 or key == 100: # d/D
    game.move(1)
  elif key == 83 or key == 115: # s/S
    game.move(2)
  elif key == 65 or key == 97: # a/A
    game.move(3)
  
  if key == curses.KEY_UP: # Shoot
    game.shoot(0)
  elif key == curses.KEY_RIGHT:
    game.shoot(1)
  elif key == curses.KEY_DOWN:
    game.shoot(2)
  elif key == curses.KEY_LEFT:
    game.shoot(3)

  game.draw()

curses.curs_set(1)
curses.endwin()