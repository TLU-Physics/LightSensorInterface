import serial
import serial.tools.list_ports

import time
import numpy as np

class LightSensor:
    
    """Use a light sensor to gather intensity values.
    
    This class uses a light sensor connected to an Arduino and utilizing a serial port to gather 
    and process light intensity data. This class takes raw data from the Arduino which is stored 
    into lists which can be analyzed by getting the averages and the errors of gather values. This
    class can record and remove any background intensity data automatically. The class can also provide
    the gain value associated with every value sent from the sensor and automatically removes any
    gain multiplier. The class provided the multiplier values which can be used to adjust any recieved 
    data accordingly.
    
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
    
    def __init__(self):
        """Declares variables to be used throughout the class."""

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
        """List out avaliable ports on device.
        
        This function is used to observe what ports are avaliable on the device being used
        and print out the name of each port. The port that will be used should match the port
        the Arduino board uses.
        """
        
        for port in serial.tools.list_ports.comports():
            print(port.device)
            
    def declarePort(self, portName):
        """Set serial variable to declared port.
        
        This function declares the port being used on the device by both the Arduino board and
        the device. Therefore, the port used must be the same as the Arduino board. The port
        is declared by a parameter controled by the user, which should match one of the printed
        port names from the getPortName function.
        
        portName (str): Name of the port the sensor uses.
        """
        
        self.ser = serial.Serial(portName, 9600)
        self.ser.timeout = 2
        
    def closePort(self):
        """Close the currently open serial port.
        
        This function closes the currently open serial port. This is important as only one device
        can use the same port at a time. Therefore, if the user wanted to edit the Arduino board
        code, or wished to create a new sensor object on the same port, the serial port would first
        need to be closed.
        """
        
        self.ser.close()
    
    def sensorRead(self):
        """Take readings from the light sensor.
        
        This function recieves the information being communicated from the Arduino board. The information
        is sent as a string through the serial port and split into the different pieces here. The
        intensity and time values are converted to integers as they are recorded as integers in the 
        Arduino code, and the time is also converted to seconds. The function then returns both the
        full and ir spectrum values, the calculated visible spectrum values, the time values, and the
        gain strings.
        
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
        """Convert the string value of the gain from the Arduino.
        
        This function takes the gain strings from the Arduino board and renames them to a more convenient
        terminology. The full, ir and visible spectrum values sent from the Arduino board are then divided
        by a gain multiplier dependent on the gain string sent by the Ardino board. This negates all the
        influence from the gain multipliers on the recorded intensity values.
        
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
            
        elif gainstr == '32':
            gain = 'HIGH'
            full = fullval / 428
            ir = irval / 428
            visible = visval / 428
            
        elif gainstr == '16':
            gain = 'MED'
            full = fullval / 25
            ir = irval / 25
            visible = visval / 25
            
        elif gainstr == '0':
            gain = 'LOW'
            full = fullval
            ir = irval
            visible = visval

        return gain, full, ir, visible
    
    def getMultipliers(self):
        """Print the gain with their multipliers.
        
        This function provides the gain options used in the Arduino code and provides the multiplier
        values. Therefore, if a user which to re-apply a gain to the recorded data, the values
        are within easy reach.
        """
        
        print('MAX: 9876')
        print('HIGH: 428')
        print('MED: 25')
        print('LOW: 1')
    
    def setBackground(self, integratetime):
        """Take readings of the background light intesity for a parameter of time.
        
        This function collects intensity values over a parameter of time in seconds and then calculates
        the average and total error of the values. This function is for the collecting of any background
        lighting to account for influencing intensity.
    
        integratetime (int): Variable for how long a trial should run.
        """  
        
        self.read(integratetime)
        self.bfull, self.bir, self.bvis = self.average()
        self.bferr, self.bierr, self.bverr = self.totalError()    
    
    def resetBackground(self):
        """Reset the background values to zero.
        
        This function resets the background variables to zero, incase there is no need to account for
        any background intensities.
        """
        
        self.bfull = 0
        self.bir = 0
        self.bvis = 0
        self.bferr = 0
        self.bierr = 0
        self.bverr = 0
    
    def read(self, integratetime):
        """Collect intensity readings over a parameter of time.
        
        This function collects intensity values using the sensor over a parameter of time. The values
        are stored into the list variables for this class and the variables are cleared each time
        this function is called. This function also tries to catch any error that can occur when using
        serial communication.
        
        integratetime (int): Variable for how long a trial should run.
        """
        
        self.ser.flushInput() # flushes the Arduino of extra values
        self.listclear()   # clears the list automatically everytime collect is called
        
        start = time.time()  # for use in controling how long the loop collects data
        currenttime = time.time()
        end = (start + integratetime)
    
        print("Intensity values being collected...")

        while currenttime < end: 
            try:
                fullval, irval, visval, seconds, gainstr = self.sensorRead()  # reads values from the Arduino
                gain, full, ir, visible = self.convertGain(gainstr, fullval, irval, visval)
                
                self.fullvals.append(full)  # stores all values into the list variables
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
        
    
    def collectData(self, integratetime):
        """Take collected data and remove the background intensity values.
        
        This is the main function being called by the user. This function uses the collect function
        and a parameter of time to collect the intensity values and then subtracts off any background
        values present. The function then prints out the calculated averages and errors.
    
        integratetime (int): Variable for how long a trial should run.
        """
        
        self.read(integratetime)
            
        for i in range(len(self.fullvals)):
            self.fullvals[i] -= self.bfull
        for i in range(len(self.irvals)):
            self.irvals[i] -= self.bir
        for i in range(len(self.visvals)):
            self.visvals[i] -= self.bvis
        
        self.printAverage()  # prints out the Averages and errors
    
    def average(self):
        """Take lists of spectra values and return the average.
        
        This function uses the list variables for the intensities and calculates the averages
        of all the light spectrum values.
        
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
        """Give the standard deviation of values.
        
        This function uses the list variables for the intensities and calculates the standard deviation
        all the spectrum values.
        
        returns:
        stdfull (float): the standard deviation of the full values list.
        stdir (float): the standard deviation of the ir values list.
        stdvis (float): the standard deviation of the visible values list.
        """
        
        stdfull = np.std(self.fullvals, ddof=1)
        stdir = np.std(self.irvals, ddof=1)
        stdvis = np.std(self.visvals, ddof=1)
    
        return stdfull, stdir, stdvis
    
    def fluctuationError(self):
        """Give the error of the fluctuations of values.
        
        This function calculates the error in the fluctuations of the spectrum values. This error
        is specifically for just the fluctuation error, or the differences between the average calculated
        and the true average.
    
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
    
    def integerError(self):
        """Give the error of the reported integer values from the Arduino.
        
        This function calculates the error of the integer values from the Arduino board, based on 
        the gain. As the Arduino reports the intensities as integers there is a possibility that the
        value sent to the device is not quite accurate. The values could range from 0.5 above the recorded
        value to 0.5 below. The error is also divided by the gain multiplier to negate the influence of
        gain.
        
        returns:
        fullerr (float): The error of the full spectrum values
        irerr (float): The error of the ir spectrum values
        viserr (float): The error of the visible spectrum values
        """
        
        for gain in self.gainhist:
            if gain == 'LOW':
                fullerr = 0.5
                irerr = 0.5
                viserr = 0.5
            elif gain == 'MED':
                fullerr = 0.5 / 25
                irerr = 0.5 / 25
                viserr = 0.5 / 25
            elif gain == 'HIGH':
                fullerr = 0.5 / 428
                irerr = 0.5 / 428
                viserr = 0.5 / 428
            elif gain == 'MAX':
                fullerr = 0.5 / 9876
                irerr = 0.5 / 9876
                viserr = 0.5 / 9876
            
        return fullerr, irerr, viserr
    
    def totalError(self):
        """Total the additive error for the light sensor.
        
        This function combines the error on the fluctuations and the error on the integers
        for a total error.
        
        returns:
        ferrtot (float): The total error of the full spectrum values
        ierrtot (float): The total error of the ir spectrum values
        verrtot (float): The total error of the visible spectrum values 
        """
        
        errfull, errir, errvis = self.fluctuationError()
        fullerr, irerr, viserr = self.integerError()
        
        ferrtot = np.sqrt((errfull ** 2) + (fullerr ** 2))
        ierrtot = np.sqrt((errir ** 2) + (irerr ** 2))
        verrtot = np.sqrt((errvis ** 2) + (viserr ** 2))
        
        return ferrtot, ierrtot, verrtot
        
    def listclear(self):
        """Clear the list variables of all values.
        
        This function clears each of the list variables of any values contained.
        """
        
        self.fullvals.clear()
        self.irvals.clear()
        self.visvals.clear()
        self.timevals.clear()
        self.gainhist.clear()
        
    def printHelp(self, name, full, ferr, ir, ierr, vis, verr):
        """Helper function to contain the format to print intensity values.
        
        This function provides the formatting to print out the intensities. This funtion should
        most likely never be used by a user, as this is a helper function.
        
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
        """Get the background values.
        
        This function retrieves the background averages and errors, which can then be
        stored into variables and used by the user.
        """
        return self.bfull, self.bferr, self.bir, self.bierr, self.bvis, self.bverr
    
    def printBackground(self):
        """Print the background values.
        
        This function uses the format provided by the printHelp function to print the background
        averages and errors in an easy to see format.
        """
        
        self.printHelp('Background', self.bfull, self.bferr, self.bir, self.bierr, self.bvis, self.bverr)
    
    def getAverage(self): 
        """Get the average and error of the current intensities in the lists.
        
        This function retrieves the current intensity averages and errors, which can then be
        stored into variables and used by the user."""
        
        fullavg, iravg, visavg = self.average()
        ferr, ierr, verr = self.totalError()
        return fullavg, iravg, visavg, ferr, ierr, verr
    
    def printAverage(self):
        """Print the average and error of the current intensities in the lists.
        
        This function uses the format provided by the printHelp function to print the current intensity
        averages and errors in an easy to see format."""
        
        full, ir, vis, ferr, ierr, verr = self.getAverage()
        self.printHelp('Average', full, ferr, ir, ierr, vis, verr)
    
    def getRecent(self):
        """Get the most recent values stored in the lists.
        
        This function gets the most recent values stored in the list variables. It should be noted that if
        the values contained in the list are needed, this function should be called and the lists stored in
        a variable by the user before new data is collected as the list will then be cleared to account for 
        new data.
        """
        
        return self.fullvals, self.irvals, self.visvals, self.timevals
    
    def getGain(self):
        """Get the history of the gain values.
        
        This function gets the history of the gain sent by the Arduino board and stored into a list. If these
        values are needed, this function should be called before new data is collected as this list will then
        be cleared to account for new data.
        """
        
        return self.gainhist