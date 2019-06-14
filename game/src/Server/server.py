import threading, sys, time
from Server.game import Game

class Server:
  def __init__(self, ip, port, config):
    self.game = Game(ip, port, config)

    threading.Thread(target = self.game.acceptClients, daemon = True).start()

    while True:
      try:
        self.game.updateExplosions()
        self.game.updateBullets()
        self.game.updatePlayers()

        self.game.updateClients()

        time.sleep(1 / self.game.tickrate)

      except KeyboardInterrupt:
        for player in self.game.players:
          if not player == None:
            player.disconnect()

        sys.exit()
