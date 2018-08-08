import serial
import serial.tools.list_ports

import time
import numpy as np

class LightSensor:
    """
	"""
	
	
    def __init__(self):
        """Class constructor that declares variables to be used in the class.
        
        ser (str): Empty string variable for the name of the serial port.
        bfull (float): A variable for the full spectrum background value, set to zero.
        bir (float): A variable for the ir spectrum background value, set to zero.
        bvis (float): A variable for the visible spectrum background value, set to zero.
        bferr (float): A variable for the full spectrum background error value, set to zero.
        bierr (float): A variable for the ir spectrum background error value, set to zero.
        bverr (float): A variable for the visible spectrum background error value, set to zero.
        fullvals (list): Empty list to contain the full spectrum values.
        irvals (list): Empty list to contain the ir spectrum values.
        visvals (list): Empty list to contain the vis spectrum values.
        timevals (list): Empty list to contain the time values.
        gainhist (list): Empty list to contain the full gain values.
        """
        self.ser = 'NONE'  # creates a variable for the serial port
        
        self.bfull = 0   # variables for the background values
        self.bir = 0
        self.bvis = 0
        self.bferr = 0
        self.bierr = 0
        self.bverr = 0
        
        self.fullvals = []   # lists for all intesity values
        self.irvals = []
        self.visvals = []
        self.timevals = []
        self.gainhist = []  # history of gain values
        
    def getPortName(self):
        """Function lists out avaliable ports on device."""
        for port in serial.tools.list_ports.comports():
            print(port.device)
            
    def declarePort(self, portName):
        """Function sets serial variable to declared port.
        
        portName (str): Name of the port the sensor uses.
        """
        self.ser = serial.Serial(portName, 9600)
        self.ser.timeout = 2
        
    def closePort(self):
        """Function closes the port."""
        self.ser.close()
    
    def sensorRead(self):
        """Function that takes readings from the light sensor.
        
        returns:
        full (int): The full spectrum value from the Arduino
        ir (int): The ir spectrum value from the Arduino
        visible (int): The visible spectrum value from the Arduino
        seconds (int): The time value in seconds from the Arduino
        gainstr (str): The string value for the gain
        """
        lightstr = self.ser.readline().decode('utf-8')
        fullstr, irstr, timestr, gainstr = lightstr.rstrip().split(sep = ' ')
        full = int(fullstr)
        ir = int(irstr)
        time = int(timestr)  # in milliseconds
        visible = full - ir
        seconds = time / 1000
        
        return full, ir, visible, seconds, gainstr
    
    def convertGain(self, gainstr, fullval, irval, visval):
        """Function that converts the string value of the gain from the Arduino.
        
        gainstr (str): The string value for the gain
        fullval (int): The full spectrum value from the Arduino
        irval (int): The ir spectrum value from the Arduino
        visval (int): The visible spectrum value from the Arduino
        
        returns:
        gain (str): The name of the gain value from the Arduino
        full (float): The full spectrum value with the gain multiplier divided out
        ir (float): The ir spectrum value with the gain multiplier divided out
        visible (float): The visible spectrum value with the gain multiplier divided out
        """
        if gainstr == '48':
            gain = 'MAX'
            full = fullval / 9876
            ir = irval / 9876
            visible = visval / 9876
        if gainstr == '32':
            gain = 'HIGH'
            full = fullval / 428
            ir = irval / 428
            visible = visval / 428
        if gainstr == '16':
            gain = 'MED'
            full = fullval / 25
            ir = irval / 25
            visible = visval / 25
        if gainstr == '0':
            gain = 'LOW'
            full = fullval
            ir = irval
            visible = visval

        return gain, full, ir, visible
    
    def getMultipliers(self):
        """Function which gives the gain with their multipliers."""
        print('MAX: 9876')
        print('HIGH: 428')
        print('MED: 25')
        print('LOW: 1')
    
    def setBackground(self, integratetime):
        """Function that takes readings of the background light intesity for a certain amount of time.
    
        integratetime (int): Variable for how long a trial should run.
        """  
        self.collect(integratetime)
        self.bfull, self.bir, self.bvis = self.average()
        self.bferr, self.bierr, self.bverr = self.error()    
    
    def resetBackground(self):
        """Function to reset the background values to zero."""
        self.bfull = 0
        self.bir = 0
        self.bvis = 0
        self.bferr = 0
        self.bierr = 0
        self.bverr = 0
    
    def collect(self, integratetime):
        """Funtion to take intensity readings over a user input time.
        
        integratetime (int): Variable for how long a trial should run.
        """
        self.ser.flushInput() # flushes the Arduino of extra values
        self.listclear()   # clears the list automatically everytime collect is called
        
        start = time.time()
        currenttime = time.time()
        end = (start + integratetime)
    
        print("Intensity values being collected...")

        while currenttime < end: 
            try:
                fullval, irval, visval, seconds, gainstr = self.sensorRead()  # reads values from the Arduino
                gain, full, ir, visible = self.convertGain(gainstr, fullval, irval, visval)
                
                self.fullvals.append(full)
                self.irvals.append(ir)
                self.visvals.append(visible)
                self.timevals.append(seconds)
                self.gainhist.append(gain)
        
                t = end - currenttime
                currenttime = time.time()
            
            except ValueError:      # error at float conversion
                print("Conversion error: frame dropped, continuing collection.")
                continue

            except IndexError:      # not all values received for a measurement set
                print("Partial frame received: frame dropped, continuing collection.")
                continue

            except serial.serialutil.SerialException: # Someone just unplugged the device, or other loss of communication.
                print("Lost connection to device, exiting.")
                break

            except:     # Catch-all
                print("Unknown error! Exiting program...")
                break
        
        print("Intensity values collected successfully.")
        
    
    def dataValues(self, integratetime):
        """Function that takes collected data and removes the background intensity values.
    
        integratetime (int): Variable for how long a trial should run.
        """
        self.collect(integratetime)
            
        for i in range(len(self.fullvals)):
            self.fullvals[i] -= self.bfull
        for i in range(len(self.irvals)):
            self.irvals[i] -= self.bir
        for i in range(len(self.visvals)):
            self.visvals[i] -= self.bvis
        
        self.printAverage()  # prints out the Averages and errors
    
    def average(self):
        """Function that takes lists of spectra values and returns the average.
        
        returns:
        fullavg (float): the average values of full spectrum intensity values.
        iravg (float): the average vaules of ir intensity values.
        visavg (float): the average values of visible intensity values.
        """
    
        fullavg = sum(self.fullvals) / len(self.fullvals)
        iravg = sum(self.irvals) / len(self.irvals)
        visavg = sum(self.visvals) / len(self.visvals)
    
        return fullavg, iravg, visavg
    
    def standardDeviation(self):
        """Function which give the standard deviation of values.
        
        returns:
        stdfull (float): the standard deviation of the full values list.
        stdir (float): the standard deviation of the ir values list.
        stdvis (float): the standard deviation of the visible values list.
        """
        stdfull = np.std(self.fullvals, ddof=1)
        stdir = np.std(self.irvals, ddof=1)
        stdvis = np.std(self.visvals, ddof=1)
    
        return stdfull, stdir, stdvis
    
    def error(self):
        """Function which gives the error of values.
    
        returns:
        errfull (float): The error of the full spectrum values
        errir (float): The error of the ir spectrum values
        errvis (float): The error of the visible spectrum values
        """
        stdfull, stdir, stdvis = self.standardDeviation()
        errfull = stdfull / np.sqrt(len(self.fullvals))
        errir = stdir / np.sqrt(len(self.irvals))
        errvis = stdvis / np.sqrt(len(self.visvals))
    
        return errfull, errir, errvis
        
    def listclear(self):
        """Function to clear the list variables of all values."""
        self.fullvals.clear()
        self.irvals.clear()
        self.visvals.clear()
        self.timevals.clear()
        self.gainhist.clear()
        
    def printHelp(self, name, full, ferr, ir, ierr, vis, verr):
        """Helper function which contains the format to print intensity values.
        
        name (str): The name of the values being printed
        full (float): The average full spectrum value
        ferr (float): The error of the full spectrum values
        ir (float): The average ir spectrum value
        ierr (float): The error of the ir spectrum values
        vis (float): The average visible spectrum value
        verr (float): The error of the visible spectrum value
        """
        print(name)
        print('Full: %f ± %f' % (full, ferr))
        print('IR: %f ± %f' % (ir, ierr))
        print('Visible: %f ± %f' % (vis, verr))
        
    def getBackground(self):
        """Gets the background values."""
        return self.bfull, self.bferr, self.bir, self.bierr, self.bvis, self.bverr
    
    def printBackground(self):
        """Prints the background values."""
        self.printHelp('Background', self.bfull, self.bferr, self.bir, self.bierr, self.bvis, self.bverr)
    
    def getAverage(self): 
        """Gets the average and error of the current intensities in the lists."""
        fullavg, iravg, visavg = self.average()
        ferr, ierr, verr = self.error()
        return fullavg, iravg, visavg, ferr, ierr, verr
    
    def printAverage(self):
        """Prints the average and error of the current intensities in the lists."""
        full, ir, vis, ferr, ierr, verr = self.getAverage()
        self.printHelp('Average', full, ferr, ir, ierr, vis, verr)
    
    def getRecent(self):
        """Gets the most recent values stored in the lists."""
        return self.fullvals, self.irvals, self.visvals, self.timevals
    
    def getGain(self):
        """Gets the history of the gain values."""
        return self.gainhist