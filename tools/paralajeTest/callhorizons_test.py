#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import callhorizons

if __name__=='__main__':
	dq = callhorizons.query('-125544', smallbody=False)
	dq.set_epochrange('2016-12-04 18:40', '2016-12-04 19:10', '1m')
	po=dq.get_ephemerides('J20')
	#print dq.fields
	#print dq.query
	print "DATE,RA,DEC"
	for i in range(po):
		print dq['datetime'][i],",",dq['RA'][i],",",dq['DEC'][i],dq['delta'][i]
