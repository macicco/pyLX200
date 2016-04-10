#!/bin/sh
gnuplot << EOF
h=1200
set term png size h*4/3,h
set output "RA.png"
set key autotitle columnhead
set y2tics
set autoscale y2
set title "RA Axis"
plot "RA.log" u 1:2 w steps,"RA.log" u 1:3 w steps,"RA.log" u 1:4 w lines,"RA.log" u 1:5 w lines,"RA.log" u 1:6 w lines lw 2,"RA.log" u 1:7 w lines lw 2,"RA.log" u 1:8 w lines lw 2,"RA.log" u 1:9 w lines lw 2   ,"DEC.log" u 1:10  axes x2y2
set output "DEC.png"
set title "DEC Axis"
set key autotitle columnhead
plot "DEC.log" u 1:2 w steps,"DEC.log" u 1:3 w steps,"DEC.log" u 1:4 w lines,"DEC.log" u 1:5 w lines,"DEC.log" u 1:6 w lines lw 2,"DEC.log" u 1:7 w lines lw 2,"DEC.log" u 1:8 w lines lw 2,"DEC.log" u 1:9 w lines lw 2 ,"DEC.log" u 1:10  axes x2y2

EOF
