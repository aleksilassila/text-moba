import sys, json
from PIL import Image

if len(sys.argv) < 3:
  print('Script takes 2 positional arguments: input image path and output file name.')
  sys.exit()

image = Image.open(sys.argv[1])
width, height = image.size
blackAndWhite = image.convert("1")

values = list(blackAndWhite.getdata())

output = {
  "walls": [],
  "size": [width, height]
}

for row in range(0, height):
  for column in range(0, width):
    if values[row * width + column] == 0:
      output['walls'].append([column, row])

with open(sys.argv[2], 'w') as file:
    json.dump(output, file)