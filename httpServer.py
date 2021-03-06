#!/usr/bin/python
from flask import Flask, render_template, request, jsonify
from functools import wraps, update_wrapper
import zmq
import time
import moduleSkull
from config import *


class httpmodule(moduleSkull.module):
	def __init__(self):
		port=servers['zmqhttpCmdPort']
		hubport=servers['zmqEngineCmdPort']
		super(httpmodule,self).__init__('httpview',port,hubport)
		CMDs={ 
		}
		self.register()

	def end(self,arg=''):
		#shutdown_server()
		super(httpmodule,self).end()
		exit(0)

module=httpmodule()

app = Flask(__name__)
app.debug = False

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

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


