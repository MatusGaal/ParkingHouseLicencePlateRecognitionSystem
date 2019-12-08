import VehicleDatabase
import useOpenAlpr
import cv2
import threading
import time
import sys
import os

class ParkingLPRecognitionSystem:

    def __init__(self, entranceCameraNumber, exitCameraNumber, localization = "eu", configurationFile = "openalpr.conf", maxRecognitionAttempts = 1):
        self.entranceFramePath = "entranceFrame.jpg"
        self.exitFramePath = "exitFrame.jpg"
        self.currentEntrancePlate = ""
        self.currentExitPlate = ""
        self.licencePlateRecognizerEntrance = useOpenAlpr.UseOpenAlpr(localization, configurationFile, maxRecognitionAttempts) # add attributes for this?
        self.licencePlateRecognizerExit = useOpenAlpr.UseOpenAlpr(localization, configurationFile, maxRecognitionAttempts) # add attributes for this?
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
        '''
        expects frame from entrance camera, checks whether frame contians licence plate.
        If frame contains licence plate, checks wether licence plate is alredy in database and adds it needed
        '''
        cv2.imwrite(self.entranceFramePath, frame)
        plate = self.licencePlateRecognizerEntrance.getPlateFromJPG(self.entranceFramePath)

        if plate == "" or plate == self.currentEntrancePlate:
            return

        self.currentEntrancePlate = plate
        print("\n\nEntrancePlate:" + plate + "\n\n")
        try:
            if self.vehicleDatabase.vehicleIsPresent(plate):
                # here cen be added some form of reaction to entering another vehicle with the same licence plate
                print("This vehicle (licence plate:" + plate + ") is already presen!")
                return
            self.vehicleDatabase.addVehicle(plate, time.time())
        except sqlite3.IntegrityError as e:
            print("Entering vehicle with licence Plate: " + plate + " is already in the parking house!")

    def handleExitFrame(self, frame):
        '''
        expects frame from exit camera, checks whether frame contains licence plate.
        If frame contains licence plate, chcecks wether the vehicle is present in database, adds departure time if needed 
        '''
        cv2.imwrite(self.exitFramePath, frame)
        plate = self.licencePlateRecognizerExit.getPlateFromJPG(self.exitFramePath)

        if plate == "" or plate == self.currentExitPlate:
            return

        self.currentExitPlate = plate
        print("\n\nExitPlate:" + plate + "\n\n")
        if not self.vehicleDatabase.vehicleIsPresent(plate):
            print("Vehicle (licence plate:" + plate + ") is leaving but never entered!")
            return
        self.vehicleDatabase.updateDepartureTime(time.time(), plate)

    def mainLoop(self):
        '''
        main loop nahdling recognition from given cameras
        '''
        if not self.entranceCamera.isOpened():
            self.entranceCamera.open(self.entranceCameraNumber)
        if not self.exitCamera.isOpened():
            self.exitCamera.open(self.exitCameraNumber)

        while self.RecognitionRunning:
            ret, entranceFrame = self.entranceCamera.read()
            ret1, exitFrame = self.exitCamera.read()

            if not ret1 or not ret:
                print("\n\n\n!!!!end of the line!!!!\n\n\n")
                break

            entranceThread = threading.Thread(target=self.handleEntranceFrame, args=(entranceFrame,))
            exitThread = threading.Thread(target=self.handleExitFrame, args=(exitFrame,))

            entranceThread.start()
            exitThread.start()

            time.sleep(0.5)

    def Run(self):
        '''
        Starts thread handling recognition from given cameras. Needs to be ended with self.Stop()
        '''
        self.RecognitionRunning = True
        self.mainLoopThread = threading.Thread(target=self.mainLoop, args=())
        self.mainLoopThread.start()

    def Stop(self):
        '''
        Stops thread Handling recognition from given cameras.
        '''
        self.RecognitionRunning = False
        if self.mainLoopThread != None:
            self.mainLoopThread.join()
            self.entranceCamera.release()
            self.exitCamera.release()
            
