import sqlite3
from sqlite3 import Error
import sys
import time
import os

class VehicleDatabase:

    def __init__(self):
        self.databaseFile = "vehicleDatabase.db"
        # create connection to DB
        #conn = None
        try:
            conn = sqlite3.connect(self.databaseFile)

        except Error as e:
            print(e)
            print("\nUnable to create connection to Database!\n")
            return

        # create table for vehicles in DB
        #self.connection = conn
        if conn is not None:
            sqlCreatePresentVehiclesTable = """ CREATE TABLE IF NOT EXISTS vehicles (
                                                licencePlate text PRIMARY KEY,
                                                arrivalTime real NOT NULL,
                                                departureTime real
                                            ); """
            try:
                c = conn.cursor()
                c.execute(sqlCreatePresentVehiclesTable)
            except Error as e:
                print(e)
        conn.close()

    def unconfigure(self):
        """
        disconnects from databaseand deletes it
        """
        #self.connection.close()
        os.remove(self.databaseFile)
            
            
        
    def addVehicle(self, licencePlate, arrivalTime):
        """
        add a new vehicle into the vehicles table
        :param licencePlate:
        :param arrivalTime:
        """
        #with self.connection as con:
        with sqlite3.connect(self.databaseFile) as con:
            sql = ''' INSERT INTO vehicles(licencePlate,arrivalTime,departureTime)
                      VALUES(?,?,NULL) '''
            cur = con.cursor()
            cur.execute(sql, (licencePlate, arrivalTime))
            con.commit()

    def updateDepartureTime(self, departureTime, licencePlate):
        """
        update departure time of a vehicle
        :param departureTime:
        """
        #with self.connection as con:
        with sqlite3.connect(self.databaseFile) as con:
            sql = ''' UPDATE vehicles
                      SET departureTime = ?
                      WHERE licencePlate = ?'''
            cur = con.cursor()
            cur.execute(sql, (departureTime, licencePlate))
            con.commit()

    def removeVehicle(self, licencePlate):
        """
        not sure if necessary
        """
        #with self.connection as con:
        with sqlite3.connect(self.databaseFile) as con:
            cur = con.cursor()
            cur.execute('DELETE FROM vehicles WHERE licencePlate=?', (licencePlate,)) # needs to be tuple, hence the comma (vehicleID,) 
            con.commit()
        

    def getPresentVehicles(self):
        """
        Query all vehicles without departure time
        :return:
        """
        #with self.connection as con:
        with sqlite3.connect(self.databaseFile) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM vehicles WHERE departureTime IS NULL")
     
            rows = cur.fetchall()
            con.commit()
     
        return rows

    def vehicleIsPresent(self, licencePlate):
        """
        returns True if licencePlate is present in databaze, False otherwise
        """
        #with self.connection as con:
        with sqlite3.connect(self.databaseFile) as con:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM vehicles WHERE licencePlate=?", (licencePlate,))
     
            rows = cur.fetchall()
            con.commit()
        return rows != []

    def getAllVehicles(self):
        """
        Query all vehicles without departure time
        :return:
        """
        #with self.connection as con:
        with sqlite3.connect(self.databaseFile) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM vehicles")
     
            rows = cur.fetchall()
            con.commit()
        return rows
