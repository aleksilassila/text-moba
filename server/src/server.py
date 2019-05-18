import threading, socket, json, time, random, sys, argparse
from game import Game

parser = argparse.ArgumentParser(description = 'Server for Text-MOBA')
parser.add_argument('address', help = 'Server bind address: [ip]:[port]')
parser.add_argument('-p', '--players', type = int, help = 'Max players, default 4')
parser.add_argument('-m', '--map', help = 'Json file containing map')
parser.add_argument('-b', '--bullets', type = int, help = 'Set max bullets in air per player, 0 to disable bullets, default 15')
parser.add_argument('-r', '--rockets', type = int, help = 'Set max rockets in air per player, 0 to disable rockets, default 1')
parser.add_argument('--tickrate', type = int, help = 'How many times game state will be updated per second, default 24')
args = parser.parse_args()

ip, port = args.address.split(":")

game = Game(ip, port)

mapFile = '../map.json' if not args.map else args.map
game.maxPlayers = 4 if not args.players else args.players
game.maxBullets = 15 if args.bullets == None else args.bullets
game.maxRockets = 1 if args.rockets == None else args.rockets
game.tickrate = 20 if args.tickrate == None else args.tickrate

with open(mapFile) as f:
  mapData = json.load(f)
  game.walls = mapData['walls']
  game.width, game.height = mapData['size']

for index in range(0, game.maxPlayers): # Create player spots in game object
  game.players.append(None)

threading.Thread(target = game.acceptClients, daemon = True).start()

while True:
  try:
    game.updateExplosions()
    game.updateBullets()
    game.killPlayers()

    game.updateClients()

    time.sleep(1 / game.tickrate)

  except KeyboardInterrupt:
    for player in game.players:
      if not player == None:
        player.disconnect()

    sys.exit()