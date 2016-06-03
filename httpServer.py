#!/usr/bin/python
from flask import Flask, render_template, request, jsonify
from flask.ext.classy import FlaskView
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


class httpview(FlaskView):
	def __init__(self):
		super(httpview,self).__init__()
		self.module=httpmodule()

	def _index():
	    return render_template('arrow.html', camera='')

	def _help():
	    return render_template('help.html')

	def _value():
		self.modulesocketHUBCmd.send('@values')
		reply=self.module.socketHUBCmd.recv()
		topic,msg=demogrify(reply)
		#print topic,msg
		return jsonify(msg)

	def getObserver():
		self.module.send('@getObserver')
		reply=self.module.recv()
		return reply

	def getGear():
		self.module.send('@getGear')
		reply=self.module.recv()
		return reply

	def getConfig():
		return jsonify(Config)

app = Flask(__name__)
httpview.register(app)

if __name__ == '__main__':
    app.run()
