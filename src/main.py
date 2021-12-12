import os
import ast
from os import walk
import cv2

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.config import ConfigParser
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty

Builder.load_file('ui.kv')

faceCascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

class VideosList(Screen):
    def __init__(self, **kwargs):
        super(VideosList, self).__init__(**kwargs)

    def on_enter(self):
        self.set_list_videos()

    def set_list_videos(self):
        filenames = next(walk('../public/'), (None, None, []))[2]
        self.ids.rv.data = []
        for name in filenames:
            if name not in self.ids.rv.data:
                self.ids.rv.data.append({
                    'viewclass': 'Button',
                    'text': name,
                    'on_press': self.redirect
                })

    def redirect(self):
        app = App.get_running_app()
        sm = app.root
        sm.current = 'menu',

class KivyCamera(Image):

    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = None
        self.output = None

    def start(self, capture, fps=60):
        self.capture = capture
        self.output = cv2.VideoWriter('./temp.avi', cv2.VideoWriter_fourcc(*'XVID'), 10, (640, 480));
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1.0 / fps)

    def stop(self):
        global capture
        self.output.release()
        capture.release()
        cv2.destroyAllWindows()

    def save(self, filename):
        self.output.release()
        os.rename('./temp.avi', '../public/'+filename+'.avi')

    def update(self, dt):
        return_value, frame = self.capture.read()
        if return_value:
            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=12,
                minSize=(30, 30),
            )

            # Draw a rectangle around the faces
            for (x, y, width, height) in faces:
                cv2.putText(frame, 'Russkiy',  (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  (0, 255, 0))
                cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
            self.output.write(frame)
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

    def save_file(self, filename):
        self.ids.qrcam.save(filename)


class VideoPage(Screen):
    print('video_page')

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
