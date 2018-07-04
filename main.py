import random

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

Window.size = (400, 700)
Builder.load_file('graphic.kv')


class Block(ButtonBehavior, Image):
    def __init__(self, c, x, y, **kwargs):
        super(Block, self).__init__(**kwargs)
        self.index_x = x
        self.index_y = y
        self.c = c
        self.source = self.load_source()

    def on_press(self):
        self.parent.parent.parent.block_pressed(self)

    def move(self, direction):
        swap_block = self.get_block_by_direction(direction)
        self.swap_colors(swap_block)

    def get_block_by_direction(self, direction):
        parent = self.parent.parent.parent
        swap_block_y = self.index_y
        swap_block_x = self.index_x

        if direction == "up" and self.index_y > 0:
            swap_block_y -= 1
        elif direction == "down" and self.index_y < parent.board_size - 1:
            swap_block_y += 1
        elif direction == "left" and self.index_x > 0:
            swap_block_x -= 1
        elif direction == "right" and self.index_x < parent.board_size - 1:
            swap_block_x += 1

        return parent.blocks[swap_block_y][swap_block_x]

    def swap_colors(self, swap_block):
        swap_block_color = swap_block.c
        swap_block.set_color(self.c)
        self.set_color(swap_block_color)

    def set_color(self, c):
        self.c = c
        self.source = self.load_source()

    def load_source(self):
        return "img/blocks/" + str(self.c) + "_block.png"


class SquareButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(SquareButton, self).__init__(**kwargs)


class MenuScreen(Screen):
    high_score = 23453

    light_color = (.8, .8, .8, 1)
    dark_color = (.1, .1, .1, 1)

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.color = True

        self.set_color(self.color)

    def change_theme(self):
        self.color = not self.color
        self.set_color(self.color)

    def set_color(self, color):
        if color:
            Window.clearcolor = self.light_color
        else:
            Window.clearcolor = self.dark_color


class PlayScreen(Screen):
    colors = ["red", "blue", "green", "yellow"]
    blocks = []
    touch_accuracy = 30
    board_size = 8

    bombs_count = 4

    last_x = 0
    last_y = 0
    actually_x = 0
    actually_y = 0
    last_touched_block = None

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        for y in range(self.board_size):
            self.blocks.append([])
            for x in range(self.board_size):
                self.blocks[y].append(Block(random.choice(self.colors), x, y))

        for x in range(self.board_size):
            for block in self.blocks[x]:
                self.board.add_widget(block)

    @staticmethod
    def bomb_drag():
        print("BOMB DRAGGED")

    def block_pressed(self, block):
        self.last_touched_block = block

    def on_touch_down(self, touch):
        self.last_x = touch.pos[0]
        self.last_y = touch.pos[1]

        super(PlayScreen, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        self.actually_x = touch.pos[0]
        self.actually_y = touch.pos[1]
        dif_x = self.actually_x - self.last_x
        dif_y = self.actually_y - self.last_y

        direction = ""
        if dif_y > self.touch_accuracy:
            direction = "up"
        elif dif_y < -self.touch_accuracy:
            direction = "down"
        elif dif_x > self.touch_accuracy:
            direction = "right"
        elif dif_x < -self.touch_accuracy:
            direction = "left"
        else:
            return

        self.last_touched_block.move(direction)
        super(PlayScreen, self).on_touch_up(touch)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(PlayScreen(name='play'))
sm.add_widget(SettingsScreen(name='settings'))


class TestApp(App):

    def build(self):
        return sm


if __name__ == '__main__':
    TestApp().run()
