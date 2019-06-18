import random

class Player:
  def __init__(self, clientsocket, data):
    self.clientsocket = clientsocket
    self.playerid = data['id']
    self.walls = data['walls']
    self.mapWidth, self.mapHeight = data['w'], data['h']

    ids = ['#', '@', '&', '+', '%', '$', '£']

    if self.playerid + 1 > len(ids):
      playerChar = 65 + self.playerid - len(ids)
    else:
      playerChar = ids[self.playerid]

    self.state = {
      'pos': {},
      'c': playerChar, # Character
      's': 0, # Score
      'd': 0 # Is dead
    }

    self.spawnPlayer()

  def spawnPlayer(self):
    while True:
      pos = [random.randint(1, self.mapWidth - 2), random.randint(1, self.mapHeight - 2)]

      if not any(pos == wall for wall in self.walls):
        break

    self.state['pos'] = {'x': pos[0], 'y': pos[1]}

  def disconnect(self):
    self.clientsocket.close()