#!/usr/bin/python

import pigpio
import time
if __name__ == '__main__':
	pi=pigpio.pi("cronostamper")
	pi.set_mode(13, pigpio.OUTPUT)
	for i in range(100):
		t1 = pi.get_current_tick()
		pi.hardware_PWM(13,i*1,500000)
		t2 = pi.get_current_tick()
		print pigpio.tickDiff(t1,t2)
		time.sleep(0.050)
	print pi.get_hardware_revision()
