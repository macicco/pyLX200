#!/usr/bin/python
from flask import Flask, render_template, request, jsonify
from functools import wraps, update_wrapper
import zmq
import time
import moduleSkull
from config import *
import signal

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    module.end()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class httpmodule(moduleSkull.module):
	def __init__(self):
		port=servers['zmqhttpCmdPort']
		hubport=servers['zmqEngineCmdPort']
		super(httpmodule,self).__init__('httpview',port,hubport)
		CMDs={ 
		}
		self.register()


module=httpmodule()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('arrow.html', camera='')

@app.route("/help")
def help():
    return render_template('help.html')

@app.route("/values.json")
def value():
	module.socketHUBCmd.send('@values')
	reply=module.socketHUBCmd.recv()
	topic,msg=demogrify(reply)
	#print topic,msg
	return jsonify(msg)

@app.route("/getobserver")
def getObserver():
	module.socketHUBCmd.send('@getObserver')
	reply=module.socketHUBCmd.recv()
	return reply

@app.route("/getGear")
def getGear():
	print "kk"
	print module
	module.socketHUBCmd.send('@getGear')
	print "kkk"
	reply=module.socketHUBCmd.recv()
	print "kkkk"
	return reply

@app.route("/getconfig")
def getConfig():
	return jsonify(Config)





if __name__ == '__main__':
    app.run()


