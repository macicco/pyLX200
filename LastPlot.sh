#!/bin/sh
headersRA=`head -1 RA.log`
headersDEC=`head -1 DEC.log`
lastRA=`tail -100 RA.log`
lastDEC=`tail -100 DEC.log`
echo $headersRA $lastRA |sed 's/\r/\n/g' |sed 's/^\ //g'  >lastRA.log
echo $headersDEC $lastDEC |sed 's/\r/\n/g' |sed 's/^\ //g' >lastDEC.log
gnuplot << EOF
h=1200
set term png size h*4/3,h
set output "RA.png"
set key autotitle columnhead
set y2tics
set autoscale y2
set title "RA Axis"
plot "lastRA.log" u 1:5 w lines,"lastRA.log" u 1:6 w points lw 2,"lastRA.log" u 1:9 w po lw 2  
set output "DEC.png"
set title "DEC Axis"
set key autotitle columnhead
plot "lastDEC.log" u 1:5 w lines,"lastDEC.log" u 1:6 w po lw 2,"lastDEC.log" u 1:9 w po lw 2

EOF
