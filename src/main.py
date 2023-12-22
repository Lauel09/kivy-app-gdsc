import kivymd
import speech_recognition as sr
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import threading
from detect import FaceDetection
from kivy.uix.camera import Camera
from kivy.app import App
from kivy.clock import Clock
# Load the .kv file

kv_config_string = '''
#:import MDFloatLayout kivymd.uix.floatlayout.MDFloatLayout
#:import MDBoxLayout kivymd.uix.boxlayout.MDBoxLayout
#:import MDCard kivymd.uix.card.MDCard
#:import MDLabel kivymd.uix.label.MDLabel
#:import MDIconButton kivymd.uix.button.MDIconButton
#:import MDTextField kivymd.uix.textfield.MDTextField
#:import MDRaisedButton kivymd.uix.button.MDRaisedButton
#:import MDBoxLayout kivymd.uix.boxlayout.MDBoxLayout
#:import MDToolbar kivymd.uix.toolbar.MDTopAppBar

<WelcomeScreen>:
    MDFloatLayout:
        canvas.before:
            Color:
                rgba: 0.5, 0.5, 1, 1  # Set the color to light blue
            Rectangle:
                pos: self.pos
                size: self.size
        MDBoxLayout:
            orientation: 'vertical'
            size_hint: None, None
            size: dp(300), dp(500)
            pos_hint: {'center_x': .5, 'center_y': .5}
            Image:
                source: 'assets/logo.png'
                size: dp(100), dp(100)
                pos_hint: {'center_x': 0.5}
            MDLabel:
                text: '[b][color=1,1,0,1]Welcome to the App![/color][/b]'
                markup: True
                font_size: dp(30)
                pos_hint: {'center_x': 0.5}
            MDRaisedButton:
                text: 'Go to login'
                on_release: root.login_screen()
                size_hint: None, None
                size: dp(150), dp(50)
                pos_hint: {'center_x': 0.5}
                pos: dp(100), dp(100)
                elevation_normal: 0
            Widget:

<MainScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Main Screen"
            left_action_items: [["arrow-left", lambda x: root.switch_screen()]]
        MDBoxLayout:
            orientation: 'horizontal'
            Camera:
                id: camera
                resolution: (640, 480)
                play: True
                size_hint_x: 0.5
            MDBoxLayout:
                orientation: 'vertical'
                MDBoxLayout:
                    MDTextField:
                        id: voice_input
                        text: root.voice_input_text
                        multiline: True
                        readonly: True
                        hint_text: 'Voice Input'
                MDRaisedButton:
                    text: 'Start Voice Recognition'
                    on_release: root.voice_recognition()
                    size: dp(150), dp(50)
                    elevation_normal: 0
                MDRaisedButton:
                    text: 'Start Face Recognition'
                    on_release: root.face_recognition()
                    size: dp(150), dp(50)
                    elevation_normal: 0

                MDLabel:
                    id: voice_label
                    text: 'Voice Recognition Result'
                    halign: 'center'
'''

Builder.load_string(kv_config_string)
kivymd.__version__ = "0.104.1"


class WelcomeScreen(Screen):
    def login_screen(self):
        self.manager.current = 'main_screen'

class MainScreen(Screen):
    voice_input_text = ""

    def _face_recognition(self):
        face_detection = FaceDetection(self.ids.camera)
        face_detection.check_files()
        face_detection.setup_neural_networks()
        Clock.schedule_once(lambda dt: face_detection.detect())
        print(face_detection.age_final,face_detection.gender_final)

    def face_recognition(self):
        # Run the face recognition on a new thread than 
        # running it on the main thread, which blocks
        # the updating of UI elements, which blocks the loading
        # of the video, and leaves it stuck.
        threading.Thread(
            target=self._face_recognition
        ).start()

    def switch_screen(self):
        app = App.get_running_app()
        app.root.current = 'welcome'

    def voice_recognition(self):
        # Run the voice recognition on a new thread than 
        # running it on the main thread, which blocks
        # the updating of UI elements, which blocks the loading
        # of the video, and leaves it stuck.
        threading.Thread(
            target=self._voice_recognition
        ).start()

    # Voice recognition happens here
    def _voice_recognition(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
    
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Starting speech recognition...")
            audio = recognizer.listen(source,timeout=10)
            print("Ending speech recognition...")
        try:
            result = recognizer.recognize_google(audio,language="en-US")
            print("Ending speech recognition...")
            self.voice_input_text = result
            Clock.schedule_once(self.update_voice_input,1)
        except sr.UnknownValueError:
            self.voice_input_text = "Could not understand audio"
        # This ensures that background proccess run this function
        # just once if possible to change the UI elements since the
        # non-main thread can't change the UI elements
        Clock.schedule_once(self.update_voice_input)
    
    def update_voice_input(self, dt):
        self.ids.voice_input.text = self.voice_input_text
    
class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(MainScreen(name='main_screen'))
        return sm

if __name__ == '__main__':
    MyApp().run()