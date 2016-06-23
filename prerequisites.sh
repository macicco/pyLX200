#!/bin/bash
sudo apt-get install git
sudo apt-get install python-pip
sudo pip install pyephem
sudo apt-get install python-zmq python-configobj python-pygame python-flask python-pyfits 
sudo apt-get install python-numpy python-scipy python-matplotlib
sudo apt-get install gnuplot socat

#install PIGPIO library
rm pigpio.zip
sudo rm -rf PIGPIO
wget abyz.co.uk/rpi/pigpio/pigpio.zip
unzip pigpio.zip
cd PIGPIO
make -j4
sudo make install
