import os
import useOpenAlpr as openalpr
os.chdir(".//PlateDetection")

def getFirstNPlatesFromVideo(cameraNumber = 0):
    cap = cv2.VideoCapture(cameraNumber)

    alpr = openalpr.Alpr("us",
                         "openalpr.conf",
                         "runtime_data")

    if not alpr.is_loaded():
        print("Error loading OpenALPR")
        return False

    alpr.set_top_n(10)
    alpr.set_default_region("md")


    try:
        while True:
            ret, frame = cap.read()
            cv2.imwrite("plateFrame.jpg", frame) # save image

            results = alpr.recognize_file("C:\\Users\\matus\\Desktop\\bakalarka\\openalpr_64ajnovsi release\\plateFrame.jpg")
            
            if results['results'] == []:
                continue

            i = 0
            for plate in results['results']:
                i += 1
                print("Plate #" +  str(i))
                print("   %12s %12s" % ("Plate", "Confidence"))
                for candidate in plate['candidates']:
                    prefix = "-"
                    if candidate['matches_template']:
                        prefix = "*"
                            
                    print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence']))
        
            
    finally:
        cap.release()
        cv2.destroyAllWindows()
        alpr.unload()
        return True

def printResultPlates(results):
    for plate in results['results']:
            i += 1
            print("Plate #" +  str(i))
            print("   %12s %12s" % ("Plate", "Confidence"))
            for candidate in plate['candidates']:
                prefix = "-"
                if candidate['matches_template']:
                    prefix = "*"
                        
                print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence']))

def plateIsIn(seeking = ["RX65PPE"], pictureDir = "C:\\Users\\matus\\Desktop\\bak\\testFiles\\images\\car1.jpg"):
    alpr = openalpr.Alpr("us",
                         "openalpr.conf",
                         "runtime_data")

    output = False
    if not alpr.is_loaded():
        print("Error loading OpenALPR")
        return False


    alpr.set_top_n(20)
    alpr.set_default_region("md")

    results = alpr.recognize_file(pictureDir)

    i = 0
    for plate in results['results']:
        for candidate in plate['candidates']:
            if candidate['matches_template']:
                print("what is this? " + candidate['plate'] + ", " + str(candidate['confidence']))
            if candidate['plate'] in seeking:
                output = True
                print(candidate['plate'] + ", " + str(candidate['confidence']))
                break
    
    print(output)
    # Call when completely done to release memory
    alpr.unload()
    #print(output)
    #return output


def getPlate(pictureDir = "C:\\Users\\matus\\Desktop\\bakalarka\\testFiles\\test_001.jpg"):
    alpr, result = openalpr.loadAlpr(localization = "eu", configurationFile = "openalpr.conf", maxRecognitionAttempts = 1, defaultImageRegion = "md")
    if not result:
        return

    plate = openalpr.openAlprGetPlate(alpr, pictureDir)
    print("Plate: " + str(plate))
    
    alpr.unload()

    return
