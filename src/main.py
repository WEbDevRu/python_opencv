import os
import ast
import time
import cv2

from datetime import datetime
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.config import ConfigParser
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.base import EventLoop
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty

Builder.load_file('ui.kv')


class SortedListFood(Screen):
    def on_enter(self):
        data_foods = self.get_data_foods()
        self.set_list_foods(data_foods)

    def get_data_foods(self):
        return ast.literal_eval(
            App.get_running_app().config.get('General', 'user_data'))

    def set_list_foods(self, data_foods):
        for f, d in sorted(data_foods.items(), key=lambda x: x[1]):
            fd = f.decode('u8') + ' ' + (datetime.fromtimestamp(d).strftime(
                '%Y-%m-%d'))
            data = {'viewclass': 'Button', 'text': fd}
            if data not in self.ids.rv.data:
                self.ids.rv.data.append({'viewclass': 'Button', 'text': fd})


class KivyCamera(Image):

    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = None
        self.output = None

    def start(self, capture, fps=60):
        print('start')
        self.capture = capture
        self.output = cv2.VideoWriter('../public/CAPTURE.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480));
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1.0 / fps)

    def stop(self):
        global capture
        self.output.release()
        capture.release()
        cv2.destroyAllWindows()

    def update(self, dt):
        return_value, frame = self.capture.read()
        if return_value:
            texture = self.texture
            self.output.write(frame)
            w, h = frame.shape[1], frame.shape[0]
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(w, h))
                texture.flip_vertical()
            texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()


capture = None


class CaptureVideo(Screen):
    _app = ObjectProperty()

    buttonText = StringProperty('Начать запись')

    def toggleVideoCapture(self, *largs):
        global capture
        if capture != None:
            self.buttonText = 'Начать запись'
            self.ids.qrcam.stop()
            capture = None
        else:
            capture = cv2.VideoCapture(0)
            self.buttonText = 'Остановить запись'
            self.ids.qrcam.start(capture)

    def doexit(self):
        global capture
        if capture != None:
            capture.release()
            capture = None
        EventLoop.close()


class VideoCameraApp(App):
    def __init__(self, **kvargs):
        super(VideoCameraApp, self).__init__(**kvargs)

        self.config = ConfigParser()
        self.screen_manager = Factory.ManagerScreens()
        self.user_data = {}

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'user_data', '{}')

    def set_value_from_config(self):
        self.config.read(os.path.join(self.directory, '%(appname)s.ini'))
        self.user_data = ast.literal_eval(self.config.get(
            'General', 'user_data'))

    def get_application_config(self):
        return super(VideoCameraApp, self).get_application_config(
            '{}/%(appname)s.ini'.format(self.directory))

    def build(self):
        return self.screen_manager


if __name__ == '__main__':
    VideoCameraApp().run()
