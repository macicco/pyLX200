#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import pyfits
from pylab import *
import commands,os, sys
import getpass
import sys
import telnetlib
import ephem

def jplHorizons(body,date_star,date_end,interval,lon,lat,height):
	HOST = "horizons.jpl.nasa.gov"
	PORT = "6775"
	tn = telnetlib.Telnet(HOST,PORT)
	tn.read_until("Horizons>")
	tn.write(body+"\n")
	#tn.write("yes\n")
	tn.write("E\n")
	tn.write("o\n")
	tn.write("coord\n")
	tn.write("g\n")
	tn.write(lon+","+lat+","+height+"\n")
	#tn.write("y\n")
	tn.write(date_star+"\n")
	tn.write(date_end+"\n")
	tn.write(interval+"\n")
	tn.write("n\n")
	tn.write("1,2,9,29\n")
	tn.write("J2000\n")
	tn.write("\n")
	tn.write("CAL\n")
	tn.write("SEC\n")
	tn.write("\n")
	tn.write("YES\n")
	tn.write("Refracted\n")
	tn.write("KM\n")
	tn.write("\n")
	tn.write("\n")
	tn.write("\n")
	tn.write("\n")
	tn.write("\n")
	tn.write("\n")
	tn.write("\n")
	tn.write("Y\n")
	tn.read_until("*******************************************************************************")
	tn.read_until("*******************************************************************************")
	tn.write("\n")
	tn.read_until("*******************************************************************************")
	result=tn.read_until("Select...")

	#print result
	tn.write("exit\n")
	i=0
	while result[i:i+5]!='$$SOE':
		i=i+1
	j=i
	while result[j:j+5]!='$$EOE':
		j=j+1
	dummy=result[i+7:j-2]	
	obs=[['Date','Light','moon','RAJ2000','DEJ2000','RAJ2000_APARENT','DEJ2000_APARENT','T-mag','N-mag','Cnst']]
	for line in dummy.split('\r\n'):
		l=line.split(',')
		d = l[0].replace('-','/')
		light=l[1]
		moon=l[2]
		ra= l[3].replace(' ',':')
		dec= l[4].replace(' ',':')
		ra_= l[5].replace(' ',':')
		dec_= l[6].replace(' ',':')
		try:
			Tmag=float(l[7])
		except:
			Tmag=999
		try:
			Nmag=float(l[8])
		except:
			Nmag=999

		Const=l[9]
		ll=[d,light,moon,ra,dec,ra_,dec_,Tmag,Nmag,Const]
		#print ll
		obs.append(ll)
	return obs


	

if __name__=='__main__':
	#result=jplHorizons("2012 DA14","2013-02-15T07:30:00","2013-02-16T01:00:00","1m","-3.679537","40.437827","600")
	#result=jplHorizons("ISS","2016-12-03T00:00:00","2016-12-03T23:59:00","1m","-16.604608","28.244542","20")
	#result=jplHorizons("2011 PY1","2011-08-17T20:50:06","2011-08-18T02:56:10.861","10m","-3.679537","40.437827","600")
	#result=jplHorizons("285263","2016-11-31T21:00:00","2016-11-01T23:00:00","10m","-3.679537","40.437827","600")
	#ISS ID=-125544
	result=jplHorizons("-125544","2016-12-04T18:00:00","2016-12-03T19:00:00","1m","-3.679537","40.437827","600")
	for line in result:
		print line[0],',',line[3],',',line[4]


