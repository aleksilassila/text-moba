import threading, socket, json, time, random, sys, argparse
from game import Game

parser = argparse.ArgumentParser(description = 'Server for Text-MOBA')
parser.add_argument('address', help = 'Server bind address: [ip]:[port]')
parser.add_argument('-g', '--gamemode', default = 'ffa', choices = ['ffa', 'br'], help = 'Set gamemode. ')
parser.add_argument('-p', '--players', default = 4, type = int, help = 'Max players')
parser.add_argument('-m', '--map', default = '../map.json', help = 'Json file containing map')
parser.add_argument('-b', '--bullets', default = 15, type = int, help = 'Set max bullets in air per player, 0 to disable bullets')
parser.add_argument('-r', '--rockets', default = 1, type = int, help = 'Set max rockets in air per player, 0 to disable rockets')
parser.add_argument('--tickrate', default = 20, type = int, help = 'How many times game state will be updated per second')
args = parser.parse_args()

ip, port = args.address.split(":")

game = Game(ip, port, args)

threading.Thread(target = game.acceptClients, daemon = True).start()

while True:
  try:
    game.updateExplosions()
    game.updateBullets()
    game.updatePlayers()

    game.updateClients()

    time.sleep(1 / game.tickrate)

  except KeyboardInterrupt:
    for player in game.players:
      if not player == None:
        player.disconnect()

    sys.exit()