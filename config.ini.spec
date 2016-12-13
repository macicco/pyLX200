[gear]
microstep = integer(1,32)
motorStepsRevolution = integer()
corona = float()
pinion = float()
reducer = float()


[engine]
maxPPSbase = integer(max=20480)
acceleration = string()
overhorizon = boolean()
go2rising = boolean()

[here]
lat = float()
temp = float()
lon = float()
elev = float()
horizon = string()

[servers]
tleurl = string()
socketPort = integer()
httpPort = integer()
zmqEngineCmdPort = integer()
zmqTrackerCmdPort = integer()
zmqJoystickCmdPort = integer()
zmqhttpCmdPort = integer()
pigpio=string()

