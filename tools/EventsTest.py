#!/usr/bin/python
#USE WITH THE ONLY AIM OF KNOWING THE
#callback capabilities
import pigpio
import time

motorBeta=0
motorBetaFalling=0

def FallingStepCounter(gpio, level, tick):
	global motorBetaFalling
	motorBetaFalling=motorBetaFalling+1

def RisingStepCounter(gpio, level, tick):
	global motorBeta
	motorBeta=motorBeta+1

if __name__ == '__main__':
	global motorBeta,motorBetaFalling
	pi=pigpio.pi('192.168.1.11')
	PIN=13
	pi.set_mode(PIN, pigpio.OUTPUT)
	pi.callback(PIN, pigpio.RISING_EDGE, RisingStepCounter)
	cb2 = pi.callback(PIN, pigpio.FALLING_EDGE, FallingStepCounter)
	t=0.01
	for f in range(10,100000,100):
		pi.hardware_PWM(PIN,f,500000)
		time.sleep(t)
		print f,t*f,motorBeta,motorBetaFalling
		if abs(motorBeta-motorBetaFalling) >1:
			print "************** A L A R M **************"
			print "************ STEPS MISSING ************"
		motorBeta= 0
		motorBetaFalling= 0

