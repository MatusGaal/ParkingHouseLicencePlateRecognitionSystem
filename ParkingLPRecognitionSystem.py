import VehicleDatabase
import useOpenAlpr
import cv2
import threading
import time
import sys
import os

class ParkingLPRecognitionSystem:

    def __init__(self, entranceCameraNumber, exitCameraNumber, localization = "eu", configurationFile = "openalpr.conf", maxRecognitionAttempts = 1):
        #currentDirectory = os.path.split(sys.argv[0])[0]
        #framesDirectory = os.path.join(currentDirectory, "currentCameraFrames")

        #if not os.path.isdir(framesDirectory):
        #    os.mkdir(framesDirectory)

        #self.entranceFramePath = os.path.join(framesDirectory, "entranceFrame.jpg")
        self.entranceFramePath = "entranceFrame.jpg"
        #self.exitFramePath = os.path.join(framesDirectory, "exitFrame.jpg")
        self.exitFramePath = "exitFrame.jpg"
        self.currentEntrancePlate = ""
        self.currentExitPlate = ""

        self.licencePlateRecognizer = useOpenAlpr.UseOpenAlpr(localization, configurationFile, maxRecognitonAttempts) # add attributes for this?
        self.vehicleDatabase = VehicleDatabase.VehicleDatabase()
        self.entranceCamera = cv2.VideoCapture(entranceCameraNumber)
        self.entranceCameraNumber = entranceCameraNumber
        self.exitCamera = cv2.VideoCapture(exitCameraNumber)
        self.exitCameraNumber = exitCameraNumber
        self.RecognitionRunning = False
        self.mainLoopThread = None

    def PrintPresentVehicles(self):
        """
        prints info about vehicles that entered but didn't leave yet 
        """
        vehicles = self.vehicleDatabase.getPresentVehicles()

        for vehicle in vehicles:
            print(vehicle[0] + ", entered: " + time.ctime(vehicle[1]))

    def PrintAllVehicles(self):
        """
        prints info about all vehicles that entered 
        """
        vehicles = self.vehicleDatabase.getAllVehicles()

        for vehicle in vehicles:
            left = "Still present" if vehicle[2] == None else time.ctime(vehicle[2])
            print(vehicle[0] + ", entered: " + time.ctime(vehicle[1]) + ", left: " + left)

    def unloadLPRecognizer(self):
        self.licencePlateRecognizer.unload()
        

    def handleEntranceFrame(self, frame):
        cv2.imwrite(self.entranceFramePath, frame)
        plate = self.licencePlateRecognizer.getPlateFromJPG(self.entranceFramePath)

        if plate == "" or plate == self.currentEntrancePlate:
            return

        self.currentEntrancePlate = plate
        
        try:
            self.vehicleDatabase.addVehicle(plate, time.time())
        except sqlite3.IntegrityError as e:
            print("Entering vehicle with licence Plate: " + plate + " is already in the parking house!")

    def handleExitFrame(self, frame):
        cv2.imwrite(self.exitFramePath, frame)
        plate = self.licencePlateRecognizer.getPlateFromJPG(self.exitFramePath)

        if plate == "" or plate == self.currentExitPlate:
            return

        self.currentExitPlate = plate

        self.vehicleDatabase.updateDepartureTime(time.time(), plate)

    def mainLoop(self):
        if not self.entranceCamera.isOpened():
            self.entranceCamera.open(self.entranceCameraNumber)
        if not self.exitCamera.isOpened():
            self.exitCamera.open(self.exitCameraNumber)

        while self.RecognitionRunning:
            ret, entranceFrame = self.entranceCamera.read()
            ret, exitFrame = self.exitCamera.read()

            entranceThread = threading.Thread(target=self.handleEntranceFrame, args=(entranceFrame,))
            exitThread = threading.Thread(target=self.handleExitFrame, args=(exitFrame,))

            entranceThread.start()
            exitThread.start()

            time.sleep(0.5)

    def Run(self):
        self.RecognitionRunning = True
        self.mainLoopThread = threading.Thread(target=self.mainLoop, args=())
        self.mainLoopThread.start()

    def Stop(self):
        self.RecognitionRunning = False
        if self.mainLoopThread != None:
            self.mainLoopThread.join()
            self.entranceCamera.release()
            self.exitCamera.release()
            
