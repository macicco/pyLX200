#!/usr/bin/python

import pigpio

'''
Just disable ENABLE_PIN.
'''

TIMESLOT=100000

pi=pigpio.pi('192.168.1.11')
pi.write(21,True)
pi.write(8,True)


