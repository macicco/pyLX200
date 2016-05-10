#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
#NACHO MAS
import ephem,urllib
from config import *
import zipfile

#Code to get TLE and Comet (format Xephem) from Minor Planet Center

class TLEhandler:
	def __init__(self,url="http://www.celestrak.com/NORAD/elements/geo.txt"):
		#ISS http://celestrak.com/NORAD/elements/stations.txt
		f='ALL_TLE.TXT'
		url="http://celestrak.com/NORAD/elements/stations.txt"
		#url="http://celestrak.com/NORAD/elements/geo.txt"
		self.data=self.readTLEurl(url)
		#self.data=self.readTLEfile(f)


	#read TLE file
	def readTLEurl(self,url):
		f=urllib.urlopen(url)
		data=f.read().split('\r\n')
		return data

	def readTLEfile(self,filename):
		with open(filename) as f:	
			data=f.read().split('\r\n')
		return data

	#return elements that match
	def TLE(self,sat):
		data=group(self.data,3)
		element=filter(lambda x:x[0].find(sat)!=-1, data)
		element=element[0]
		return ephem.readtle(element[0],element[1],element[2])
		





if __name__=='__main__':
	here = ephem.Observer()
	here.lat="40.440154"
	here.lon="-3.668747"
	print "COORD:", here.lat,here.lon
	here.horizon="00:00:00"
	here.elev = 700
	here.temp = 25e0
	here.compute_pressure()


	i=TLEhandler()
	iss=i.TLE('ISS')
	iss=i.TLE('METEOSAT 7')
	iss.compute(here)
	print iss.ra,iss.dec



