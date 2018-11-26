import os
import random

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

Builder.load_file('graphic.kv')


# PROJECT CLOSED I WANT TO THANK TO MYSELF.


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
    opacity = 1.2

    def __init__(self, c, x, y, **kwargs):
        super(Block, self).__init__(**kwargs)
        self.index_x = x
        self.index_y = y

        self.set_color(c)

    def on_press(self):
        parent = self.parent.parent.parent
        if not parent.is_bomb_drag:
            parent.block_pressed(self)
        else:
            self.blow()

    def blow(self):
        parent = self.parent.parent.parent
        parent.add_bomb(-1)
        self.destroy_blocks_nearby()
        parent.bomb_unactive()

    def destroy_blocks_nearby(self):
        if self.block_up.c != "":
            self.block_up.block_left.destroy()
            self.block_up.block_right.destroy()
        if self.block_down.c != "":
            self.block_down.block_left.destroy()
            self.block_down.block_right.destroy()

        self.block_left.destroy()
        self.block_up.destroy()
        self.destroy()
        self.block_right.destroy()
        self.block_down.destroy()

    def check_for_bonus_row(self, side_a1, side_a2, side_b1, side_b2):
        bombs_to_add = 0

        if self.c == side_a1.c and self.c == side_b1.c and self.c == side_b2.c:
            bombs_to_add += 1

        if self.c == side_a1.c and self.c == side_b1.c and self.c == side_a2.c:
            bombs_to_add += 1

        return bombs_to_add

    def look_for_line(self, destroy=True, look_for_black=True):
        parent = self.parent.parent.parent

        horizontal_blocks = self.check_for_bonus_row(self.block_left, self.block_left2, self.block_right, self.block_right2)
        vertical_blocks = self.check_for_bonus_row(self.block_up, self.block_up2, self.block_down, self.block_down2)

        if self.click_destroy():
            parent.add_bomb(horizontal_blocks)
            parent.add_bomb(vertical_blocks)

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

        if len(to_destroy) > 3:
            for block in to_destroy:
                block.look_for_black()
                block.destroy()

            if len(to_destroy) > 4:
                parent = self.parent.parent.parent
                parent.add_score(parent.block_destroy_bonus * len(to_destroy))
            return True
        return False

    def look_for_black(self):
        if self.block_left.c == "black" or self.block_right.c == "black" or self.block_up.c == "black" or self.block_down.c == "black":
            Clock.schedule_once(self.parent.parent.parent.game_over, .5)

    def fall(self, dt):
        if self.index_y > 0:
            if self.c == "white":
                self.swap_colors(self.block_up, False)
                Clock.schedule_once(self.block_up.fall, 0.03)
        self.check_is_destroyed()

    def destroy(self):
        Clock.schedule_once(self.set_to_destroyed, 0.1)

    def set_to_destroyed(self, dt):
        parent = self.parent.parent.parent
        if self.c == "black":
            parent.add_score(parent.black_bonus)
            parent.add_black_chance(-9)

        self.set_color("white")
        Clock.schedule_once(self.fall, 0.15)
        parent.add_score()

    def move(self, direction):
        swap_block = self.get_block_by_direction(direction)
        if swap_block is not None:
            self.swap_colors(swap_block)
        self.parent.parent.parent.last_touched_block = None

    def swap_colors(self, swap_block, look=True):
        if swap_block.c != self.c:
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
        if parent.actual_chance_for_black < parent.black_chance:
            available_colors = [x for x in parent.colors if x != self.c]
            c = random.choice(available_colors)
            self.set_color(c)
            parent.add_black_chance(0.9)
            parent.black_chance -= 0.1
        else:
            self.set_color("black")
            parent.add_black_chance(-7)

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

    def load_source(self):
        self.source = "img/blocks/" + str(self.c) + "_block.png"


class SquareButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(SquareButton, self).__init__(**kwargs)


class GameOverScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(GameOverScreen, self).__init__(**kwargs)


class BombActiveScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(BombActiveScreen, self).__init__(**kwargs)
        self.anim = Animation(opacity=0.7, duration=.7) + Animation(opacity=1.5, duration=.7)
        self.anim.repeat = True
        self.anim.start(self.background)


class MenuScreen(Screen):
    high_score = 0

    light_color = (.75, .75, .75, 1)
    dark_color = (.13, .13, .13, 1)

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

    @staticmethod
    def get_random_rgba():
        return random.uniform(0.1, 0.9), random.uniform(0.1, 0.9), random.uniform(0.1, 0.9), .9

    def set_score(self, score):
        self.high_score = int(score)
        self.high_score_label.text = str(score)

        app = App.get_running_app()
        save_file = open(app.user_data_dir + "/save.txt", "w")
        save_file.write(str(self.high_score) + "\n")
        save_file.close()


class PlayScreen(Screen):
    all_colors = ["red", "blue", "green", "yellow", "orange", "purple", "turquoise", "pink"]
    colors = []
    blocks = []

    # static Game settings
    board_size = 8
    color_count = 6
    black_chance = 30
    touch_accuracy = 20
    block_destroy_points = 10
    block_destroy_bonus = 5
    black_bonus = 70
    bomb_bonus = 30

    score = 0
    bombs_count = 0
    actual_chance_for_black = 0
    last_x = 0
    last_y = 0
    actually_x = 0
    actually_y = 0
    last_touched_block = None
    game_active = True
    is_bomb_drag = False

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        self.lose_info = GameOverScreen()
        self.bomb_active_screen = BombActiveScreen()
        self.start_game()

    def bomb_drag(self):
        if self.bombs_count > 0:
            if not self.is_bomb_drag:
                self.bomb_active()
            else:
                self.bomb_unactive()

    def bomb_active(self):
        self.last_touched_block = None
        self.is_bomb_drag = True
        self.bomb.size_hint_x = .25
        self.add_widget(self.bomb_active_screen)

    def bomb_unactive(self):
        self.is_bomb_drag = False
        self.bomb.size_hint_x = .22
        self.remove_widget(self.bomb_active_screen)

    def add_score(self, amount=None):
        if self.game_active:
            if amount is not None:
                self.score += amount
            else:
                self.score += self.block_destroy_points
            self.score_board.text = str(self.score)

    def add_bomb(self, amount=1):
        self.bombs_count += amount
        self.bomb_label.text = str(self.bombs_count)
        self.add_score(self.bomb_bonus)

    def add_black_chance(self, amount):
        self.actual_chance_for_black += amount

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

    def game_over(self, dt):
        if self.lose_info not in self.children:
            self.add_widget(self.lose_info)
        self.game_active = False
        self.check_for_high_score()

    def check_for_high_score(self):
        menu = self.manager.get_screen('menu')
        settings_screen = self.manager.get_screen("settings")
        if settings_screen.board_size == settings_screen.default_board_size \
                and settings_screen.color_count == settings_screen.default_color_count:
            if self.score > menu.high_score:
                menu.set_score(self.score)

    def try_again(self):
        self.remove_widget(self.lose_info)
        self.score = 0
        self.score_board.text = str(self.score)
        self.bombs_count = 0
        self.bomb_label.text = str(self.bombs_count)
        self.actual_chance_for_black = 0
        self.black_chance = 30
        self.bomb_unactive()
        self.game_active = True
        self.last_touched_block = None
        self.start_game()

    def on_touch_down(self, touch):
        if self.game_active and not self.is_bomb_drag:
            self.last_x = touch.pos[0]
            self.last_y = touch.pos[1]

        super(PlayScreen, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.game_active:
            if self.last_touched_block is not None and not self.is_bomb_drag:
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


class OptionButton(Button):
    def __init__(self, option, **kwargs):
        super(OptionButton, self).__init__(**kwargs)
        self.option = option

        self.font_size = self.size_hint_x * 40
        self.text = str(option)
        self.background_color = (.3, .5, 1, .8)


class SettingsScreen(Screen):
    board_size_options = [5, 6, 8, 10, 12]
    colors_count_options = [4, 5, 6, 7, 8]

    default_board_size = 8
    default_color_count = 6

    board_size = default_board_size
    color_count = default_color_count

    board_size_btn = None
    color_count_btn = None

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        for size in self.board_size_options:
            btn = OptionButton(size)
            btn.bind(on_press=self.change_board)
            self.board_size_grid.add_widget(btn)
            if size == self.board_size:
                btn.disabled = True
                self.board_size_btn = btn

        for size in self.colors_count_options:
            btn = OptionButton(size)
            self.colors_count_grid.add_widget(btn)
            btn.bind(on_press=self.change_color)
            if size == self.color_count:
                btn.disabled = True
                self.color_count_btn = btn

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
    info_count = 3
    current_info = 1

    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        self.change_info_image(0)

    def change_info_image(self, direction):
        self.current_info += direction
        if 0 < self.current_info <= self.info_count:
            self.load_info_source()
        else:
            self.current_info -= direction

        if self.current_info == 3:
            self.rightb.size_hint_x = 0
        else:
            self.rightb.size_hint_x = .12

        if self.current_info == 1:
            self.leftb.size_hint_x = 0
        else:
            self.leftb.size_hint_x = .12

    def load_info_source(self):
        self.info.source = "img/game_info/" + str(self.current_info) + ".png"


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(PlayScreen(name='play'))
sm.add_widget(SettingsScreen(name='settings'))
sm.add_widget(InfoScreen(name='info'))


class Decode(App):
    def build(self):
        data = 0
        if os.path.exists(self.user_data_dir + "/save.txt"):
            save_file = open(self.user_data_dir + "/save.txt", "r")
            data = save_file.readlines()[0].strip()
            save_file.close()
        sm.get_screen('menu').set_score(int(data))
        return sm


if __name__ == '__main__':
    Decode().run()
