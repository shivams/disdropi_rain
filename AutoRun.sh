#!/bin/sh

cd '/home/pi/Desktop/DisdroPi_Rain/'

lxterminal --command 'python Read_ADC.py'
lxterminal --command 'python Read_Disdro.py'
