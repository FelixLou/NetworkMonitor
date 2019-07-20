#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import time

from flask import Flask, render_template, send_file, make_response, request
app = Flask(__name__)

import sqlite3
conn=sqlite3.connect('/app/db/network.db', check_same_thread=False)
curs=conn.cursor()
curs.execute("CREATE TABLE IF NOT EXISTS network_speed(timestamp DATETIME, upload NUMERIC, download NUMERIC)")
mb = 1000000

# Retrieve LAST data from database
def getLastData():
	for row in curs.execute("SELECT * FROM network_speed ORDER BY timestamp DESC LIMIT 1"):
		time = str(row[0])
		upload = row[1]/mb
		download = row[2]/mb
	#conn.close()
	return time, upload, download

# Get 'x' samples of historical data
def getHistData (numSamples):
	curs.execute("SELECT * FROM network_speed ORDER BY timestamp DESC LIMIT "+str(numSamples))
	data = curs.fetchall()
	dates = []
	uploads = []
	downloads = []
	for row in reversed(data):
		dates.append(row[0])
		uploads.append(row[1]/mb)
		downloads.append(row[2]/mb)
		# uploads, downloads = testeData(uploads, downloads)
	return dates, uploads, downloads

# Test data for cleanning possible "out of range" values
# def testeData(uploads, downloads):
# 	n = len(uploads)
# 	for i in range(0, n-1):
# 		if (uploads[i] < -10 or uploads[i] >50):
# 			uploads[i] = uploads[i-2]
# 		if (downloads[i] < 0 or downloads[i] >100):
# 			downloads[i] = uploads[i-2]
# 	return uploads, downloads


# Get Max number of rows (table size)
def maxRowsTable():
	for row in curs.execute("select COUNT(upload) from  network_speed"):
		maxNumberRows=row[0]
	return maxNumberRows

# Get sample frequency in minutes
def freqSample():
	times, uploads, downloads = getHistData (2)
	fmt = '%Y-%m-%d %H:%M:%S'
	tstamp0 = datetime.strptime(times[0], fmt)
	tstamp1 = datetime.strptime(times[1], fmt)
	freq = tstamp1-tstamp0
	freq = int(round(freq.total_seconds()/60))
	return (freq)

# define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
        numSamples = 100

global freqSamples
freqSamples = freqSample()

global rangeTime
rangeTime = 100
				
		
# main route 
@app.route("/")
def index():
	time, upload, download = getLastData()
	networkData = {
	  'time'		: time,
      'upload'		: upload,
      'download'	: download,
      'freq'		: freqSamples,
      'rangeTime'	: rangeTime
	}
	return render_template('index.html', **networkData)


@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples 
    global freqSamples
    global rangeTime
    rangeTime = int (request.form['rangeTime'])
    if (rangeTime < freqSamples):
        rangeTime = freqSamples + 1
    numSamples = rangeTime//freqSamples
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    
    time, upload, download = getLastData()
    
    networkData = {
	  'time'		: time,
      'upload'		: upload,
      'download'	: download,
      'freq'		: freqSamples,
      'rangeTime'	: rangeTime
	}
    return render_template('index.html', **networkData)
	
	
@app.route('/plot/upload')
def plot_upload():
	times, uploads, downloads = getHistData(numSamples)
	ys = uploads
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("upload")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/download')
def plot_download():
	time.sleep(0.01)
	times, uploads, downloads = getHistData(numSamples)
	ys = downloads
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("download")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
	
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)


