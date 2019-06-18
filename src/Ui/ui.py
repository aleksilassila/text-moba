import curses, sys

from Ui.menu import Menu

class Ui:
  def __init__(self, state, error):
    self.state = state # -2: exit, -1: main menu, 0: join screen, 1: host screen
    self.error = error

    self.hostSelection = 0

    self.ip = None
    self.bind = None

    self.s = curses.initscr()
    curses.curs_set(0)
    curses.noecho()

    self.w = curses.newwin(24, 80, 0, 0)
    self.w.timeout(0)

    self.mainMenu = [
      {'Label': 'Join a game', 'selectable': 1},
      {'Label': 'Host a game', 'selectable': 1}
    ]

    self.hostMenu = [
      {'Label': 'Host a game', 'skip': True},
      {'Label': '', 'skip': True},
      {'Label': 'Gamemode:'},
      {'Label': '  FFA:',              'boolean': True},
      {'Label': '  Battle Royale:',    'boolean': False},
      {'Label': '', 'skip': True},
      {'Label': 'Max players:',        'value': 4},
      {'Label': 'Max bullets in air:', 'value': 15},
      {'Label': 'Max rockets in air:', 'value': 1},
      {'Label': '', 'skip': True},
      {'Label': 'Tickrate:',           'value': 20},
      {'Label': '', 'skip': True},
      {'Label': 'Continue', 'selectable': 1}
    ]

    if self.state == -1:
      try:
        self.drawBackground()
        self.w.getch()
        m = Menu(self.mainMenu, 4, 19, 15, (80 - 19)//2)
        m.createMenu()
        self.state = m.selection
      except KeyboardInterrupt:
        sys.exit()

    elif self.state == 0:
      try:
        self.w.erase()
        self.w.getch()
        m = Menu(None, 3, 24, 12, (80 - 24)//2, message = ' Join a server: ')
        self.ip = m.prompt()
      except KeyboardInterrupt:
        self.state = -1

    elif self.state == 1:
      try:
        m = Menu(self.hostMenu, 24, 80, 0, 0, help = '  Move: ↓↑ ─ Adjust sliders: ←→ ─ Select: Enter ─ Back: Ctrl + C  ')
        m.createMenu()

        if not m.selection == -1:
          p = Menu(None, 3, 27, 15, 2, message = ' Enter a bind address: ')
          self.bind = p.prompt()
          self.payload = m.menu
        else:
          self.state = -1
      except KeyboardInterrupt:
        self.state = -1

    else:
      self.state = -1

  def drawBackground(self):
    self.w.addstr(1, 15, " _____         _         _____ _____ _____ _____ ")
    self.w.addstr(2, 15, "|_   _|___ _ _| |_  ___ |     |     | __  |  _  |")
    self.w.addstr(3, 15, "  | | | -_|_'_|  _||___|| | | |  |  | __ -|     |")
    self.w.addstr(4, 15, "  |_| |___|_,_|_|       |_|_|_|_____|_____|__|__|")
    self.w.addstr(5, 15, "  |_| |___|_,_|_|       |_|_|_|_____|_____|__|__|")

    walls = [
      [4,4], 
      [5,4], 
      [6,4], 
      [7,4], 
      [4,5], 
      [4,6], 
      [4,7], 
      
      [30,10],
      [30,11], 
      [30,12],

      [50,8], 
      [50,9], 
      [50,10],

      [75, 4], 
      [75, 5], 
      [75, 6], 
      [74, 4],
      [73, 4],
      [72, 4],

      [15, 16],
      [21, 20],
      [52, 22],
      [70, 18]
    ]

    explosion = [
        [60, 14],
        [60, 13],
        [61, 13],
        [61, 14],
        [61, 15],
        [60, 15],
        [59, 15],
        [59, 14],
        [59, 13],
        [62, 14],
        [58, 14],
        [60, 12],
        [60, 16]
      ]

    for tile in explosion:
      self.w.addch(tile[1], tile[0], '░')

    for wall in walls:
      self.w.addch(wall[1], wall[0], '▓')

    self.w.addch(14, 20, '#')
    self.w.addch(14, 25, '.')
    self.w.addch(14, 28, '.')

    self.w.addch(12, 65, '@')

    self.w.border(0)

    self.w.addstr(0, (80 - len(self.error))//2, self.error)
    self.w.addstr(23, 2, ' Move: ↓↑ ─ Select: Enter ─ Exit: Ctrl + C ')
