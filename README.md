# Text MOBA

A text-based game created with python curses library. Supports multiplayer and custom map importing form images and json files. Note that curses library does not have Windows version. To play on Windows you need virtual machine or linux subsystem.

## To get started:

Start the server: `python3.7 server/src/server.py [your ip]:[port]`

Connect a client: `python3.7 game/src/main.py [server ip]:[port]`

Import map from image: `python3.7 server/image_to_map.py [input.png] [output.json]`

* Note that you'll need Pillow library if you want to import your own map from image.

## Screenshots

![](/screenshots/bigger_maps.png?raw=true "Play with as many friends as you like")
![](/screenshots/game.png?raw=true)