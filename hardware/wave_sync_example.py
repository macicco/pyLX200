#!/usr/bin/python

import math
import time,datetime
import pigpio
raspberry='192.168.1.11'

STEP_PIN=13

pi=pigpio.pi(raspberry)
pi.wave_clear()
t=50
steps=1000


def generateW():
   wave=[]
   for i in range(steps):
	wave.append(pigpio.pulse(0, 1<<STEP_PIN, t))
	wave.append(pigpio.pulse(1<<STEP_PIN, 0, t))
   pi.wave_add_generic(wave)

generateW()
wid = pi.wave_create() 
pi.wave_send_once(wid)
old_wid=wid
while True:

	generateW()
	wid = pi.wave_create() 
	pi.wave_send_using_mode(wid, pigpio.WAVE_MODE_ONE_SHOT_SYNC)
	#pi.wave_send_once(wid)

	if old_wid !=-9999:
		#print "Deleting:",pi.wave_tx_at(),old_wid,wid
		while pi.wave_tx_at()==old_wid:
			time.sleep(0.00000001)
		pi.wave_delete(old_wid)



	old_wid=wid
