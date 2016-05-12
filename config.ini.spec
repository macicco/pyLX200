[gear]
microstep = integer(1,32)
motorStepsRevolution = integer()
corona = float()
pinion = float()
reducer = float()


[engine]
maxPPS = integer(max=2048)


[here]
lat = float()
temp = float()
lon = float()
elev = float()
horizon = string()

[servers]
camera = string()
tleurl = string()
socketPort = integer()
httpPort = integer()
zmqCmdPort = integer()
socketsPort = integer()
zmqStreamPort = integer()
