import random

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

Window.size = (400, 700)
Builder.load_file('graphic.kv')


class Block(Image):
    def __init__(self, c, **kwargs):
        super(Block, self).__init__(**kwargs)
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
    bombs_count = 4
    colors = ["red", "blue", "green", "yellow"]

    touch_accuracy = 20
    last_x = 0
    last_y = 0
    actually_x = 0
    actually_y = 0

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        for i in range(100):
            self.board.add_widget(Block(random.choice(self.colors)))

    def bomb_drag(self):
        print("BOMB DRAGGED")

    def on_touch_down(self, touch):
        self.last_x = touch.pos[0]
        self.last_y = touch.pos[1]
        super(PlayScreen, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        self.actually_x = touch.pos[0]
        self.actually_y = touch.pos[1]
        dif_x = self.actually_x - self.last_x
        dif_y = self.actually_y - self.last_y

        if dif_y > self.touch_accuracy:
            print("Up")
        elif dif_y < -self.touch_accuracy:
            print("Down")
        elif dif_x > self.touch_accuracy:
            print("Right")
        elif dif_x < -self.touch_accuracy:
            print("LEFT")

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
