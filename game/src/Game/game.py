import socket, json, threading, curses

class Game:
  def __init__(self, host, port):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.address = (host, port)

    self.playerid = 0
    self.game = {}
    self.walls = []

  def move(self, direction):
    try:
      self.s.send(bytes(json.dumps({'a': 'm', 'p': direction}) + ";", "utf-8")) # Action: Move, payload: direction
    except:
      pass

  def shoot(self, direction):
    try:
      self.s.send(bytes(json.dumps({'a': 's', 'p': direction}) + ";", "utf-8")) # Action: shoot, payload: direction
    except:
      pass

  def connect(self):
    # try:
    self.s.connect(self.address)
    message = ""
    while True:
      message += self.s.recv(1).decode('utf-8')
      if message[-1] == ";":
        data = json.loads(message[:-1])
        break

    self.playerid = data['id']
    self.size = (data['h'], data['w'])
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

    if self.game['players'][self.playerid] == None:
      self.s.close()
      self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.connect()
    else:
      for player in self.game['players']: # Players
        if not player == None:
          self.window.addch(player['pos']['y'], player['pos']['x'], player['c'])

      for bullet in self.game['bullets']: # Bullets
        self.window.addch(bullet['pos']['y'], bullet['pos']['x'], '.')

      for wall in self.walls:
        self.window.addch(wall[1], wall[0], '▓')