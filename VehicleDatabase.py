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

        # create table for vehicles in DB
        self.connection = conn
        if self.connection is not None:
            sqlCreatePresentVehiclesTable = """ CREATE TABLE IF NOT EXISTS vehicles (
                                                licencePlate text PRIMARY KEY,
                                                arrivalTime real NOT NULL,
                                                departureTime real
                                            ); """
            try:
                c = self.connection.cursor()
                c.execute(sqlCreatePresentVehiclesTable)
            except Error as e:
                print(e)

    def unconfigure(self):
        """
        disconnects from databaseand deletes it
        """
        self.connection.close()
        os.remove(self.databaseFile)
            
            
        
    def addVehicle(self, licencePlate, arrivalTime):
        """
        add a new vehicle into the vehicles table
        :param licencePlate:
        :param arrivalTime:
        """
        with self.connection:
            sql = ''' INSERT INTO vehicles(licencePlate,arrivalTime,departureTime)
                      VALUES(?,?,NULL) '''
            cur = self.connection.cursor()
            cur.execute(sql, (licencePlate, arrivalTime))

    def updateDepartureTime(self, departureTime, licencePlate):
        """
        update departure time of a vehicle
        :param departureTime:
        """
        with self.connection:
            sql = ''' UPDATE vehicles
                      SET departureTime = ?
                      WHERE licencePlate = ?'''
            cur = self.connection.cursor()
            cur.execute(sql, (departureTime, licencePlate))
            self.connection.commit()

    def removeVehicle(self, licencePlate):
        """
        not sure if necessary
        """
        with self.connection:
            cur = self.connection.cursor()
            cur.execute('DELETE FROM vehicles WHERE licencePlate=?', (licencePlate,)) # needs to be tuple, hence the comma (vehicleID,) 
            self.connection.commit()
        

    def getPresentVehicles(self):
        """
        Query all vehicles without departure time
        :return:
        """
        with self.connection:
            cur = self.connection.cursor()
            cur.execute("SELECT * FROM vehicles WHERE departureTime IS NULL")
     
            rows = cur.fetchall()
     
        return rows

    def vehicleIsPresent(self, licencePlate):
        """
        """
        with self.connection:
            cur = self.connection.cursor()
            cur.execute("SELECT 1 FROM vehicles WHERE licencePlate=?", (licencePlate,))
     
            rows = cur.fetchall()
     
        return rows != []

    def getAllVehicles(self):
        """
        Query all vehicles without departure time
        :return:
        """
        with self.connection:
            cur = self.connection.cursor()
            cur.execute("SELECT * FROM vehicles")
     
            rows = cur.fetchall()
     
        return rows
