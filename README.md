__pyLX200__
========

Introduction
------------

A telescope controller using python and a raspberry pi.

Arrow project is a telescope motor controller using a  raspberry. It has several advance features such satellite tracking (TLE) and smooth movements. It also has several interfaces like http, TCP/IP lx200, zmq.

https://youtu.be/HGe5Pjcod7E

This video shows the first stepper test showing the  syncronize RA axis motor movements.

The raspberry is  commanded from a Stellarium software. You can see the raspberry, an easydriver, the stepper and arduino. The last one only is used as power supply for the motor.

The sequence of commands show:

.- Regular goto capabilites
.- Sequence of coords, in this case the main stars in the zodiac costellations. Each 6 seconds a new coord is sent. It show fluent movements when changing the target coord on the way.
.- Satellite tracket (ISS in this case) . A module that track satellites using its TLE.

Nacho Mas - Abril 2016


