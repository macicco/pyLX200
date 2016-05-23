#!/usr/bin/python

import pigpio
import time
if __name__ == '__main__':
	pi=pigpio.pi("cronostamper")
	pi.set_mode(12, pigpio.OUTPUT)
	pi.hardware_PWM(12,1,500000)
	for i in range(1,2000):
		t1 = pi.get_current_tick()
		pi.hardware_PWM(12,i*1,500000)
		pi.get_PWM_dutycycle(12)
		t2 = pi.get_current_tick()
		print i,pigpio.tickDiff(t1,t2)
		time.sleep(0.00050)
	print pi.get_hardware_revision()
