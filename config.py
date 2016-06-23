#!/usr/bin/python
import json
import threading
import ConfigParser
from configobj import ConfigObj
from validate import Validator


def saveConfig():
	#TBD
	Config = ConfigObj()
	Config.filename="config.ini"

	#configuration options
	gear={}
	gear['maxPPS']=1024
	gear['motorStepsRevolution']=200
	gear['microstep']=32
	gear['corona']=30
	gear['pinion']=300

	Config['gear']=gear

	here={}
	here['lat']="40.440154"
	here['lon']="-3.668747"
	here['horizon']="10:00:00"
	here['elev']=700
	here['temp']=25e0
	Config['observer']=here

	servers={}
	servers['tleurl']="http://www.idb.com.au/files/TLE_DATA/ALL_TLE.ZIP"
	servers['zmqStreamPort'] = 7556
	servers['zmqCmdPort'] = 7557
	servers['socketsPort'] = 7999
	servers['httpPort']= 7000
	Config['servers']=servers

	Config.write()



#Ancillary functions

def mogrify(topic, msg):
    """ json encode the message and prepend the topic """
    return topic + ' ' + json.dumps(msg)

def demogrify(topicmsg):
    """ Inverse of mogrify() """
    json0 = topicmsg.find('{')
    topic = topicmsg[0:json0].strip()
    msg = json.loads(topicmsg[json0:])
    return topic, msg 

def threaded(fn):
    def wrapper(*args, **kwargs):
        t1=threading.Thread(target=fn, args=args, kwargs=kwargs)
	t1.start()
	return t1
    return wrapper

def group(lst, n):
  for i in range(0, len(lst), n):
    val = lst[i:i+n]
    if len(val) == n:
      yield tuple(val)


configFile="config.ini"
configFileSpec="config.ini.spec"
Config = ConfigObj(configFile,configspec=configFileSpec)
val=Validator()
test = Config.validate(val)
if test == True:
    print 'Config OK'
else:
    print 'Config wrong!!!'
    print 'Check that '+configFile+" match the rules in "+ configFileSpec
    exit(1)
	
gear=Config['gear']
here=Config['here']
servers=Config['servers']
engine=Config['engine']
'''
print here
print gear
print servers
print engine
'''






