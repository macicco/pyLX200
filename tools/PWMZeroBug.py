#!/usr/bin/python

import pigpio
if __name__ == '__main__':
	pi=pigpio.pi("cronostamper")
	pi.set_mode(13, pigpio.OUTPUT)
	pi.set_PWM_frequency(13,0)
	for f in [142,2323,0,4320,1,0]:
		if f==0:
			pi.hardware_PWM(13,1,0)
		else:
			pi.hardware_PWM(13,f,500000)
		print "Hardware PWM/get_PWM_frequency()",f,"/",pi.get_PWM_frequency(13),pi.get_PWM_dutycycle(13)

