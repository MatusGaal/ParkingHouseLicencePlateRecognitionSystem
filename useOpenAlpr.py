import sys
import os
import openalpr

from argparse import ArgumentParser

class UseOpenAlpr:

    def __init__(self, localization = "eu", configurationFile = "openalpr.conf", maxRecognitionAttempts = 1):
        # loads alpr configuration files
        self.alpr = openalpr.Alpr(localization, configurationFile, "runtime_data")
        aelf.alpr.set_top_n(maxRecognitionAttempts)

        
    def unload(self):
        """
        use when finished with recognizing licence plates
        """
        self.alpr.unload()

    def getPlateFromJPG(self, filePath):
        """
        recognizes licence plate in image on filePath path
        returns string with licence plate characters
        """
        
        result = self.alpr.recognize_file(filePath)
        plate = ""
        if result['results'] == []:
            plate = "" # no licence plate found  
        else:
            plate = result['results'][0]['candidates'][0]['plate']

        return plate
        
