import random, threading, json, socket
from player import Player

class Game:
  def __init__(self, ip, port, args):
    self.players = []
    self.bullets = []
    self.walls = []
    self.exps = []

    self.winner = [-1, 0] # [playerid, score]
    """ Example
    game = {
      'players': [{pos: {x: 5, y: 5}, c: character, s: score, d: dead}, None, None, None],
      'bullets': [{pos: {x: 5, y: 5}, dir: direction, id: playerid}],
      'walls': []
    }
    """

    self.maxPlayers = args.players
    self.maxBullets = args.bullets
    self.maxRockets = args.rockets
    self.tickrate = args.tickrate
    self.gamemode = args.gamemode

    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.bind((ip, int(port)))
    self.s.listen(16)

    with open(args.map) as data:
      mapData = json.load(data)
      self.walls = mapData['walls']
      self.width, self.height = mapData['size']

    for index in range(0, self.maxPlayers): # Create player spots in game object
      self.players.append(None)

  def acceptClients(self):
    while True:
      clientsocket, address = self.s.accept()
      
      for index in range(0, len(self.players)):
        if self.players[index] == None:
          playerid = index
          break
        else:
          playerid = -1

      if playerid == -1:
        clientsocket.send(bytes("full;", 'utf-8'))
        clientsocket.close()
        print(f'Connection from {address} rejected.')
      else:
        print(f'Connection from {address}. Assigning to player {playerid}')
        initData = {'id': playerid, 'w': self.width, 'h': self.height, 'walls': self.walls, 't': self.tickrate, 'g':self.gamemode}

        clientsocket.send(bytes(json.dumps(initData) + ";", 'utf-8'))
        self.players[playerid] = Player(clientsocket, initData)

        threading.Thread(target = self.listen, args = (playerid, ), daemon = True).start()

  def listen(self, playerid):
    while True:
      player = self.players[playerid]
      """
      recv = {
        do: move,
        payload: dir
      }
      """
      data = ""
      try:
        while True:
          data += player.clientsocket.recv(1024).decode('utf-8')

          if data[-1] == ";":
            break

      except:
        print(f'Player {playerid}: Disconnected')
        player.clientsocket.close()
        self.players[playerid] = None
        break

      try:
        if not player.state['d']:
          data = json.loads(data[:-1])
          action = data['a']
          payload = data['p']

          pos = player.state['pos']
          
          if action == 'm': # Move
            if payload == 0 and pos['y'] - 1 > 0 and not any([pos['x'], pos['y'] - 1] == wall for wall in self.walls): # Up
              pos['y'] -= 1
            if payload == 1 and pos['x'] + 1 < self.width - 1 and not any([pos['x'] + 1, pos['y']] == wall for wall in self.walls): # Right
              pos['x'] += 1
            if payload == 2 and pos['y'] + 1 < self.height - 1 and not any([pos['x'], pos['y'] + 1] == wall for wall in self.walls): # Down
              pos['y'] += 1
            if payload == 3 and pos['x'] - 1 > 0 and not any([pos['x'] - 1, pos['y']] == wall for wall in self.walls): # Left
              pos['x'] -= 1

          if action == 's':
            bulletsCount = [0, 0] # Bullets, rockets
            for bullet in self.bullets:
              if bullet['id'] == playerid:
                if bullet['r']:
                  bulletsCount[1] += 1
                else:
                  bulletsCount[0] += 1

            if (bulletsCount[0] < self.maxBullets and not payload[1]) or (bulletsCount[1] < self.maxRockets and payload[1]):
              self.bullets.append({'pos': { 'x': pos['x'], 'y': pos['y'] }, 'dir': payload[0], 'id': playerid, 'r': payload[1]})

      except:
        pass

  def explode(self, pos, bulletid):
    x = pos['x']
    y = pos['y']

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

    for index in range(0, len(self.players)):
      player = self.players[index]

      if not player == None and any([player.state['pos']['x'], player.state['pos']['y']] == item for item in areaOfEfect):
        player.spawnPlayer()

        if bulletid == index:
          player.state['s'] -= 1
        else:
          self.players[bulletid].stete['s'] += 1

    self.exps.append(pos)

  def updateExplosions(self):
    for index in range(0, len(self.exps)): # Remove explosions
      if random.randint(1, 100) > 90: # 10% change to clear explosion per tick
        self.exps[index] = -1

    self.exps = [item for item in self.exps if not item == -1]

  def updateBullets(self):
    for bullet in self.bullets: # Move bullets
      if bullet['dir'] == 0:
        bullet['pos']['y'] -= 1

      elif bullet['dir'] == 1:
        bullet['pos']['x'] += 1

      elif bullet['dir'] == 2:
        bullet['pos']['y'] += 1

      elif bullet['dir'] == 3:
        bullet['pos']['x'] -= 1

    for index in range(0, len(self.bullets)): # Check for collisions
      bullet = self.bullets[index]

      if (bullet['pos']['y'] <= 0 or bullet['pos']['x'] <= 0
        or bullet['pos']['y'] >= self.height - 1 or bullet['pos']['x'] >= self.width - 1
        or any([bullet['pos']['x'], bullet['pos']['y']] == wall for wall in self.walls)):
          if bullet['r']:
            self.explode(bullet['pos'], bullet['id'])
          bullet['pos'] = -1

    self.bullets = [item for item in self.bullets if not item['pos'] == -1] # Remove bullets

  def updatePlayers(self):
    winner = [-1, 0] # potential winner

    for index in range(0, len(self.players)): # Check if player dies
      player = self.players[index]

      if player:
        for bullet in self.bullets:
          if player.state['pos'] == bullet['pos'] and not bullet['id'] == index:
            try:
              self.players[bullet['id']].state['s'] += 1 # Give a point

              if self.gamemode == 'ffa':
                player.spawnPlayer()

              elif self.gamemode == 'br':
                self.players[index].state['d'] = 1 # make player dead
                winner[0] = bullet['id']
                winner[1] = self.players[bullet['id']].state['s']
            except:
              pass

    if self.gamemode == 'br':
      playersAlive = len([player for player in self.players if player and not player.state['d']])
      playersTotal = len([player for player in self.players if player])
      
      if not playersTotal == 1 and playersAlive == 1: # If game has ended
        self.bullets = []

        for index in range(0, len(self.players)):
          if self.players[index]:
            self.players[index].spawnPlayer()
            self.players[index].state['s'] = self.players[index].state['d'] = 0

        self.winner = winner

  def updateClients(self):
    players = []

    for index in range(0, len(self.players)):
      player = self.players[index]

      players.append(player.state if player else None)

    for player in self.players:
      if player:
        player.clientsocket.send(bytes(json.dumps({'p': players, 'b': self.bullets, 'e': self.exps, 'w': self.winner}) + ";", 'utf-8'))