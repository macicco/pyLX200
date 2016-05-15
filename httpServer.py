#!/usr/bin/python
from flask import Flask, render_template, request, jsonify
from functools import wraps, update_wrapper
import zmq
import time
from config import *

app = Flask(__name__)
last={}

@app.route('/')
def index():
    return render_template('arrow.html', camera='')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/values.json')
def gps_json():
	return jsonify(lastValue())

@app.route('/getObserver')
def getObserver():
	socketCmd.send('@getObserver')
	reply=socketCmd.recv()
	return reply

@app.route('/getGear')
def getGear():
	socketCmd.send('@getGear')
	reply=socketCmd.recv()
	return reply

@app.route('/getConfig')
def getConfig():
	return jsonify(Config)

def lastValue():
	global last
	try:
		m= socketStream.recv(flags=zmq.NOBLOCK)
		topic, msg  = demogrify(m)
		last=msg
	except:
		msg=last
    	return msg

if __name__ == '__main__':
	context = zmq.Context()
	socketStream = context.socket(zmq.SUB)
	#CONFLATE: get only one message (do not work with the stock version of zmq, works from ver 4.1.4)
	socketStream.setsockopt(zmq.CONFLATE, 1)
	socketStream.connect ("tcp://localhost:%s" % servers['zmqStreamPort'])
	socketStream.setsockopt(zmq.SUBSCRIBE, 'values')

	socketCmd = context.socket(zmq.REQ)
	socketCmd.connect ("tcp://localhost:%s" % servers['zmqEngineCmdPort'])



	#main loop
	app.run(host='0.0.0.0',port=servers['httpPort'],debug=False)
