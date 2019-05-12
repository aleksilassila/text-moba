import threading, socket, json, time, random, sys

ip, port = sys.argv[1].split(":")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip, int(port)))
s.listen(16)

clients = [None, None, None, None]

width = 80
height = 24

game = {
  'players': [None, None, None, None],
  'bullets': [],
  'walls': []
}

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
  [72, 4]
]

"""
players = [
{ pos: {'x':5, 'y':5}, 'c':"#", s: 3},
]
"""

def acceptClients():
  while True:
    clientsocket, address = s.accept()
    
    for index in range(0, len(game['players'])):
      if game['players'][index] == None:
        playerid = index
        break
      else:
        playerid = -1

    print(f'Connection from {address}. Assigning to player {playerid}')
    clientsocket.send(bytes(json.dumps({'id': playerid, 'w': width, 'h': height, 'walls': walls}) + ";", 'utf-8'))

    ids = ['#', '@', '&', '+']

    if not playerid == -1:
      game['players'][playerid] = {'pos': {'x': random.randint(1, width - 2), 'y': random.randint(1, height - 2)}, 'c':ids[playerid] }
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
        print(f'Player {playerid}: Error')
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
          if payload == 0 and pos['y'] - 1 > 0 and not any([pos['x'], pos['y'] - 1] == wall for wall in walls): # Up
            pos['y'] -= 1
          if payload == 1 and pos['x'] + 1 < width - 1 and not any([pos['x'] + 1, pos['y']] == wall for wall in walls): # Right
            pos['x'] += 1
          if payload == 2 and pos['y'] + 1 < height - 1 and not any([pos['x'], pos['y'] + 1] == wall for wall in walls): # Down
            pos['y'] += 1
          if payload == 3 and pos['x'] - 1 > 0 and not any([pos['x'] - 1, pos['y']] == wall for wall in walls): # Left
            pos['x'] -= 1

        if action == 's':
          if payload == 0: # Up
            game['bullets'].append({'pos': { 'x': pos['x'], 'y': pos['y'] - 1 }, 'dir': payload})
          if payload == 1: # Right
            game['bullets'].append({'pos': { 'x': pos['x'] + 1, 'y': pos['y'] }, 'dir': payload})
          if payload == 2: # Down
            game['bullets'].append({'pos': { 'x': pos['x'], 'y': pos['y'] + 1 }, 'dir': payload})
          if payload == 3: # Left
            game['bullets'].append({'pos': {'x': pos['x'] - 1, 'y': pos['y'] }, 'dir': payload})
      except:
        pass

threading.Thread(target = acceptClients, daemon = True).start()

while True: # Update clients
  try:
    for bullet in game['bullets']:
      if not bullet == -1:
        if bullet['dir'] == 0:
          bullet['pos']['y'] -= 1
        elif bullet['dir'] == 1:
          bullet['pos']['x'] += 1
        elif bullet['dir'] == 2:
          bullet['pos']['y'] += 1
        elif bullet['dir'] == 3:
          bullet['pos']['x'] -= 1

    for index in range(0, len(game['bullets'])):
      if game['bullets'][index]['pos']['y'] <= 0 or game['bullets'][index]['pos']['x'] >= width - 1 or game['bullets'][index]['pos']['y'] > height - 1 or game['bullets'][index]['pos']['x'] <= 0:
        game['bullets'][index] = -1
      else:
        if any([game['bullets'][index]['pos']['x'], game['bullets'][index]['pos']['y']] == wall for wall in walls):
          game['bullets'][index] = -1

    game['bullets'] = [item for item in game['bullets'] if
      not item == -1] # Remove still bullets

    for index in range(0, len(game['players'])):
      player = game['players'][index]
      for bullet in game['bullets']:
        if not player == None and player['pos']['x'] == bullet['pos']['x'] and player['pos']['y'] == bullet['pos']['y']:
          game['players'][index] = None

    for index in range(0, len(game['players'])):
      if not clients[index] == None:
        clients[index].send(bytes(json.dumps(game) + ";", 'utf-8'))

    
    time.sleep(0.1)
  except KeyboardInterrupt:
    for client in clients:
      if not client == None:
        client.close()
    sys.exit()