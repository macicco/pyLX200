#!/usr/bin/python
import pygame
import sys,os
import time
import moduleSkull
from config import *

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.joystick.init()


class stick(moduleSkull.module):
   def __init__(self):
		port=servers['zmqJoystickCmdPort']
		hubport=servers['zmqEngineCmdPort']
		super(stick,self).__init__('joystick',port,hubport)
		CMDs={ 
		}
		self.register()

   def run(self):
	vRA=0
	vDEC=0
	deadZone = 0.1 # make a wide deadzone
	m1 = 0 # motor 1 (1 = forward / 2 = backwards)
	try:
		j = pygame.joystick.Joystick(0) # create a joystick instance
		j.init() # init instance
		print 'Enabled joystick: ' + j.get_name()
	except pygame.error:
		print 'no joystick found.'

	while 1:
	   for e in pygame.event.get(): # iterate over event stack
	      if e.type == pygame.JOYAXISMOTION: # Read Analog Joystick Axis
        	 x1 , y1 = j.get_axis(0), j.get_axis(1) 

	         print x1
	         print y1

	         if x1 < -1 * deadZone:
	             print 'Left Joystick 1'

	         if x1 > deadZone:
	             print 'Right Joystick 1'

	         if y1 <= deadZone and y1 >= -1 * deadZone:
	             m1 = 0 # Dont go forward or backwards

	         if y1 < -1 * deadZone:
	             print 'Up Joystick 1'
	             m1 = 1 # go forward
	             print m1
             
	         if y1 > deadZone:
	             print 'Down Joystick 1'
	             m1 = 2 # go forward
	             print m1

 
	      if e.type == pygame.JOYBUTTONDOWN:
	            print("Joystick button pressed.")
	      if e.type == pygame.JOYBUTTONUP:
	            print("Joystick button released.")
	      vRA=vRA-x1/100
	      vDEC=vDEC+y1/100
	   self.sendTrackSpeed(vRA,vDEC)

   def sendTrackSpeed(self,vRA,vDEC):
	self.socketHUBCmd.send('@setTrackSpeed '+str(vRA)+' '+str(vDEC))
	reply=self.socketHUBCmd.recv()

s=stick()
try:
	s.run()
except:
	s.end()

