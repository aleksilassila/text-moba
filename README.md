# Text MOBA

A text-based game created with python curses library. Supports custom map importing and multiplayer up to 4 players. Note that curses library does not have Windows version. To play on Windows you need virtual machine or linux subsystem.

## To get started:

Start the server: `python3.7 server/src/main.py [your local ip]:[port] [map file path]`

Connect a client: `python3.7 game/src/main.py [your local ip]:[port]`

## Screenshots

![](/screenshots/game.png?raw=true)
![](/screenshots/multiplayer.png?raw=true "Multiplayer up to 4 players")

## Upcoming features

* Host will be able to issue commands and events
* Diffrent guns
* Spectator mode
* Different game modes
