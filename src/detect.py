#A Gender and Age Detection program by Mahesh Sawant

import cv2
import math
import argparse
from pathlib import Path
import logging
import numpy as np


class FaceDetection():
    MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
    ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']

    # Each model has a prototxt file which defines the model architecture 
    # and a .caffemodel file which contains the weights for the actual layers
    required_files = {
        "faceProto": "assets/opencv_face_detector.pbtxt",
        "faceModel":"assets/opencv_face_detector_uint8.pb",
        "ageProto":"assets/age_deploy.prototxt",
        "ageModel":"assets/age_net.caffemodel",
        "genderProto":"assets/gender_deploy.prototxt",
        "genderModel":"assets/gender_net.caffemodel",
    }
    gender_list = ['Male','Female']

    face_nn = None
    age_nn = None
    gender_nn = None

    # Variables
    age_final = None
    gender_final = None

    def __init__(self,camera):
        self.camera = camera
    
    def check_files(self):
        for file in self.required_files:
            if not Path(self.required_files.get(file)).exists():
                raise FileNotFoundError(f"{file} not found")
        print("All files found...")

    def setup_neural_networks(self):
        self.face_nn=cv2.dnn.readNet(self.required_files.get("faceModel"),self.required_files.get("faceProto"))
        self.age_nn=cv2.dnn.readNet(self.required_files.get("ageModel"),self.required_files.get("ageProto"))
        self.gender_nn=cv2.dnn.readNet(self.required_files.get("genderModel"),self.required_files.get("genderProto"))
        print("Neural networks setup complete...")

    def scan_faces(self,frame,conf_threshold=0.7):
        neural_net = self.face_nn
        frameOpencvDnn=frame.copy()
        frameHeight=frameOpencvDnn.shape[0]
        frameWidth=frameOpencvDnn.shape[1]
        blob=cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)
        neural_net.setInput(blob)
        detections=neural_net.forward()
        faceBoxes=[]
        for i in range(detections.shape[2]):
            confidence=detections[0,0,i,2]
            # If the confidence is less than 70% then ignore the detection
            if confidence>conf_threshold:
                x1=int(detections[0,0,i,3]*frameWidth)
                y1=int(detections[0,0,i,4]*frameHeight)
                x2=int(detections[0,0,i,5]*frameWidth)
                y2=int(detections[0,0,i,6]*frameHeight)
                faceBoxes.append([x1,y1,x2,y2])
        return  faceBoxes

    def detect(self):
        padding = 20
        # Read a frame 
        texture = self.camera.texture
        if texture is None:
            # We have not received any data from the camera yet
            logging.error("Camera has not started yet")
            return
        
        pixel_data = texture.pixels

        frame = np.frombuffer(pixel_data,dtype= np.uint8).reshape(texture.height, texture.width, -1)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        face_boxes = self.scan_faces(frame)
        
        if not face_boxes:
            print("No face detected")
            return
        for face_box in face_boxes:
            face = frame[max(0,face_box[1]-padding):
                         min(face_box[3]+padding,frame.shape[0]-1),max(0,face_box[0]-padding)
                            :min(face_box[2]+padding, frame.shape[1]-1)]
            blob = cv2.dnn.blobFromImage(face, 1.0, (227,227), self.MODEL_MEAN_VALUES, swapRB=False)

            # Detect gender
            self.gender_nn.setInput(blob)
            gender_preds = self.gender_nn.forward()
            self.gender_final = self.gender_list[gender_preds[0].argmax()]

            # Detect age
            self.age_nn.setInput(blob)
            age_preds = self.age_nn.forward()
            self.age_final = self.ageList[age_preds[0].argmax()]


if __name__ == "__main__":
    face_detection = FaceDetection()
    face_detection.check_files()
    face_detection.setup_neural_networks()
    face_detection.detect()
    