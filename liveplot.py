'''
This module provides the class LivePlot which can plot data from a serial device
live.

Tested on Ubuntu 15.10 with Arduino Uno.

@author: Sverre
'''
import serial
import matplotlib.pyplot as plt
import multiprocessing as mp

class LivePlot(mp.Process):
    '''
    This class handles extends multiprocessing.Process so that the 
    computation and plotting happens in a new thread.
    
    To start the plotting, call the method L{start()}. The thread will close if 
    the main thread closes, so if no work is done, nothing will be plotted. 
    This can be avoided by calling L{raw_input()}. 
    
    The thread can be closed with the method L{join()}.
    '''
    def __init__(self, ser, comp, dec=None, prop=None, save=None, clean=None, 
                 cb=None, verb=False):
        '''
        @param ser: The serial device to communicate with.
        @type ser: Serial
        @param comp: The function to be used on the input from the serial device
        to convert it to something plotable.
        @type comp: L{callable}
        @keyword dec: String with decorations for the plot such as symbol for 
        data points.
        @type dec: L{str}
        @keyword prop: Properties of the plot such as alpha and color.
        @type prop: L{tuple}
        @keyword save: File to save the processed data to.
        @type save: L{str}
        @keyword cb: Not implemented.
        @todo: Implement callback possibilities.
        @keyword clean: Not implemented.
        @todo: Implement the possibility to only read new serial data.
        @keyword verb: Boolean indicating if the data is to be printed to the 
        terminal.
        @type verb: L{bool}
        '''
        # Setup thread handling
        mp.Process.__init__(self)
        self.stopping = mp.Event()
         
        # Initialize attributes
        self.dec = dec
        self.ser = ser
        self.comp = comp
        self.verb = verb
        self.values = []
        self.fig = None
        self.prop = prop
        self.save = save
        if self.save is not None:
            self.save_file = open(save, 'w+')
        
        # Todo    
        if cb is not None:
            raise NotImplementedError
        if clean is not None:
            raise NotImplementedError
        
    def run(self):
        '''
        Read and process the data from the serial device, plot it and
        potentially save it to a file. The thread runs continuously until
        L{join()} is called or the script terminates.
        '''
        # Setup plot
        plt.figure()
        plt.ion()
        plt.show()
        plt.hold(False)
        
        while not self.stopping.is_set():
            # Process the data
            raw = self.ser.readline()
            data = self.comp(raw)
            self.values.append(data)
            
            # Display output
            if self.verb:
                print 'read: %splot: %s' % (raw, data)
            if self.save is not None:
                self.save_data(data)
            self.plot()
    
    def join(self):
        '''
        Stops the thread safely.
        '''
        self.stopping.set()
        if self.save is not None:
            self.save_file.close()
        super(self.__class__, self).join()
           
    def plot(self):
        '''
        Plots the data.
        '''
        if self.dec is not None:
            self.fig = plt.plot(self.values, self.dec)
        else:
            self.fig = plt.plot(self.values)
        if self.prop is not None:
            plt.setp(self.fig, *self.prop)
        plt.draw()
    
    def save_data(self, data):
        '''
        Saves the data to a file.
        
        @param data: The data to be saved.
        '''
        self.save_file.write(str(data) + '\n')
        self.save_file.flush()
    
def example():
    '''
    Example use of LivePlot.
    
    The serial device is an Arduino Uno connected on /dev/ttyACM0. The Arduino 
    is connected to a TMP36 sensor with +V_S connected to +5.0 VCC and V_OUT 
    connected to A0. The Arduino is connected on the port /dev/ttyACM0 and 
    loaded with the following sketch::
    
        const int sensor = 0;
        
        void setup(){
            Serial.begin(9600);
        }
        
        void loop(){
            delay(1000);
            int signal = analogRead(sensor);
            Serial.println(signal);
        } 
    '''
    a_ref = 5.0
    def convert_to_temp(line):
        signal = float(line)    
        voltage = (signal * a_ref) / 1024.
        temperature = (voltage - .5) * 100        
        return temperature
    
    device = serial.Serial(port='/dev/ttyACM0', baudrate=9600)
    p = LivePlot(device, convert_to_temp, save='/home/user/temp.dat', verb=True)
    p.start()
    raw_input()
    p.join()
    
if __name__ == '__main__':
    example() 
    
    
    