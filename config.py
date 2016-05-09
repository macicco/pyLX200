#!/usr/bin/python
import json
import threading

#configuration options
gear={}
gear['maxPPS']=1000
gear['motorStepsRevolution']=200
gear['microstep']=32
gear['corona']=500
gear['pinion']=500

here={}
here['lat']="40.440154"
here['lon']="-3.668747"
here['horizon']=10
here['elev']=700
here['temp']=25e0

tleurl="http://www.idb.com.au/files/TLE_DATA/ALL_TLE.ZIP"

camera="KK"

zmqStreamPort = 5556
zmqCmdPort = 5557

socketsPort = 9999
httpPort= 5000



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
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

def group(lst, n):
  for i in range(0, len(lst), n):
    val = lst[i:i+n]
    if len(val) == n:
      yield tuple(val)


