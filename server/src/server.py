import threading, socket, json, time, random, sys, argparse

width = 80
height = 24

ids = ['#', '@', '&', '+', '%', '$', '£']

clients = []

game = {
  'players': [],
  'bullets': [],
  'walls': []
}

""" Example
game = {
  'players': [{pos: {x: 5, y: 5}, c: character, s: score, d: dead}, None, None, None],
  'bullets': [{pos: {x: 5, y: 5}, dir: direction, id: playerid}],
  'walls': []
}
"""

parser = argparse.ArgumentParser(description = 'Server for Text-MOBA')
parser.add_argument('address', help = 'Server bind address: [ip]:[port]')
parser.add_argument('-p', '--players', type = int, help = 'Max players')
parser.add_argument('-m', '--map', help = 'Json file containing map')
parser.add_argument('-b', '--bullets', type = int, help = 'Set max bullets in air per player')
args = parser.parse_args()

ip, port = args.address.split(":")
mapFile = '../map.json' if not args.map else args.map
maxPlayers = 4 if not args.players else args.players
maxBullets = 15 if not args.bullets else args.bullets

with open(mapFile) as f:
  mapData = json.load(f)
  game['walls'] = mapData['walls']
  width, height = mapData['size']

for index in range(0,maxPlayers): # Create player spots in game and client objects
  game['players'].append(None)
  clients.append(None)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip, int(port)))
s.listen(16)

def acceptClients():
  while True:
    clientsocket, address = s.accept()
    
    for index in range(0, len(game['players'])):
      if game['players'][index] == None:
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
      clientsocket.send(bytes(json.dumps({'id': playerid, 'w': width, 'h': height, 'walls': game['walls']}) + ";", 'utf-8'))

      if playerid + 1 > len(ids):
        playerChar = 65 + playerid - len(ids)
      else:
        playerChar = ids[playerid]
      if not playerid == -1:
        game['players'][playerid] = {
          'pos': {'x': random.randint(1, width - 2), 'y': random.randint(1, height - 2)},
          'c': playerChar, # Character
          's': 0 # Score
          #'d': 0 # Is dead
        }
        clients[playerid] = clientsocket

        threading.Thread(target = listenToPlayer, args = (clientsocket, playerid), daemon = True).start()

def listenToPlayer(clientsocket, playerid):
    while True:
      """
      recv = {
      do: move,
      payload: dir
      }
      """
      data = ""
      try:
        while True:
          data += clientsocket.recv(1024).decode('utf-8')

          if data[-1] == ";":
            break
      except:
        print(f'Player {playerid}: Disconnected')
        game['players'][playerid] = None
        clients[playerid] = None
        clientsocket.close()
        break

      try:
        data = json.loads(data[:-1])
        action = data['a']
        payload = data['p']

        pos = game['players'][playerid]['pos']

        if action == 'm': # Move
          if payload == 0 and pos['y'] - 1 > 0 and not any([pos['x'], pos['y'] - 1] == wall for wall in game['walls']): # Up
            pos['y'] -= 1
          if payload == 1 and pos['x'] + 1 < width - 1 and not any([pos['x'] + 1, pos['y']] == wall for wall in game['walls']): # Right
            pos['x'] += 1
          if payload == 2 and pos['y'] + 1 < height - 1 and not any([pos['x'], pos['y'] + 1] == wall for wall in game['walls']): # Down
            pos['y'] += 1
          if payload == 3 and pos['x'] - 1 > 0 and not any([pos['x'] - 1, pos['y']] == wall for wall in game['walls']): # Left
            pos['x'] -= 1

        if action == 's':
          bulletsCount = 0
          for bullet in game['bullets']:
            if bullet['id'] == playerid:
              bulletsCount += 1

          if bulletsCount < maxBullets:
            game['bullets'].append({'pos': { 'x': pos['x'], 'y': pos['y'] }, 'dir': payload, 'id': playerid})

      except:
        pass

threading.Thread(target = acceptClients, daemon = True).start()

while True: # Update clients
  try:
    for bullet in game['bullets']: # Move bullets
      if bullet['dir'] == 0:
        bullet['pos']['y'] -= 1
      elif bullet['dir'] == 1:
        bullet['pos']['x'] += 1
      elif bullet['dir'] == 2:
        bullet['pos']['y'] += 1
      elif bullet['dir'] == 3:
        bullet['pos']['x'] -= 1

    for index in range(0, len(game['bullets'])): # Mark bullets to be removed
      if game['bullets'][index]['pos']['y'] <= 0 or game['bullets'][index]['pos']['x'] >= width - 1 or game['bullets'][index]['pos']['y'] >= height - 1 or game['bullets'][index]['pos']['x'] <= 0:
        game['bullets'][index] = -1
      else:
        if any([game['bullets'][index]['pos']['x'], game['bullets'][index]['pos']['y']] == wall for wall in game['walls']):
          game['bullets'][index] = -1

    game['bullets'] = [item for item in game['bullets'] if
      not item == -1] # Remove bullets

    for index in range(0, len(game['players'])): # Check if player dies
      player = game['players'][index]
      if not player == None:
        for bullet in game['bullets']:
          if player['pos'] == bullet['pos'] and not bullet['id'] == index:
            bulletid = bullet['id']

            game['players'][index]['pos'] = {
              'x': random.randint(1, width - 2),
              'y': random.randint(1, height - 2)
            } # Respawn player

            game['players'][bulletid]['s'] += 1 # Give a point

    for index in range(0, len(game['players'])): # Send game state to players
      if not clients[index] == None:
        clients[index].send(bytes(json.dumps(game) + ";", 'utf-8'))

    
    time.sleep(0.1)
  except KeyboardInterrupt:
    for client in clients:
      if not client == None:
        client.close()
    sys.exit()