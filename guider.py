#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
'''
Module Skeleton virtual class
'''

import moduleSkull

class guidermodule(moduleSkull.module):
	def cmd_guide(self,arg):
		return "GUIDE"

	def cmd_resolve(self,arg):
		return "RESOLVE"

	def __init__(self,name,port,hubport):
		super(guidermodule,self).__init__(name,port,hubport)
		CMDs={ 
		":resolve": self.cmd_resolve, \
		":guide": self.cmd_guide \
		}
		self.addCMDs(CMDs)
		self.register()


if __name__ == '__main__':
	port=7770
	guiderport=7772
  	g=guidermodule('guider',guiderport,port)
	g.run()
	exit()


