import socket, json, threading, curses, sys

class Game:
  def __init__(self, host, port):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.address = (host, port)

    self.playerid = 0
    self.game = {}
    self.walls = []
    self.facing = 0

  def move(self, direction):
    try:
      self.s.send(bytes(json.dumps({'a': 'm', 'p': direction}) + ";", "utf-8")) # Action: Move, payload: direction
      self.facing = direction
    except:
      pass

  def shoot(self, direction, rocket = False):
    bullet = {'a': 's', 'p': [direction, 0]} # Action: shoot, payload: [direction, isRocket]
    
    if rocket:
      bullet['p'][1] = 1

    try:
      self.s.send(bytes(json.dumps(bullet) + ";", "utf-8"))
    except:
      pass

  def connect(self):
    # try:
    self.s.connect(self.address)
    message = ""
    while True:
      message += self.s.recv(1).decode('utf-8')
      if message[-1] == ";":
        if message[:-1] == 'full':
          print('Session is full.')
          sys.exit()
        else:
          data = json.loads(message[:-1])
          break

    self.size = (data['h'], data['w'])
    self.playerid = data['id']
    self.walls = data['walls']

    self.window = curses.newwin(self.size[0], self.size[1], 0, 0)
    self.window.keypad(1)
    self.window.timeout(100)

    threading.Thread(target = self.update, daemon = True).start()
    # except:
    #   print('Error while connecting')

  def update(self): # Update positions
    message = ""
    while True:
      try:
        message += self.s.recv(1).decode('utf-8')
        if message[-1] == ";":
            self.game = json.loads(message[:-1])
            message = ""
      except:
        message = ""

  def draw(self):
    self.window.erase()
    self.window.border(0) # Draw border

    for bullet in self.game['bullets']: # Bullets
      char = '•' if bullet['r'] else '.'
      self.window.addch(bullet['pos']['y'], bullet['pos']['x'], char)

    toplist = []

    for index in range(0, len(self.game['players'])): # Players
      player = self.game['players'][index]

      if not player == None:
        self.window.addch(player['pos']['y'], player['pos']['x'], player['c'])
        toplist.append((player['s'], index))

    for explosion in self.game['exps']:
      x = explosion['x']
      y = explosion['y']

      areaOfEfect = [
        [x, y],
        [x, y - 1],
        [x + 1, y - 1],
        [x + 1, y],
        [x + 1, y + 1],
        [x, y + 1],
        [x - 1, y + 1],
        [x - 1, y],
        [x - 1, y - 1],
        [x + 2, y],
        [x - 2, y],
        [x, y - 2],
        [x, y + 2]
      ]

      for tile in areaOfEfect:
        if tile[0] >= 0 and tile[0] <= self.size[1] - 1 and tile[1] >= 0 and tile[1] <= self.size[0] - 1:
          if not [tile[0], tile[1]] == [self.size[1] - 1, self.size[0] - 1]:
            self.window.addch(tile[1], tile[0], '░')

    self.window.addstr(0, 2, f' Text MOBA – {self.address[0]}:{self.address[1]} – Your score: {self.game["players"][self.playerid]["s"]} ')

    toplist = sorted(toplist, reverse = True)

    # Draw scores
    self.window.addstr(self.size[0] - 1, 2, ' Top 4 ')
    for index in range(0, len(toplist)):
      score = toplist[index]
      
      if index > 3:
        break

      self.window.addstr(
        self.size[0] - 1,
        10 + (index * 15),
        f' Player {self.game["players"][toplist[index][1]]["c"]}: {toplist[index][0]} '
      )

    for wall in self.walls:
      self.window.addch(wall[1], wall[0], '▓')