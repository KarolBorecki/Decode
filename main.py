import random

from kivy.app import App
from kivy.clock import Clock
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
        self.load_source()

    def on_press(self):
        self.parent.parent.parent.block_pressed(self)

    def look_for_line(self, destroy=True, look_for_black=True):
        blocks_to_destroy = self.check_horizontal() + self.check_vertical()
        if len(blocks_to_destroy) > 0:
            if destroy:
                for block in blocks_to_destroy:
                    if look_for_black:
                        block.look_for_black()
                    block.destroy()
            return True
        return False

    def check_vertical(self):
        parent = self.parent.parent.parent
        y = self.index_y
        x = self.index_x

        blocks_to_destroy = []
        is_done = False
        if not y >= parent.board_size - 1 and not y <= 0:
            if self.c == parent.blocks[y - 1][x].c and self.c == parent.blocks[y + 1][x].c:
                if y > 1:
                    if self.c == parent.blocks[y - 2][x].c:
                        blocks_to_destroy.append(parent.blocks[y - 2][x])
                        parent.add_bomb()
                blocks_to_destroy.append(parent.blocks[y - 1][x])
                blocks_to_destroy.append(self)
                blocks_to_destroy.append(parent.blocks[y + 1][x])
                if not y >= parent.board_size - 2:
                    if self.c == parent.blocks[y + 2][x].c:
                        blocks_to_destroy.append(parent.blocks[y + 2][x])
                        parent.add_bomb()
                is_done = True
        if y > 1 and not is_done:
            if self.c == parent.blocks[y - 1][x].c and self.c == parent.blocks[y - 2][x].c:
                blocks_to_destroy.append(parent.blocks[y - 2][x])
                blocks_to_destroy.append(parent.blocks[y - 1][x])
                blocks_to_destroy.append(self)
                is_done = True
        if not y >= parent.board_size - 2 and not is_done:
            if self.c == parent.blocks[y + 1][x].c and self.c == parent.blocks[y + 2][x].c:
                blocks_to_destroy.append(self)
                blocks_to_destroy.append(parent.blocks[y + 1][x])
                blocks_to_destroy.append(parent.blocks[y + 2][x])
        return blocks_to_destroy

    def check_horizontal(self):
        parent = self.parent.parent.parent
        y = self.index_y
        x = self.index_x

        blocks_to_destroy = []
        is_done = False
        if not x >= parent.board_size - 1 and not x <= 0:
            if self.c == parent.blocks[y][x - 1].c and self.c == parent.blocks[y][x + 1].c:
                if x > 1:
                    if self.c == parent.blocks[y][x - 2].c:
                        blocks_to_destroy.append(parent.blocks[y][x - 2])
                        parent.add_bomb()
                if not x >= parent.board_size - 2:
                    if self.c == parent.blocks[y][x + 2].c:
                        blocks_to_destroy.append(parent.blocks[y][x + 2])
                        parent.add_bomb()

                blocks_to_destroy.append(parent.blocks[y][x - 1])
                blocks_to_destroy.append(self)
                blocks_to_destroy.append(parent.blocks[y][x + 1])
                is_done = True
        if not x <= 0 and not is_done:
            if self.c == parent.blocks[y][x - 1].c and self.c == parent.blocks[y][x - 2].c:
                blocks_to_destroy.append(parent.blocks[y][x - 2])
                blocks_to_destroy.append(parent.blocks[y][x - 1])
                blocks_to_destroy.append(self)
                is_done = True
        if not x >= parent.board_size - 2 and not is_done:
            if self.c == parent.blocks[y][x + 1].c and self.c == parent.blocks[y][x + 2].c:
                blocks_to_destroy.append(parent.blocks[y][x + 1])
                blocks_to_destroy.append(parent.blocks[y][x + 2])
                blocks_to_destroy.append(self)
        return blocks_to_destroy

    def look_for_black(self):
        parent = self.parent.parent.parent
        if not self.index_y >= parent.board_size - 1:
            if parent.blocks[self.index_y + 1][self.index_x].c == "black":
                parent.game_over()
        if not self.index_y <= 0:
            if parent.blocks[self.index_y - 1][self.index_x].c == "black":
                parent.game_over()
        if not self.index_x >= parent.board_size - 1:
            if parent.blocks[self.index_y][self.index_x + 1].c == "black":
                parent.game_over()
        if not self.index_x <= 0:
            if parent.blocks[self.index_y][self.index_x - 1].c == "black":
                parent.game_over()

    def fall(self, dt):
        parent = self.parent.parent.parent
        if self.index_y > 0:
            if self.c == "white":
                block_above = parent.blocks[self.index_y - 1][self.index_x]
                self.swap_colors(block_above, False)
                Clock.schedule_once(block_above.fall, 0.0)
        self.check_is_destroyed()
        self.look_for_line(look_for_black=False)

    def destroy(self):
        Clock.schedule_once(self.set_to_destroyed, 2)

    def set_to_destroyed(self, dt):
        self.set_color("white")
        Clock.schedule_once(self.fall, 0.05)
        self.parent.parent.parent.add_score(10)

    def move(self, direction):
        swap_block = self.get_block_by_direction(direction)
        self.swap_colors(swap_block)
        self.parent.parent.parent.last_touched_block = None

    def swap_colors(self, swap_block, look=True):
        swap_block_color = swap_block.c
        swap_block.set_color(self.c)
        self.set_color(swap_block_color)
        if look:
            swap_block_looking = swap_block.look_for_line()
            self_looking = self.look_for_line()
            if not swap_block_looking and not self_looking:
                self.swap_colors(swap_block, False)

    def check_is_destroyed(self):
        if self.c == "white":
            self.randomize_color()

    def check_color(self):
        parent = self.parent.parent.parent
        x1 = parent.blocks[self.index_y][self.index_x - 1].c
        x2 = parent.blocks[self.index_y][self.index_x - 2].c
        y1 = parent.blocks[self.index_y - 1][self.index_x].c
        y2 = parent.blocks[self.index_y - 2][self.index_x].c

        if self.c == x1 and self.c == x2:
            self.randomize_color()
        if self.c == y1 and self.c == y2:
            self.randomize_color()

    def randomize_color(self):
        parent = self.parent.parent.parent
        if parent.actual_chance_for_black < 30:
            available_colors = [x for x in parent.colors if x != self.c]
            c = random.choice(available_colors)
            self.set_color(c)
        else:
            self.set_color("black")
            parent.actual_chance_for_black = 0
        parent.actual_chance_for_black += 1

    def set_color(self, c):
        self.c = c
        self.load_source()

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

    def print_index(self):
        print("y: " + str(self.index_y) + " x: " + str(self.index_x))

    def load_source(self):
        self.source = "img/blocks/" + str(self.c) + "_block.png"


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
    colors = ["red", "blue", "green", "yellow", "purple"]
    blocks = []
    touch_accuracy = 30
    board_size = 8

    score = 0
    bombs_count = 0

    last_x = 0
    last_y = 0
    actually_x = 0
    actually_y = 0
    last_touched_block = None
    actual_chance_for_black = 0

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)

        for y in range(self.board_size):
            self.blocks.append([])
            for x in range(self.board_size):
                self.blocks[y].append(Block(random.choice(self.colors), x, y))

        for x in range(self.board_size):
            for block in self.blocks[x]:
                self.board.add_widget(block)

        for y in self.blocks:
            for x in y:
                x.check_color()

    @staticmethod
    def bomb_drag():
        print("BOMB DRAGGED")

    def add_score(self, amount):
        self.score += amount
        self.score_board.text = str(self.score)

    def add_bomb(self):
        self.bombs_count += 1
        self.bomb_label.text = str(self.bombs_count)

    def block_pressed(self, block):
        self.last_touched_block = block

    def game_over(self):
        print("GAME OVER")
        self.add_widget(Image(source="img/shadow.png", pos_hint={'center_x': .5, 'center_y': .5}))
        self.add_widget(Image(source="img/game_over.png", pos_hint={'center_x': .5, 'center_y': .5}))

    def on_touch_down(self, touch):
        self.last_x = touch.pos[0]
        self.last_y = touch.pos[1]

        super(PlayScreen, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.last_touched_block is not None:
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


class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(PlayScreen(name='play'))
sm.add_widget(SettingsScreen(name='settings'))
sm.add_widget(InfoScreen(name='info'))


class Decode(App):
    def build(self):
        return sm


if __name__ == '__main__':
    Decode().run()
