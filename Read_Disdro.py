import sqlite3
import time
import datetime
import serial
import os
import dropCalculator
import sys

# Definitions:
BAUDRATE    = 9600
#PORT        = '/dev/ttyUSB0'  # Use this when Disdro is connected with USB
PORT        = '/dev/ttyS0'    # use this when Disdro is connected via Hardware Serial
DBNAME      = '/home/pi/Desktop/DisdroPi_Rain/DisdroPi_Rain.db'
TIMEOUT     = 1 # seconds

print ('This is Disdro ')

# SQLite3 Connection & Cursor definition
conn = sqlite3.connect(DBNAME)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS Rain_Data
            (Timestamp text,
             Bin_Index integer,
             Kinetic_Energy integer,
             Drop_Radius REAL,
             MM_equivalent REAL)''')

# function to write data to DataBase
def data_entry(Ke,Rs,mm,bin_val):
    ts = datetime.datetime.now()    #generates timestamp

    #formats accordingly to DB
    dbList = ((ts),             #Timestamp
              (bin_val),        #Bin Value
              (Ke),             #Energy
              (Rs),             #Drop radius
              (mm))             #Drop equivalent in terms of 'mm' of rain

    c.execute('''INSERT INTO Rain_Data VALUES(?,?,?,?,?)''', dbList)      # Inserting data
    conn.commit()                                                             # saving the inserted values

# Serial Conection
try:  # try to open serial port with ser as object
    
    ser           = serial.Serial()     # get serial instance
    ser.baudrate  = BAUDRATE            # configure the baudrate
    ser.port      = PORT                # set port information
    ser.timeout   = TIMEOUT             # set timeout to 1 seconds
    ser.stopbits  = serial.STOPBITS_TWO # configure stop bits
    time.sleep(2)                       # wait for some time
    ser.open()                          # open the port
    print('Serial port successfully opened')   # print ok
    
except: # cannot open serial port
    print('Failed to open Serial port')
    sys.exit()

# Turn the device into Kort mode (Automatic Send Short Data)
print('Starting the short mode')
dropCalculator.sendSerialCommand(ser,2)

# wait for 1 second before starting code
time.sleep(1)

try:  # MAIN LOOP
  drop_string = ''                                                        # initialize
  while True:
      ser_char = ser.read()                                               # reads single byte from serial
      if ser_char == b'':                                                 # skips null characters
          continue                                                        # restart the loop

      char = ser_char.decode('utf-8', errors='ignore')                    # converts in string, ignore errors
      drop_string += char                                                 # appends to drop_string

      if drop_string == 'ASON\r\n':                                       # filter initial string
          print('Device ready for gathering data!')
          drop_string = ''
          continue                                                        # restart the loop

      if ser_char == b'\n':
          Ke,Rs,mm = dropCalculator.processDrop2(drop_string)             # function to convert raw data
          bin_val = dropCalculator.processDrop(drop_string, 2)                           # function to get bin value
          data_entry(Ke,Rs,mm,bin_val)                                    # writing data to DataBase
          print 'Drop detected, KE =',Ke,', Drop radius =', Rs, ' mm'     # showing bin value of current drop to user
          drop_string = ''                                                # resetting string for next drop

except KeyboardInterrupt:
  print('Reseting the board')

dropCalculator.sendSerialCommand(ser,4)
ser.close()   # close the serial port
conn.close()  # close DB connection
