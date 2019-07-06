# Program for reading ADC values and storing into SQL database

import time
from datetime import datetime

# Import SQL Class from Voltage_db.py
from Voltage_db import SQL

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


# Software SPI configuration:
        #Pin connections from MCP3004:
        #    - CLK  = 23
        #    - MISO/DOUT = 19
        #    - MOSI/DIN = 21
        #    - CS   = 24
CLK  = 11
MISO = 10
MOSI = 9
CS   = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Object for SQL class
db = SQL()

print('Starting to read ADC values...')

# Print nice channel column headers.
print('| {0:>5} | {1:>5} | {2:>5} | {3:>5} |'.format(*range(4)))
print('-' * 33)

# Main program loop.
while True:
    # Read all the ADC channel values in a list.
	values = [0]*4
	values_vol = [0.0]*4
	# Loop to all available channels of ADC
	for i in range(4):
        # The read_adc function will get the value of the specified channel (0-3).
		values[i] = mcp.read_adc(i)
		# Convert read RAW values to perticular voltages with Vref=Vcc
		values_vol[i] = round( ( (float(values[i]) * 5.14) / 1023), 3)
		# Multiply each channel with it's specific scale factor
		if i == 0:
			values_vol[i] = values_vol[i] * 3
		if i == 1:
		 	values_vol[i] = values_vol[i] * 5
		if i == 2:
			values_vol[i] = values_vol[i] * 1
			
	# Print the ADC values.
	print('| {0:>5} | {1:>5} | {2:>5} | {3:>5} |'.format(*values_vol))
	# Inserting values to SQL database
	db.insert(str(datetime.now()),values_vol)
	# Pause for half a second.
	time.sleep(10)
