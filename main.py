from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

Window.size = (270, 480)
Builder.load_file('graphic.kv')


class MenuScreen(Screen):
    light_color = (.9, .9, .9, 1)
    dark_color = (.1, .1, .1, 1)

    def __init__(self, color, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.color = color

        self.set_color(color)

    def change_theme(self):
        self.color = not self.color
        self.set_color(self.color)

    def set_color(self, color):
        if color:
            Window.clearcolor = self.light_color
        else:
            Window.clearcolor = self.dark_color


class PlayScreen(Screen):
    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)


sm = ScreenManager()
sm.add_widget(MenuScreen(True, name='menu'))
sm.add_widget(PlayScreen(name='play'))
sm.add_widget(SettingsScreen(name='settings'))


class TestApp(App):

    def build(self):
        return sm


if __name__ == '__main__':
    TestApp().run()
