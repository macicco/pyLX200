#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
'''
LX200 command set
'''
import ephem
import time,datetime
import threading
import ramps
import math

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class lx200conductor():
	def __init__(self):
		print "Conductor create"
		self.CMDs={ \
		":info": self.cmd_info,  \
  		":FirmWareDate": self.cmd_firware_date,  \
  		":GVF": self.cmd_firware_ver,  \
  		":V": self.cmd_firware_ver,  \
  		":GVD": self.cmd_firware_date,  \
  		":GC": self.cmd_getLocalDate,  \
  		":GL": self.cmd_getLocalTime,  \
  		":Sr": self.cmd_setTargetRA,  \
  		":Sd": self.cmd_setTargetDEC,  \
  		":Gr": self.cmd_getTargetRA,  \
  		":Gd": self.cmd_getTargetDEC,  \
  		":GR": self.cmd_getTelescopeRA,  \
  		":GD": self.cmd_getTelescopeDEC,  \
  		":RS": self.cmd_setMaxSlewRate,  \
  		":Me": self.cmd_pulseE,  \
  		":Mw": self.cmd_pulseW,  \
  		":Mn": self.cmd_pulseN,  \
  		":Ms": self.cmd_pulseS,  \
  		":CM": self.cmd_dummy
		}
		self.targetRA=0		
		self.targetDEC=0	
		self.RA=0		
		self.DEC=0
		self.RUN=True
		self.pulseStep=ephem.degrees('00:01:00')
		self.m=ramps.mount(ephem.degrees('20:00:00'),ephem.degrees('01:00:00'))
		self.run()	

    	def end(self):
        	print "conductor ending.."
		self.RUN=False
		self.m.end()

		
	@threaded
	def run(self):
		print "Starting motors."
	  	while self.RUN:
			self.m.slew(self.targetRA,self.targetDEC)
			time.sleep(0.25)
			#self.m.coords()
			self.DEC=ephem.degrees(self.m.axis2.beta)
			self.RA=ephem.hours(self.m.axis1.beta)
		self.end()
		print "MOTORS STOPPED"



	def cmd(self,cmd):
		print cmd
                for c in self.CMDs.keys():
			l=len(c)
			if (cmd[:l]==c):
				arg=cmd[l:].strip()
				#print "K",c,"KK",cmd,"KKK",arg
				return self.CMDs[c](arg)
				break

		return self.cmd_dummy(cmd)



	def cmd_dummy(self,arg):
		return arg,"#"

	def cmd_info(self,arg):
		return "pyLX200 driver#"

	def cmd_firware_date(self,arg):
		return "01/02/2016#"

	def cmd_firware_ver(self,arg):
		return "LX200 Master. Python mount controler. Ver 0.1#"

	def cmd_getLocalDate(self,arg):
		return time.strftime("%m/%d/%y")+'#'
	
	def cmd_getLocalTime(self,arg):
		return time.strftime("%H:%M:%S")+'#'

	def cmd_getTargetRA(self,arg):
		return self.targetRA

	def cmd_getTargetDEC(self,arg):
		return self.targetDEC

	def cmd_setTargetRA(self,arg):
		self.targetRA=ephem.hours(arg)
		#return self.targetRA
		
	def cmd_setTargetDEC(self,arg):
		self.targetDEC=ephem.degrees(arg)
		#return self.targetDEC

	def cmd_getTelescopeRA(self,arg):
		data=str(self.RA)
		d=data[:data.index(".")]
		return d+'#'

	def cmd_getTelescopeDEC(self,arg):
		data=str(self.DEC)
		D,M,S=data.split(':')
		D=int(D)
		M=int(M)
		S=round(float(S))
		#print D,M,S 
		d="%+02d*%02d’%02d"  % (D,M,S)
		d="%+02d*%02d"  % (D,M)
		return d+'#'

    	def cmd_pulseE(self,arg):
		self.targetRA=self.targetRA+self.pulseStep

    	def cmd_pulseW(self,arg):
		self.targetRA=self.targetRA-self.pulseStep

    	def cmd_pulseN(self,arg):
		self.targetDEC=self.targetDEC+self.pulseStep

    	def cmd_pulseS(self,arg):
		self.targetDEC=self.targetDEC-self.pulseStep

	def cmd_setMaxSlewRate(self,arg):
		return

if __name__ == '__main__':
	c=lx200conductor()
	c.cmd(':CM')
	c.cmd(':info')

'''
  		":GVN": self.cmd_firware_number,  \
  		":GVP": self.cmd_firware_product,  \
  		":GVT": self.cmd_firware_time,  \

  		":GM": self.cmd_getSite1Name,  \
  		":Sa": self.cmd_dummy,  \
  		":Sz": self.cmd_dummy,  \

  		":Sg": self.cmd_setSiteLongitude,  \
  		":St": self.cmd_setSiteLatitude,  \
  		":SL": self.cmd_setLocalTime,  \
  		":SC": self.cmd_setLocalDate,  \
  		":SG": self.cmd_dummy,  \
  		":GA": self.cmd_dummy,  \
  		":GZ": self.cmd_dummy,  \



  		":Gg": self.cmd_getSiteLongitude,  \
  		":Gt": self.cmd_getSiteLatitude,  \
  		":Gc": self.cmd_getClockFormat,  \


  		":GG": self.cmd_dummy,  \
  		":MA": self.cmd_dummy,  \
  		":Me": self.cmd_dummy,  \
  		":Mn": self.cmd_dummy,  \
  		":Ms": self.cmd_dummy,  \
  		":Mw": self.cmd_dummy,  \
  		":MS": self.cmd_slew,  \
  		":Q": self.cmd_abortMotion,  \

'''
