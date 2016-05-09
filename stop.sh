kill -9 `ps -ef | grep engine.py | grep -v grep | awk '{print $2}'`
kill -9 `ps -ef | grep LX200.py | grep -v grep | awk '{print $2}'`
kill -9 `ps -ef | grep httpServer.py | grep -v grep | awk '{print $2}'`
killall -9 socat
