import curses
from time import sleep

class Menu:
  def __init__(self, menu, height, width, y, x, message = None, help = None):
    self.menu = menu
    self.message = message
    self.help = help

    self.height = height
    self.width = width

    self.w = curses.newwin(height, width, y, x)
    self.w.timeout(100)
    self.w.keypad(1)
    self.w.border(0)

    self.selection = 0

  def prompt(self):
    if self.message:
      self.w.addstr(0, 1, self.message)
    
    self.w.timeout(-1)
    curses.echo()
    
    prompt = self.w.getstr(1, 2, 22)

    self.w.timeout(100)
    curses.noecho()

    return prompt.decode("utf-8").split(":")

  def createMenu(self):
    # try:
    while True:
      key = self.w.getch()

      if key == curses.KEY_UP:
        index = self.selection
        
        while True:  
          if index - 1 >= 0 and 'skip' in self.menu[index - 1]:
            index -= 1
          elif index - 1 >= 0:
            index -= 1
            break
          else:
            break

        self.selection = index
      
      elif key == curses.KEY_DOWN:
        index = self.selection
        
        while True:  
          if index + 1 <= len(self.menu) - 1 and 'skip' in self.menu[index + 1]:
            index += 1
          elif index + 1 <= len(self.menu) - 1:
            index += 1
            break
          else:
            break

        self.selection = index
      
      elif key == curses.KEY_RIGHT:
        if 'value' in self.menu[self.selection]:
          self.menu[self.selection]['value'] += 1
        
        elif 'boolean' in self.menu[self.selection]:
          self.menu[self.selection]['boolean'] = not self.menu[self.selection]['boolean']

      elif key == curses.KEY_LEFT:
        if 'value' in self.menu[self.selection]:
          self.menu[self.selection]['value'] = self.menu[self.selection]['value'] - 1 if self.menu[self.selection]['value'] >= 1 else 0
        
        elif 'boolean' in self.menu[self.selection]:
          self.menu[self.selection]['boolean'] = not self.menu[self.selection]['boolean']

      elif key == 10:
        if 'selectable' in self.menu[self.selection]:
          self.select()
          break

      self.draw()
    # except KeyboardInterrupt:
    #   self.selection = -1

  def draw(self):
    self.w.erase()
    self.w.border(0)
    for index in range(0, len(self.menu)):
      item = self.menu[index]

      checked = '*' if index == self.selection else ' '
      value = f'{item["value"]}      ' if 'value' in item else ''
      boolean = f'{item["boolean"]} ' if 'boolean' in item else ''
      
      self.w.addstr(1 + index, 2, f'{checked} {self.menu[index]["Label"]} {value}{boolean}')

    if self.help: self.w.addstr(self.height - 1, 2, self.help)

  def select(self):
    label = self.menu[self.selection]['Label']
    index = self.selection

    for i in range(2):
      self.menu[index]['Label'] = ''
      self.draw()
      self.w.refresh()
      sleep(0.15)

      self.menu[index]['Label'] = label
      self.draw()
      self.w.refresh()
      sleep(0.15)