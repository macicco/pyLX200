DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Starting..."
$DIR/stop.sh
nohup $DIR/engine.py >/dev/null &
nohup $DIR/LX200.py >/dev/null &
nohup $DIR/httpServer.py >/dev/null &
sleep 1
socat TCP:localhost:7666,reuseaddr pty,link=/tmp/lx200
