#! /usr/bin/python

import threading, time
import sqlite3 as lite
import sys
import datetime
import RPi.GPIO as GPIO
import homeSystem

PIR = 13
LED = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIR, GPIO.IN)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)

   
def checkPIRSensor(channel):
    print 'Rising edge on PIR detected'
    try:
        #Check PIR sensor
        #if GPIO Pin is HIGH, call function TO check time of day, update average and save to DB
        if GPIO.input(PIR) == True:
            print 'PIR event detected'
            GPIO.output(LED, GPIO.HIGH)
            checkTiming()
    except KeyboardInterrupt:
        pass   

def checkTiming():
    dateToday = datetime.datetime.now().strftime('%Y-%m-%d')
    timeNow = datetime.datetime.now().time()
    morningCheck1 = datetime.time(12)
    tableFlag = 0
    
    if timeNow < morningCheck1:
        morningCheck2 = datetime.time(5, 30)
        print 'Time now is less than 12:00'
        print ''
        if timeNow < morningCheck2:
            #Create function to send alert
            print 'Time now is less than 5:30 - Abnormal Condition'
            print ''
            time.sleep(2)
            GPIO.output(LED, GPIO.LOW)
        else:
            print 'Time now is more than 5:30 - Proceed to check tables'
            print ''
            tableFlag = 1
            tbName = 'morningTime'
            checkDBEntry(tableFlag, tbName)
    else:
        print 'Time now is greater than 12:00'
        print ''
        afternoonCheck = datetime.time(17, 30)
        if timeNow < afternoonCheck:
            #Create function to send alert
            print 'Time is less than 17:30 - Abnormal condition'
            print ''
            time.sleep(2)
            GPIO.output(LED, GPIO.LOW)
        else:
            print 'Time now is more than 17:30 - Proceed to check tables'
            print ''
            tableFlag = 2
            tbName = 'eveningTime'
            checkDBEntry(tableFlag, tbName)
        
def checkDBEntry(flag, name):
    dateToday = datetime.datetime.now().strftime('%Y%m%d')
    codeState = 0
    with lite.connect('sm.sql') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM "+ name +" WHERE date_record = " + dateToday)
        row = len(cur.fetchall())
        if row > 0:
            print 'PIR Activity For Current Hour already recorded'
            #for test only
            #codeState = 1 # test only set to one, otherwise delete and pass
            time.sleep(2)
            GPIO.output(LED, GPIO.LOW)
        else:
            print 'No recorded activity for current hour. Proceed to store data...'
            codeState = 1
    
    if codeState == 1:
        codeState = 0
        recordActivity(flag, name)


def recordActivity(flag, name):
    if flag == 1:
        tableName = 'morningTime'
    else:
        talbeName = 'eveningTime'
        
    with lite.connect('sm.sql') as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO "+ name +" (date_record, time_record) VALUES ("+datetime.datetime.now().strftime('%Y%m%d')+", "+datetime.datetime.now().strftime('%H%M')+")")
        print 'PIR evening activity recorded'
        print ''
        codeState = 1
    
    if codeState == 1:
        codeState = 0
        calculateAverage(flag, name)


def calculateAverage(flag, name):
    timeNow = datetime.datetime.now().strftime('%H%M')
    total = 0
    if flag == 1:
        status = 'AM'
    else:
        status = 'PM'
    
    with lite.connect('sm.sql') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + name)
        totalCount = len(cur.fetchall())
        print 'Total Count Value is'
        print totalCount
        print ''
        if totalCount == 0:
            print 'First entry in average database'
            print ''
            with lite.connect('sm.sql') as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO averageTime (time_record, timeFlag) VALUES (?, ?)", (timeNow, status,))
                time.sleep(2)
                GPIO.output(LED, GPIO.LOW)
        else :
            print 'Read all values and calculate average'
            print ''
            with lite.connect('sm.sql') as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM " + name)
                for items in cur:
                    tmp = int(items[1])
                    total = total + tmp
            
            print 'total count is :'
            print totalCount
            averageTime = total / totalCount
            print 'New average time is : '
            print averageTime
            print ''
            #update entry in database with averageTime
            with lite.connect('sm.sql') as conn:
                cur = conn.cursor()
                cur.execute("UPDATE averageTime SET time_record = ? WHERE timeFlag = ?", (averageTime, status))
                time.sleep(2)
                GPIO.output(LED, GPIO.LOW)


def getTemperature():
    tempfile = open("/sys/bus/w1/devices/28-00000449fa06/w1_slave")
    filetext = tempfile.read()
    tempfile.close()
    tempdata = filetext.split("\n")[1].split(" ")[9]
    temperature = float(tempdata[2:])
    temperature = temperature / 1000
    print 'Current temperature is ' + str(temperature)
    
homeSystem.createTables()
GPIO.add_event_detect(PIR, GPIO.RISING, callback=checkPIRSensor)
print ''
print 'Sensor activity'
print '-'
print 'Crtl-C to exit'
print ''
        
def main():
    GPIO.output(LED, GPIO.LOW)
    print 'Start of Main Function - PIR & Temp Check'
    getTemperature()
    #eventDetectPIR()
    #call function to get Temperature
   
homeSystem.runLoop(main)