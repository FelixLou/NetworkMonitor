#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import sqlite3
import speedtest
import sys
import random

dbname='/app/db/network.db'
sampleFreq = 60 # time in seconds

# get data from DHT sensor
def getNetworkSpeed():	
	
	speedtester = speedtest.Speedtest()
	speedtester.get_best_server()

	return speedtester.upload(), speedtester.download()

# log sensor data on database
def logData (upload, download):
	conn=sqlite3.connect(dbname, check_same_thread=False)
	cur = conn.cursor() 
	cur.execute("CREATE TABLE IF NOT EXISTS network_speed(timestamp DATETIME, upload NUMERIC, download NUMERIC)")
	
	cur.execute("INSERT INTO network_speed values(datetime('now'), (?), (?))", (round(upload), round(download)))
	print("Inserted to db")
	conn.commit()
	conn.close()

# main function
def main():
	while True:
		upload, download = getNetworkSpeed()
		# upload, download = random.randint(1,20), random.randint(1,101)
		print("Upload speed is {}, download speed is {} at time {}".format(upload, download, datetime.datetime.now()))
		logData (upload, download)
		time.sleep(sampleFreq)

# ------------ Execute program 
main()
