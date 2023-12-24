import kivymd
import speech_recognition as sr
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import threading
from detect import FaceDetection
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.app import App
from kivy.clock import Clock
from speech_recog import MedicineRecognizer
from logging import info,debug,warn,error
import cv2
from web_scraping_new import WebScraping
from pathlib import Path
# Load the .kv file'

Builder.load_file('src/main.kv')
kivymd.__version__ = "0.104.1"

face_detection = None

userGender = None
userAge = None

lastFrame = None

class WelcomeScreen(Screen):
    def login_screen(self):
        self.manager.current = 'main_screen'

class CameraWidget(Image):
    def __init__(self,capture,face_detection,fps, **kwargs):
        super(CameraWidget,self).__init__(**kwargs)
        self.capture = capture
        self.face_detection = face_detection
        self.fps = fps
        Clock.schedule_interval(self.update,1.0/fps)
        # Didn't work so commenting them out
        #width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        #height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def update(self, dt):
        # Here we read from the self.capture which is a video
        ret,frame = self.capture.read()
        # Reading happens in the BGR which needs to be
        # converted to RGB
        #info(ret)
        if ret:
            #frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            result_image = self.face_detection.detect(frame)
            #info(frame)
            
            buf1 = cv2.flip(result_image, 0)
            
            if frame is not None and buf1 is not None:
                buf = buf1.tostring()
                global userAge,userGender,lastFrame
                userAge = self.face_detection.age_final
                lastFrame = buf1
                if self.face_detection.age_final and self.face_detection.gender_final is not None:
                    userGender = self.face_detection.gender_final
                    info(f"Calculations\nAge:{userAge}\nGender:{userGender}")

                image_texture = Texture.create(size=(result_image.shape[1], result_image.shape[0]), colorfmt='rgb')
                image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
                self.texture = image_texture
                cv2.imwrite('assets/last_frame.png',frame)
                info(frame)

    
class CameraScreen(Screen):
    def __init__(self,screen_manager ,**kwargs):
        super(CameraScreen,self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.capture = None
        self.camera_widget = None
        info("Initializing CameraScreen...")

    def on_pre_enter(self,*args):
        global face_detection
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            error("Camera is not opened")
            return 
        self.camera_widget = CameraWidget(self.capture,face_detection=face_detection,fps=30)
        self.add_widget(self.camera_widget)

        Clock.schedule_once(self.switch_to_main,5)
    
    def switch_to_main(self,dt):
        if self.capture is not None:
            self.capture.release()
        self.manager.current = 'main_screen'
    
    def on_leave(self,*args):
        self.remove_widget(self.camera_widget)
        self.camera_widget = None
        self.screen_manager.get_screen('main_screen').update_image()
        self.screen_manager.get_screen('main_screen').change_image('last_frame.png')

class MainScreen(Screen):
    voice_input_text = ""
    meds_recognizer = None
    user_age = ""
    user_gender = ""
    path_user_image = 'assets/last_frame.png'
    user_image = None
    scraper = None
    def on_pre_enter(self) :
        global userAge,userGender
        if self.meds_recognizer is None:
            info("Setting up medicine recognizer")
            self.initialize_medicine_recognizer()
        if face_detection is None:
            info("Setting up face recognition...")
            self.setup_face_recognition()
        if userAge is None:
            self.ids.user_age.text = "Age: Unknown"
            self.user_age = "Age: Unknown"
        else:
            self.ids.user_age.text = f"Age: {userAge}"
        if userGender is None:
            self.ids.user_gender.text = "Gender: Unknown"
        else:
            self.ids.user_gender.text = f"Gender:{userGender}"
        
    def change_image(self,new_image_path):
        self.ids.user_image.source = new_image_path
        self.path_user_image = new_image_path
    
    def update_image(self):
        global lastFrame
        if lastFrame is not None:
            buf = lastFrame.tostring()
            image_texture = Texture.create(size=(lastFrame.shape[1], lastFrame.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
            self.ids.user_image.texture = image_texture
            self.user_image = image_texture

    def _initialize_medicine_recognizer(self):
        self.meds_recognizer = MedicineRecognizer()

    def initialize_medicine_recognizer(self):
        # Run the face recognition on a new thread than
        # running it on the main thread, which blocks
        # the updating of UI elements, which blocks the loading
        # of the video, and leaves it stuck.
        threading.Thread(
            target=self._initialize_medicine_recognizer
        ).start()

    def setup_face_recognition(self):
        threading.Thread(
            target=self._setup_face_recognition
        ).start()

    def _setup_face_recognition(self):
        global face_detection
        face_detection = FaceDetection()
        face_detection.check_files()
        face_detection.setup_neural_networks()
        info(f"Face Detection object:{face_detection}")
        info("Face detection setup complete")
        
    def _face_recognition(self):
        Clock.schedule_once(lambda dt: face_detection.detect())
        if (face_detection.age_final and face_detection.gender_final is not None):
            self.user.age = face_detection.age_final
            self.user.gender = face_detection.gender_final
        info(face_detection.age_final,face_detection.gender_final)

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
    
    def switch_to_camera(self):
        app = App.get_running_app()
        self.ids.voice_input.text = ' '
        self.ids.voice_label.text = ' '
        self.remove_widget(self.ids.voice_input)
        self.remove_widget(self.ids.voice_label)
        app.root.current = 'camera_screen'

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
            info("Starting speech recognition...")
            audio = recognizer.listen(source,timeout=10)
            info("Ending speech recognition...")

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
        if self.voice_input_text != "":
            self.meds_recognizer.extract_medicine_name(self.voice_input_text)
            self.scraper = WebScraping(self.meds_recognizer.meds_scanned)
            print("Finding medicines:")
            self.scraper.scrape()
            from pprint import pprint
            pprint(self.scraper.apollo_products)
                
        Clock.schedule_once(self.update_voice_input)
    
    def update_voice_input(self, dt):
        self.ids.voice_input.text = self.voice_input_text

    def get_search_results(self):
        info("Getting search results")
        
    
class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(MainScreen(name='main_screen'))
        sm.add_widget(CameraScreen(name='camera_screen',screen_manager=sm))
        return sm

if __name__ == '__main__':
    MyApp().run()
