import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

s1, s2, s3, s4 = (400, 700), (200, 350), (100, 170), (600, 900)

Window.size = s1
Builder.load_file('graphic.kv')


class NullBlock(ButtonBehavior, Image):
    index_x, index_y = 0, 0
    c = ""

    def __init__(self, **kwargs):
        super(NullBlock, self).__init__(**kwargs)

    def destroy(self):
        return

    def look_for_black(self):
        return


class Block(NullBlock):
    block_up, block_down, block_right, block_left, block_up2, block_down2, block_right2, block_left2 \
        = NullBlock(), NullBlock(), NullBlock(), NullBlock(), NullBlock(), NullBlock(), NullBlock(), NullBlock()

    def __init__(self, c, x, y, **kwargs):
        super(Block, self).__init__(**kwargs)
        self.index_x = x
        self.index_y = y

        self.set_color(c)

    def on_press(self):
        parent = self.parent.parent.parent
        parent.block_pressed(self)
        if self.parent.parent.parent.is_bomb_drag:
            self.blow()

    def blow(self):
        parent = self.parent.parent.parent
        if 0 < self.index_y < parent.board_size - 1 and 0 < self.index_x < parent.board_size - 1:
            parent.add_bomb(-1)
            self.destroy_blocks_nearby()
            parent.bomb_unactive()

    def destroy_blocks_nearby(self):
        self.block_up.block_left.destroy()
        self.block_up.destroy()
        self.block_up.block_right.destroy()
        self.block_left.destroy()
        self.destroy()
        self.block_right.destroy()
        self.block_down.block_left.destroy()
        self.block_down.destroy()
        self.block_down.block_right.destroy()

    def check_line(self, side_a1, side_a2, side_b1, side_b2):
        parent = self.parent.parent.parent

        blocks_to_destroy = []

        if self.c == side_a1.c and self.c == side_b1.c:
            if side_a2 is not None and self.c == side_a2.c:
                blocks_to_destroy.append(side_a2)
                parent.add_bomb()

            blocks_to_destroy.append(side_a1)
            blocks_to_destroy.append(self)
            blocks_to_destroy.append(side_b1)

            if self.c == side_b2.c:
                blocks_to_destroy.append(side_b2)
                parent.add_bomb()

        if self.c == side_a1.c and self.c == side_a2.c:
            blocks_to_destroy.append(side_a2)
            blocks_to_destroy.append(side_a1)
            blocks_to_destroy.append(self)

        if self.c == side_b1.c and self.c == side_b2.c:
            blocks_to_destroy.append(self)
            blocks_to_destroy.append(side_b1)
            blocks_to_destroy.append(side_b2)

        return blocks_to_destroy

    def look_for_line(self, destroy=True, look_for_black=True):
        horizontal_blocks = self.check_line(self.block_left, self.block_left2, self.block_right, self.block_right2)
        vertical_blocks = self.check_line(self.block_up, self.block_up2, self.block_down, self.block_down2)
        blocks_to_destroy = horizontal_blocks + vertical_blocks

        if len(blocks_to_destroy) > 0:
            if destroy:
                for block in blocks_to_destroy:
                    if look_for_black:
                        block.look_for_black()
                    block.destroy()
            return True
        return False

    def look_for_group(self):
        founded_group = []
        blocks = [self]

        if len(self.get_vertical_same_color()) > 0:
            blocks += self.get_vertical_same_color()
            turn = False
        else:
            blocks += self.get_horizontal_same_color()
            turn = True

        while len(blocks) > 0:
            founded_in_row = []
            for block in blocks:
                if block not in founded_group:
                    if turn:
                        founded_in_row += block.get_vertical_same_color()
                    else:
                        founded_in_row += block.get_horizontal_same_color()

            founded_group += blocks
            blocks = founded_in_row
            turn = not turn

        return founded_group

    def click_destroy(self):
        to_destroy = self.look_for_group()
        if len(to_destroy) > 0:
            to_destroy.append(self)

        if len(to_destroy) > 2:
            for block in to_destroy:
                block.look_for_black()
                block.destroy()

    def get_horizontal_same_color(self):
        return self.check_left() + self.check_right()

    def get_vertical_same_color(self):
        return self.check_up() + self.check_down()

    def check_up(self):
        if self.block_up.c == self.c:
            return [self.block_up] + self.block_up.check_up()
        return []

    def check_down(self):
        if self.block_down.c == self.c:
            return [self.block_down] + self.block_down.check_down()
        return []

    def check_left(self):
        if self.block_left.c == self.c:
            return [self.block_left] + self.block_left.check_left()
        return []

    def check_right(self):
        if self.block_right.c == self.c:
            return [self.block_right] + self.block_right.check_right()
        return []

    def look_for_black(self):
        if self.block_left.c == "black" or self.block_right.c == "black" or self.block_up.c == "black" or self.block_down.c == "black":
            self.parent.parent.parent.game_over()

    def fall(self, dt):
        if self.index_y > 0:
            if self.c == "white":
                self.swap_colors(self.block_up, False)
                Clock.schedule_once(self.block_up.fall, 0.0)
        self.check_is_destroyed()

    def destroy(self):
        Clock.schedule_once(self.set_to_destroyed, 0.2)

    def set_to_destroyed(self, dt):
        self.set_color("white")
        Clock.schedule_once(self.fall, 0.2)
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
            self.check_line_after_swap(swap_block)

    def check_line_after_swap(self, swap_block):
        swap_block_look_result = swap_block.look_for_line()
        self_look_result = self.look_for_line()
        if not swap_block_look_result and not self_look_result:
            self.swap_colors(swap_block, False)

    def check_is_destroyed(self):
        if self.c == "white":
            self.randomize_color()

    def randomize_color(self):
        parent = self.parent.parent.parent
        if parent.actual_chance_for_black < 20:
            available_colors = [x for x in parent.colors if x != self.c]
            c = random.choice(available_colors)
            parent.actual_chance_for_black += 1
            self.set_color(c)
        else:
            self.set_color("black")
            parent.actual_chance_for_black = 0

    def check_block_nearby(self):
        parent = self.parent.parent.parent
        x = self.index_x
        y = self.index_y
        if x > 0:
            self.block_left = parent.blocks[y][x - 1]
            if x > 1:
                self.block_left2 = parent.blocks[y][x - 2]
        if x < parent.board_size - 1:
            self.block_right = parent.blocks[y][x + 1]
            if x < parent.board_size - 2:
                self.block_right2 = parent.blocks[y][x + 2]
        if y > 0:
            self.block_up = parent.blocks[y - 1][x]
            if y > 1:
                self.block_up2 = parent.blocks[y - 2][x]
        if y < parent.board_size - 1:
            self.block_down = parent.blocks[y + 1][x]
            if y < parent.board_size - 2:
                self.block_down2 = parent.blocks[y + 2][x]

    def set_color(self, c):
        self.c = c
        self.load_source()

    def get_block_by_direction(self, direction):
        parent = self.parent.parent.parent

        if direction == "up" and self.index_y > 0:
            return self.block_up
        elif direction == "down" and self.index_y < parent.board_size - 1:
            return self.block_down
        elif direction == "left" and self.index_x > 0:
            return self.block_left
        elif direction == "right" and self.index_x < parent.board_size - 1:
            return self.block_right

    def print_index(self):
        print("y: " + str(self.index_y) + " x: " + str(self.index_x) + " color: " + self.c)

    def load_source(self):
        self.source = "img/blocks/" + str(self.c) + "_block.png"


class SquareButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(SquareButton, self).__init__(**kwargs)


class GameOverScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(GameOverScreen, self).__init__(**kwargs)


class MenuScreen(Screen):
    high_score = 0

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

    def set_score(self, score):
        self.high_score = score
        self.high_score_label.text = str(score)


class PlayScreen(Screen):
    all_colors = ["red", "blue", "green", "yellow", "orange", "purple", "turquoise", "pink"]
    colors = []
    blocks = []
    touch_accuracy = 30
    board_size = 8
    color_count = 5

    score = 0
    bombs_count = 0

    last_x = 0
    last_y = 0
    actually_x = 0
    actually_y = 0
    last_touched_block = None
    actual_chance_for_black = 0
    game_active = True
    is_bomb_drag = False

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        self.lose_info = GameOverScreen()
        self.start_game()

    def bomb_drag(self):
        if not self.is_bomb_drag and self.bombs_count > 0:
            self.bomb_active()
        else:
            self.bomb_unactive()

    def bomb_active(self):
        self.is_bomb_drag = True
        self.bomb.size_hint_x = .25

    def bomb_unactive(self):
        self.is_bomb_drag = False
        self.bomb.size_hint_x = .22

    def add_score(self, amount):
        self.score += amount
        self.score_board.text = str(self.score)

    def add_bomb(self, amount=1):
        self.bombs_count += amount
        self.bomb_label.text = str(self.bombs_count)

    def block_pressed(self, block):
        self.last_touched_block = block

    def start_game(self):
        self.colors = self.all_colors[0:self.color_count]
        self.blocks = []
        self.board.clear_widgets()
        self.board.cols = self.board_size

        self.random_choice_blocks_colors()
        self.add_blocks_to_board()
        self.check_blocks_nearby()

    def random_choice_blocks_colors(self):
        for y in range(self.board_size):
            self.blocks.append([])
            for x in range(self.board_size):
                self.blocks[y].append(Block(random.choice(self.colors), x, y))

    def add_blocks_to_board(self):
        for x in range(self.board_size):
            for block in self.blocks[x]:
                self.board.add_widget(block)

    def check_blocks_nearby(self):
        for y in self.blocks:
            for x in y:
                x.check_block_nearby()

    def game_over(self):
        print (self.children)
        self.add_widget(self.lose_info)
        menu = self.manager.get_screen('menu')
        self.game_active = False

        if self.score > menu.high_score:
            menu.set_score(self.score)

    def try_again(self):
        self.remove_widget(self.lose_info)
        self.score = 0
        self.score_board.text = str(self.score)
        self.bombs_count = 0
        self.bomb_label.text = str(self.bombs_count)
        self.bomb_unactive()
        self.game_active = True
        self.start_game()

    def on_touch_down(self, touch):
        if self.game_active:
            self.last_x = touch.pos[0]
            self.last_y = touch.pos[1]

        super(PlayScreen, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.game_active:
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
                    self.last_touched_block.click_destroy()
                    return

                self.last_touched_block.move(direction)
        else:
            self.try_again()

        super(PlayScreen, self).on_touch_up(touch)

    def print_board(self):
        for y in self.blocks:
            for block in y:
                block.print_index()
            print("\n")


class OptionButton(Button):
    def __init__(self, option, **kwargs):
        super(OptionButton, self).__init__(**kwargs)
        self.option = option

        self.text = str(option)
        self.font_size = self.height * 0.2
        self.background_color = (.3, .5, 1, .8)


class SettingsScreen(Screen):
    board_size_options = [4, 6, 8, 10, 15]
    colors_count_options = [4, 5, 6, 7, 8]

    board_size = 8
    color_count = 5

    board_size_btn = None
    color_count_btn = None

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        for size in self.board_size_options:
            btn = OptionButton(size)
            btn.bind(on_press=self.change_board)
            if size == self.board_size:
                print("size: " + str(size))
                print (btn.option)
                btn.disabled = True
                self.board_size_btn = btn
            self.board_size_grid.add_widget(btn)

        for size in self.colors_count_options:
            btn = OptionButton(size)
            btn.bind(on_press=self.change_color)
            if size == self.color_count:
                btn.disabled = True
                self.color_count_btn = btn
            self.colors_count_grid.add_widget(btn)

    def save(self):
        print("SAVING")

    def change_board(self, instance):
        play_screen = self.manager.get_screen('play')
        if self.board_size != instance.option:
            self.board_size_btn.disabled = False
            self.board_size = instance.option

            instance.disabled = True
            self.board_size_btn = instance

            play_screen.board_size = self.board_size
            play_screen.try_again()

    def change_color(self, instance):
        play_screen = self.manager.get_screen('play')
        if self.color_count != instance.option:
            self.color_count_btn.disabled = False
            self.color_count = instance.option

            instance.disabled = True
            self.color_count_btn = instance

            play_screen.color_count = self.color_count
            play_screen.try_again()


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
