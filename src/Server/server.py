from time import sleep
from threading import Thread

from Server.game import Game

class Server:
  def __init__(self, ip, port, config):
    self.game = Game(ip, port, config)

    Thread(target = self.game.acceptClients, daemon = True).start()

    while True:
      try:
        self.game.updateExplosions()
        self.game.updateBullets()
        self.game.updatePlayers()

        self.game.updateClients()

        sleep(1 / self.game.tickrate)

      except KeyboardInterrupt:
        for player in self.game.players:
          if not player == None:
            player.disconnect()

        break
