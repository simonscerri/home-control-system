import os
import sys
import time
import threading
import sqlite3 as lite

__running__ = False
INTERVAL = 3

def runLoop(func=None):
    global __running__
    __running__ = True
    if func != None:
        while __running__:
            func()
            time.sleep(INTERVAL)
            #GPIO.remove_event_detect(13)
            #GPIO.cleanup()
    else:
        while __running__:
            try:
                time.sleep(INTERVAL)
            except KeyboardInterrupt:
    
                print '\nExiting'

def createTables():
    # Create database table
    with lite.connect('sm.sql') as conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS morningTime(date_record date, time_record time)")
        cur.execute("CREATE TABLE IF NOT EXISTS eveningTime(date_record date, time_record time)")
        cur.execute("CREATE TABLE IF NOT EXISTS averageTime(time_record time, timeFlag varchar(2))")