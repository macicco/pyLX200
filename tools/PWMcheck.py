#!/usr/bin/python

import pigpio
import time
if __name__ == '__main__':
  dire=0
  while True:
	pi=pigpio.pi("cronostamper")
	pi.set_mode(12, pigpio.OUTPUT)
	f=2000.
	s=382.
	n=.25
	pi.hardware_PWM(12,f,500000)
	time.sleep(s*n/f)
	pi.hardware_PWM(12,f,0)
	if dire==0:
		dire=1
	else:
		dire=0
	pi.write(4, dire>0)
	time.sleep(1)
