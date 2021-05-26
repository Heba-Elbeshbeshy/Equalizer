from PyQt5 import QtWidgets, uic, QtCore, QtGui
from pyqtgraph import PlotWidget, PlotItem
import pyqtgraph as pg
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm
from scipy.io import wavfile
from scipy.fftpack import fft
from random import randint
import matplotlib.pyplot as plt
from playsound import playsound
import sys
import os
import pathlib
import numpy as np
import math
from MainWindow import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.Input_Updated_Channel = [self.ui.graphicsView,self.ui.graphicsView_2]
        self.sliders_vector =[self.ui.verticalSlider, self.ui.verticalSlider_2 ,self.ui.verticalSlider_3,self.ui.verticalSlider_4 , self.ui.verticalSlider_5 , self.ui.verticalSlider_6 ,self.ui.verticalSlider_7,self.ui.verticalSlider_8,self.ui.verticalSlider_9, self.ui.verticalSlider_10]
        self.MaxminSliders = [self.ui.verticalSlider_11 , self.ui.verticalSlider_12]
        self.Photo = [ self.ui.photo , self.ui.photo2]
        
        self.flag = False
        self.slider_change = False
        self.sliderchange =False
        self.Max_Min=False

        self.color1 = pg.mkPen(color=(255,255,0))
        self.color2 = pg.mkPen(color=(255,0,0)) 
        self.color =[self.color1 , self.color2]    

        self.ui.verticalSlider_11.valueChanged.connect(self.MaxMin)  
        self.ui.verticalSlider_12.valueChanged.connect(self.MaxMin) 
       
        self.ui.actionOpen.triggered.connect(lambda :self.loadFile())
        self.ui.actionNew.triggered.connect(self.new_window)  
        # self.ui.print.triggered.connect(print)
        self.ui.comboBox.currentIndexChanged.connect(self.spectrogram)
        self.ui.checkBox.stateChanged.connect(self.hidespectro)
        self.ui.reset.clicked.connect(lambda : self.reset())
        self.ui.save.clicked.connect(lambda : self.save())
        self.ui.Zoomin.clicked.connect(lambda : self.zoom(1))
        self.ui.Zoomout.clicked.connect(lambda : self.zoom(2))
        self.ui.Scrollr.clicked.connect(lambda : self.Scroll(1))
        self.ui.Scrolll.clicked.connect(lambda : self.Scroll(2))
        self.ui.Scrollu.clicked.connect(lambda : self.Scroll(3))
        self.ui.Scrolld.clicked.connect(lambda : self.Scroll(4))
        self.ui.Clear.clicked.connect(self.clear)  
        self.ui.playb.clicked.connect(lambda : self.playsound(1))
        self.ui.playa.clicked.connect(lambda : self.playsound(2))

        for slider in self.sliders_vector:
            slider.valueChanged.connect(self.update_sliders)

    def new_window(self):
        self.new = MainWindow()
        self.new.show()

    def update_sliders(self):
        self.sliderValue= list()
        for i in range(10) :  
            self.sliderValue.append(self.sliders_vector[i].value())
        print(self.sliderValue)
        self.getSliderValue(self.sliderValue)
    
    def loadFile(self) :
        fname = QtGui.QFileDialog.getOpenFileName( self, 'choose the signal', os.getenv('HOME') ,"wav(*.wav)" )
        self.path = fname[0]     
        if self.path =="" :
            return
        self.flag = True
        self.fs , self.data = wavfile.read(self.path)
        self.data =np.array(self.data)
        print(self.data)

        self.Time = []
        self.duration = len(self.data) / self.fs
        for i in range(len(self.data)):
           x=i/self.fs
           self.Time.append(x)

        freq=np.arange(1.0,(self.fs/2)+1)
        dec= 20*(np.log10(freq)*(-1))

        for sldr in range(2):
            self.MaxminSliders[sldr].setMinimum(min(dec))
            self.MaxminSliders[sldr].setMaximum(max(dec))

        # FourierTransform
        self.DataFourier  =np.fft.rfft(self.data)
        self.Magnitude = np.abs(self.DataFourier) #to be real 
        self.phase = np.exp(1j*np.angle(self.DataFourier))
        self.DataFrequency =np.fft.fftfreq(len(self.data))
        
        self.copyData = self.Magnitude[:]

        #Creating bands
        self.bands = list() 
        for i in range(10):
            self.StartBand = int(i / 10 * len(self.copyData)) 
            self.EndBand = int((i + 1) / 10 * len(self.copyData))
            self.bands.append(self.copyData[self.StartBand : self.EndBand]) 
        self.bandContainer = self.bands[:] 

        # Plotting the OriginalSignal 
        for i in range(2):
            self.Input_Updated_Channel[i].setLimits(xMin=0, xMax=80200, yMin=-50000, yMax=50000)
            self.Input_Updated_Channel[i].setYRange(min(self.data),max(self.data)) 
            self.Input_Updated_Channel[i].plot(self.data , pen = self.color[i]) 
            self.spectrogram()
            
    def getSliderValue(self, SlidersGain):
        self.slider_change = True  
        self.sliderchange =True 

        if self.flag and self.slider_change:
            for index in range (10):
                self.bandContainer[index] = np.multiply( SlidersGain[index],self.bands[index])         
            self.NewData= list()
            self.NewData.clear()
            for i in range(10):
                for j in range(len(self.bandContainer[i])):
                    self.NewData.append(self.bandContainer[i][j])

            # InverseFourier
            self.CombinedData = np.multiply(np.array(self.NewData), self.phase)            
            self.absInverse = np.fft.irfft(self.CombinedData)
            print (self.absInverse)
            
            self.Input_Updated_Channel[1].clear()
            self.Input_Updated_Channel[1].plot(self.absInverse, pen = self.color[1])
            self.spectrogram()     

    def MaxMin(self):
        global min_slider, max_slider 
        self.Max_Min=True

        max_slider= self.ui.verticalSlider_11.value()
        min_slider= self.ui.verticalSlider_12.value()

        print(max_slider) 
        print(min_slider)  
        self.spectrogram()

    def spectrogram(self, *args): 
        global cmap  
        palette=['inferno','viridis','plasma','magma','cividis']

        #cmap='color'
        for i in range(len(palette)):
            if self.ui.comboBox.currentIndex()==i:
                cmap= palette[i]

        plt.figure(1)
        plt.title('Spectrogram')    
        plt.specgram(self.data,Fs=self.fs,cmap=cmap)
        plt.colorbar()
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.savefig('Input Spectrogram.PNG')
        plt.clf()
        self.ui.photo.setPixmap(QtGui.QPixmap("Input Spectrogram.PNG"))
        self.ui.photo2.setPixmap(QtGui.QPixmap("Input Spectrogram.PNG"))

        if self.sliderchange :
            plt.specgram(self.absInverse, Fs=self.fs, cmap=cmap)

            if self.Max_Min:
                plt.specgram(self.absInverse, Fs=self.fs, cmap=cmap, scale = "dB" , vmax=max_slider ,vmin=min_slider)

            plt.colorbar()
            plt.savefig('Updated Spectrogram.PNG')
            plt.clf()
            self.ui.photo2.setPixmap(QtGui.QPixmap("Updated Spectrogram.PNG"))  

    # def print(self):
    #     plt.savefig('Updated Spectrogram.Png')
            
    def zoom(self, IN_OUT):
        if IN_OUT == 2:
            Scale=2
        elif IN_OUT == 1:
            Scale=1/2

        for i in range(2):
            xrange, yrange = self.Input_Updated_Channel[i].viewRange()
            self.Input_Updated_Channel[i].setYRange(yrange[0]*Scale, yrange[1]*Scale, padding=0)
            self.Input_Updated_Channel[i].setXRange(xrange[0]*Scale, xrange[1]*Scale, padding=0) 

    def Scroll(self , RIGHT_LEFT_UP_DOWN):
        rangeX = 0 
        rangeY = 0

        if RIGHT_LEFT_UP_DOWN == 1:
            rangeX = 0.5 
        elif RIGHT_LEFT_UP_DOWN == 2:
            rangeX = -0.5 
        elif RIGHT_LEFT_UP_DOWN == 3:
            rangeY = +0.9
        elif RIGHT_LEFT_UP_DOWN == 4:
            rangeY = -0.9 

        for i in range(2):
          self.Input_Updated_Channel[i].getViewBox().translateBy(x=-rangeX, y=rangeY)

    def clear(self) :
        for i in range(2):
           self.Input_Updated_Channel[i].clear()
           self.Photo[i].setPixmap(QtGui.QPixmap("white.PNG"))       

    def reset(self) : 
        for i in range(len(self.sliders_vector)):
            self.sliders_vector[i].setValue(1)
        self.update_sliders()

    def save(self):
        self.name = QtGui.QFileDialog.getSaveFileName( self,"Save file",os.getenv('HOME'),"wav (*.wav)")
        self.path_New = self.name[0] 
        new_file = np.copy(self.absInverse / self.absInverse.max()) 
        if self.path : 
            wavfile.write(self.path_New, self.fs, new_file)

    def hidespectro(self) :
            if (self.ui.checkBox.isChecked()) :
                self.ui.photo.hide()
                self.ui.photo2.hide()
            else :               
                self.ui.photo.show()
                self.ui.photo2.show()   

    def playsound(self, BEFORE_AFTER):
        if BEFORE_AFTER == 1:
            playsound(self.path)
        elif BEFORE_AFTER == 2:
            playsound(self.path_New)     

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':      
    main()
 