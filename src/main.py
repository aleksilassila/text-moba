import curses

from Game.game import Game
from Server.server import Server
from Ui.ui import Ui

s = curses.initscr()

uiState = -1
uiError = ''


while True:
  ui = Ui(uiState, uiError)
  uiState = ui.state
  uiError = ''

  if ui.ip: # If connectin to a game
    try:
      game = Game(ui.ip[0], int(ui.ip[1]))
      game.connect()

      windowSize = s.getmaxyx()

      if windowSize[0] < game.size[0] or windowSize[1] < game.size[1]:
        uiError = f' Sorry, your terminal window has to be at least {game.size[1]}x{game.size[0]}. '
        uiState = -1

      else:
        game.start()
        break

    except:
      uiError = ' Error: Connection refused '
      uiState = -1

  elif ui.bind: # If hosting a game
    try:
      if ui.payload[3]['boolean']:
        gamemode = 'ffa'
      elif ui.payload[4]['boolean']:
        gamemode = 'br'

      Server(
        ui.bind[0], ui.bind[1],
        {
          'gamemode': gamemode,
          'players': ui.payload[6]['value'],
          'bullets': ui.payload[7]['value'],
          'rockets': ui.payload[8]['value'],
          'tickrate': ui.payload[10]['value']
        }
      )
      break
    except:
      uiError = ' Error: Unable to bind server to given address '
      uiState = -1

s.refresh()
curses.endwin()
