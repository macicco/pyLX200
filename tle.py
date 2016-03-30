#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#NACHO MAS
import ephem,urllib
from pylab import *

def group(lst, n):
  for i in range(0, len(lst), n):
    val = lst[i:i+n]
    if len(val) == n:
      yield tuple(val)

#Code to get TLE and Comet (format Xephem) from Minor Planet Center

class TLEhandler:
	def __init__(self):
		self.setObserver()

	#read TLE file
	def readTLEfile(self,url):
		url=url
		f=urllib.urlopen(url)
		data=f.read().split('\r\n')
		s=group(data,3)
		return s

	#return elements that match
	def TLE(self,url,name):
		data=self.readTLEfile(url)
		element=filter(lambda x:x[0].find(name)!=-1, data)
		element=element[0]
		return ephem.readtle(element[0],element[1],element[2])
		

	def ISS(self):	
	#ISS http://celestrak.com/NORAD/elements/stations.txt
		url="http://celestrak.com/NORAD/elements/stations.txt"
		return self.TLE(url,'ISS')

	def setObserver(self):
		here = ephem.Observer()
		here.lat="40.440154"
		here.lon="-3.668747"
		print "COORD:", here.lat,here.lon
		here.horizon="00:00:00"
		here.elev = 700
		here.temp = 25e0
		here.compute_pressure()
		self.observer=here

	def path(self,date=ephem.now(),interval=10,step=20):
		obs=self.observer
		iss=self.ISS()
		obs.date=date
		pos=[]
		for d in range(0,interval):
			obs.date=obs.date+ephem.second*step
			iss.compute(obs)
			#l=list((ephem.localtime(obs.date),iss.ra*180/pi,iss.dec*180/pi))
			l=list((obs.date,iss.ra,iss.dec))
			pos.append(l)
		return pos


if __name__=='__main__':
	i=TLEhandler()
	iss=i.ISS()
	iss.compute()
	print iss.ra,iss.dec
	print i.path()


