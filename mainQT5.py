#!/usr/bin/python3
import matplotlib
matplotlib.use("Qt5Agg", force = True)
from matplotlib.pyplot import *
from skimage.exposure import adjust_gamma
from skimage.color import rgb2gray
from skimage.util import dtype
import PIL.ImageOps
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
style.use('ggplot')
from sys import argv
import pickle
import glob
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from skimage.transform import rescale, resize, downscale_local_mean
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
from ast import literal_eval as make_tuple
import re
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from skimage.feature import blob_dog, blob_log
from skimage import io
from math import sqrt
from collections import Counter
from skimage import exposure
from skimage import transform
from numpy import array, transpose, vstack, hstack
from numpy import sum, angle, nan_to_num
from pandas import DataFrame, read_csv, concat
from skimage.feature import corner_harris, corner_subpix, corner_peaks
from skimage.transform import warp, AffineTransform
from matplotlib.lines import Line2D
import matplotlib
import imageio
from skimage.filters import median
#matplotlib.style.use('ggplot')
#mpl.rcParams[''] = 2


#form_class = uic.loadUiType("C:\Users\thiag\Documents\GitHub\RapID-cell-counter\bycells2.ui")[0]
form_class = uic.loadUiType("bycells2v2.ui")[0]
#form_class2 = uic.loadUiType("bycells_classwindow.ui")[0]

class MainWindow(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.cellpoints = np.array([])
        self.FindCells.clicked.connect(self.Id_cells)
        self.AddClassified.clicked.connect(self.create_csv)
        self.imageviewbutton.clicked.connect(self.openMainFig)
        self.numLayers.valueChanged.connect(self.redrawLayers)
        #self.maxSigSpin.valueChanged.connect(self.Id_cells)
        #self.minSigSpin.valueChanged.connect(self.Id_cells)
        #self.log_overlap.valueChanged.connect(self.Id_cells)
        #self.thresholdSpin.valueChanged.connect(self.Id_cells)
        self.cropsize = 25
        self.fig = Figure()
        self.THEimage = np.array([])
        self.BLUEimage = 0
        self.BLUEblobs = np.array([])
        self.REDimage = 0
        self.GREENimage = 0
        self.THEblobs = np.array([])
        self.table.setColumnCount(6)
        self.layout.addWidget(self.table, 1, 0)
        self.table.setHorizontalHeaderLabels(['Layer', 'Fluorescent cell count', 'Area', 'Density', 'Nuclei count', 'Fluorescent fraction' ])
        for num, layer in enumerate( [str(x+1) for x in range(int(self.numLayers.text()))] + ['Total selected reg', 'Total image']):
            self.table.insertRow(num)
            self.table.setItem(num , 0, QtWidgets.QTableWidgetItem(layer))
            self.table.setItem(num , 1, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 2, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 3, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 4, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 5, QtWidgets.QTableWidgetItem("0"))

        self.directory = 'singleCells/'
        self.guidePoints = {'TR': 0, 'TL' : 0, 'BL' : 0, 'BR': 0}
        self.innergridRight = [(self.guidePoints['TR']*i+ self.guidePoints['BR']*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(1,int(self.numLayers.text()) +1)]
        self.innergridLeft = [(self.guidePoints['TL']*i+ self.guidePoints['BL']*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(1,int(self.numLayers.text()) +1)]
        self.polygonList = []
        self.bigpoligon = 0
        self.figname = 0
        self.imgPolygon =0
        self.orange_rgb_representation = np.array([93.6, 37.8, 0])/255
        #self.saveDir.setText('singleCells/')

    def openDIRwindow(self):
        dirwindow = allDirectoriesWindow(self)
        dirwindow.exec_()

    def removeCell(self, cellnumber):
        self.THEblobs[cellnumber:-1] = self.THEblobs[cellnumber+1:]
        self.THEblobs = self.THEblobs[:-1]
        self.ImgAddPatches()


    def chooseDirectory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self)
        self.saveDir.setText(str(directory) + '/')
        self.DatabaseSize.setText(str( len(glob.glob(str(self.saveDir.text())+ '*.png') ) ) )

    def extract_specific_color_from_image(self,figure2transform, color_rep_rgb):
        rgb_temp = dtype.img_as_float(figure2transform, force_copy=True) + 2
        reshaped_rgb = np.reshape(-np.log(rgb_temp), (-1, 3))
        single_stain = -np.dot(reshaped_rgb, color_rep_rgb)
        single_stain = 255*(single_stain - single_stain.min())/ (single_stain.max() - single_stain.min())
        return np.reshape(single_stain, (rgb_temp.shape[0], rgb_temp.shape[1]))

    def openMainFig(self):
        if self.THEimage.any() == True:
            self.rmmpl()
            self.THEimage = np.array([])
            self.BLUEimage = 0
            while self.table.rowCount() < int(self.numLayers.text())+2: self.table.insertRow(0)
            while self.table.rowCount() > int(self.numLayers.text())+2: self.table.removeRow(0)
            for num, layer in enumerate([str(x+1) for x in range(int(self.numLayers.text()))] + ['Total selected reg', 'Total image']):
                self.table.setItem(num , 0, QtWidgets.QTableWidgetItem(layer))
                self.table.setItem(num , 1, QtWidgets.QTableWidgetItem("0"))
                self.table.setItem(num , 2, QtWidgets.QTableWidgetItem("0"))
                self.table.setItem(num , 3, QtWidgets.QTableWidgetItem("0"))
                self.table.setItem(num , 4, QtWidgets.QTableWidgetItem("0"))
                self.table.setItem(num , 5, QtWidgets.QTableWidgetItem("0"))
            self.directory = 'singleCells/'
            self.guidePoints = {'TR': 0, 'TL' : 0, 'BL' : 0, 'BR': 0}
            self.innergridRight = [(self.guidePoints['TR']*i+ self.guidePoints['BR']*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(1,int(self.numLayers.text()) +1)]
            self.innergridLeft = [(self.guidePoints['TL']*i+ self.guidePoints['BL']*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(1,int(self.numLayers.text()) +1)]
            self.polygonList = []
            self.bigpoligon = 0
            self.nMarkedCells.setText(str(0))
            self.THEblobs = np.array([])

        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', '~/Desktop/', "Image files (*.jpg *.png *.tif *.tiff)")
        self.figname = str(name[0])
        image = imageio.imread(self.figname)
        ### if image is too large we will resize it
        if image.shape[0] > 2000 or image.shape[1] > 2000:
            if image.shape[0] > image.shape[1]: resize_factor = 2000/image.shape[0]
            else:resize_factor = 2000/image.shape[1]
            image = resize(image, (int(image.shape[0] * resize_factor), int(image.shape[1] * resize_factor)),anti_aliasing=True)

        #self.saveNames.setText(str(name).split("/")[-1][:-4] + 'i')
        #image = median(image)
        self.THEimage = image
        self.imgPolygon = Polygon([[0,0],[0,image.shape[1]],[image.shape[0],image.shape[1]],[image.shape[0],0]]  )
        self.BLUEimage = image[:,:,2]
        #self.BLUEblobs = blob_log(self.BLUEimage[self.cropsize:-self.cropsize,self.cropsize:-self.cropsize],  max_sigma=int(self.maxSigSpin.text()), num_sigma=10, min_sigma = int(self.minSigSpin.text()),overlap = float(self.log_overlap.text()) ,threshold=float(self.thresholdSpin.text()))
        self.REDimage = image[:,:,0]
        self.GREENimage = image[:,:,1]
        self.ORANGEimage = self.extract_specific_color_from_image(image, self.orange_rgb_representation)
        baseimage = self.fig.add_subplot(111)
        #baseimage.axis('off', frameon=False)
        #baseimage.grid(False)
        #baseimage.imshow(image)
        #axis('off')
        #subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

        self.fig, ax = subplots(1, 1)
        ax.imshow(self.THEimage)
        ax.axis('off')
        subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

        self.canvas = FigureCanvas(self.fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.widget, coordinates=True)
        self.mplvl.addWidget(self.toolbar)
        cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

    def onclick(self, event):
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %(event.button, event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            if str(self.rClicktype.currentText()) == 'Add cell':
                squaresize = self.cropsize
                #print(len(self.THEblobs))
                self.THEblobs =np.array(self.THEblobs.tolist() + [[int(event.ydata), int(event.xdata), self.cropsize]])
                #print(len(self.THEblobs))
                #self.table.setHorizontalHeaderLabels(['index', 'auto class', 'manual class'])
                #rowPosition = self.table.rowCount()
                #self.table.insertRow(rowPosition)

                self.nMarkedCells.setText(str(int(self.nMarkedCells.text()) + 1))
                self.ImgAddPatches()
            if str(self.rClicktype.currentText()) == 'Add 1st box corner':
                self.guidePoints['TR'] = [int(event.ydata),int(event.xdata)]
                self.rClicktype.setCurrentIndex =='Add 2nd box corner'

                if 0 not in self.guidePoints.values():
                   self.polygonList = []
                   self.innergridRight = [(array(self.guidePoints['TR'])*i+ array(self.guidePoints['BR'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
                   self.innergridLeft = [(array(self.guidePoints['TL'])*i+ array(self.guidePoints['BL'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
                   #print(self.innergridLeft, self.innergridRight)
                   self.bigpoligon = Polygon([self.guidePoints['TR'], self.guidePoints['TL'],self.guidePoints['BL'],self.guidePoints['BR']])
                   for i in range(len(self.innergridLeft)-1):
                       self.polygonList += [Polygon([self.innergridRight[i], self.innergridLeft[i],self.innergridLeft[i+1], self.innergridRight[i+1]])]
                self.ImgAddPatches()

            if str(self.rClicktype.currentText()) == 'Add 2nd box corner':
                self.guidePoints['TL'] = [int(event.ydata),int(event.xdata)]
                self.rClicktype.setCurrentIndex =='Add 3rd box corner'

                if 0 not in self.guidePoints.values():
                   self.polygonList = []
                   self.innergridRight = [(array(self.guidePoints['TR'])*i+ array(self.guidePoints['BR'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
                   self.innergridLeft = [(array(self.guidePoints['TL'])*i+ array(self.guidePoints['BL'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
                   #print(self.innergridLeft, self.innergridRight)
                   self.bigpoligon = Polygon([self.guidePoints['TR'], self.guidePoints['TL'],self.guidePoints['BL'],self.guidePoints['BR']])
                   for i in range(len(self.innergridLeft)-1):
                       self.polygonList += [Polygon([self.innergridRight[i], self.innergridLeft[i],self.innergridLeft[i+1], self.innergridRight[i+1]])]
                self.ImgAddPatches()

            if str(self.rClicktype.currentText()) == 'Add 3rd box corner':
                self.guidePoints['BL'] = [int(event.ydata),int(event.xdata)]
                self.rClicktype.setCurrentIndex =='Add 4th box corner'

                if 0 not in self.guidePoints.values():
                   self.polygonList = []
                   self.innergridRight = [(array(self.guidePoints['TR'])*i+ array(self.guidePoints['BR'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
                   self.innergridLeft = [(array(self.guidePoints['TL'])*i+ array(self.guidePoints['BL'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
                   #print(self.innergridLeft, self.innergridRight)
                   self.bigpoligon = Polygon([self.guidePoints['TR'], self.guidePoints['TL'],self.guidePoints['BL'],self.guidePoints['BR']])
                   for i in range(len(self.innergridLeft)-1):
                       self.polygonList += [Polygon([self.innergridRight[i], self.innergridLeft[i],self.innergridLeft[i+1], self.innergridRight[i+1]])]
                self.ImgAddPatches()

            if str(self.rClicktype.currentText()) == 'Add 4th box corner':
                self.guidePoints['BR'] = [int(event.ydata),int(event.xdata)]
                if 0 not in self.guidePoints.values():
                   self.polygonList = []
                   self.innergridRight = [(array(self.guidePoints['TR'])*i+ array(self.guidePoints['BR'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
                   self.innergridLeft = [(array(self.guidePoints['TL'])*i+ array(self.guidePoints['BL'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
                   #print(self.innergridLeft, self.innergridRight)
                   self.bigpoligon = Polygon([self.guidePoints['TR'], self.guidePoints['TL'],self.guidePoints['BL'],self.guidePoints['BR']])
                   #print(self.bigpoligon)
                   for i in range(len(self.innergridLeft)-1):
                       self.polygonList += [Polygon([self.innergridRight[i], self.innergridLeft[i],self.innergridLeft[i+1], self.innergridRight[i+1]])]
                self.ImgAddPatches()
            if str(self.rClicktype.currentText()) == 'Remove cell':
                dist = np.sum((self.THEblobs[:,0:2]-[event.ydata,event.xdata])**2,1)
                if min(dist) < 800:
                    line = dist.tolist().index(min(dist))
                    #print(line)
                    self.removeCell(line)
                    self.nMarkedCells.setText(str(int(self.nMarkedCells.text()) - 1))
                #self.ImgAddPatches()


        elif event.button == 2:
            #print(self.THEblobs[:,0:2])
            dist = np.sum((self.THEblobs[:,0:2]-[event.ydata,event.xdata])**2,1)
            if min(dist) < 800:
                line = dist.tolist().index(min(dist))
                #print(line)
                self.removeCell(line)
                self.nMarkedCells.setText(str(int(self.nMarkedCells.text()) - 1))
            #self.ImgAddPatches()


    def redrawLayers(self):
        if 0 not in self.guidePoints.values():
           self.polygonList = []
           self.innergridRight = [(array(self.guidePoints['TR'])*i+ array(self.guidePoints['BR'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
           self.innergridLeft = [(array(self.guidePoints['TL'])*i+ array(self.guidePoints['BL'])*(int(self.numLayers.text())-i))/int(self.numLayers.text()) for i in range(0,int(self.numLayers.text()) +1)]
           #print(self.innergridLeft, self.innergridRight)
           self.bigpoligon = Polygon([self.guidePoints['TR'], self.guidePoints['TL'],self.guidePoints['BL'],self.guidePoints['BR']])
           #print(self.bigpoligon)
           for i in range(len(self.innergridLeft)-1):
               self.polygonList += [Polygon([self.innergridRight[i], self.innergridLeft[i],self.innergridLeft[i+1], self.innergridRight[i+1]])]
        self.ImgAddPatches()


    def changeFIGURE(self, newFIG):
        self.rmmpl()
        self.canvas = FigureCanvas(newFIG)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.widget, coordinates=True)
        self.mplvl.addWidget(self.toolbar)
        cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)


    def rmmpl(self,):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()

    def Id_cells(self):
        if type(self.BLUEimage) == type(0): return
        while self.table.rowCount() < int(self.numLayers.text())+2: self.table.insertRow(0)
        while self.table.rowCount() > int(self.numLayers.text())+2: self.table.removeRow(0)
        for num, layer in enumerate( [str(x+1) for x in range(int(self.numLayers.text()))] + ['Total selected reg', 'Total image']):
            self.table.setItem(num , 0, QtWidgets.QTableWidgetItem(layer))
            self.table.setItem(num , 1, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 2, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 3, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 4, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 5, QtWidgets.QTableWidgetItem("0"))

        squaresize = self.cropsize
        image_gray = self.BLUEimage

        self.BLUEblobs = blob_log(self.BLUEimage,  max_sigma=int(self.maxSigSpin.text()), num_sigma=10, min_sigma = int(self.minSigSpin.text()),overlap = float(self.log_overlap.text()) ,threshold=float(self.thresholdSpin.text()), exclude_border = squaresize)
        self.table.setItem(int(self.numLayers.text()) +1 , 4, QtWidgets.QTableWidgetItem(str(len(self.BLUEblobs))))
        if str(self.fMarker.currentText())  == 'RFP':
            blobs = blob_log(self.REDimage,  max_sigma=int(self.maxSigSpin.text()), num_sigma=10, min_sigma = int(self.minSigSpin.text()),overlap = float(self.log_overlap.text()) ,threshold=float(self.thresholdSpin.text()), exclude_border = squaresize)
            self.table.setItem(int(self.numLayers.text()) +1 , 4, QtWidgets.QTableWidgetItem(str(len(self.BLUEblobs))))
        if str(self.fMarker.currentText())  == 'GFP':
            blobs = blob_log(self.GREENimage,  max_sigma=int(self.maxSigSpin.text()), num_sigma=10, min_sigma = int(self.minSigSpin.text()),overlap = float(self.log_overlap.text()) ,threshold=float(self.thresholdSpin.text()), exclude_border = squaresize)
            self.table.setItem(int(self.numLayers.text()) +1 , 4, QtWidgets.QTableWidgetItem(str(len(self.BLUEblobs))))
        if str(self.fMarker.currentText())  == 'GFP or RFP':
            intermediary_fig = self.REDimage + self.GREENimage.astype(float)
            intermediary_fig = 255*(intermediary_fig - intermediary_fig.min())/ (intermediary_fig.max() - intermediary_fig.min())
            blobs = blob_log(intermediary_fig.astype('uint8'),  max_sigma=int(self.maxSigSpin.text()), num_sigma=10, min_sigma = int(self.minSigSpin.text()),overlap = float(self.log_overlap.text()) ,threshold=float(self.thresholdSpin.text()), exclude_border = squaresize)
            self.table.setItem(int(self.numLayers.text()) +1 , 4, QtWidgets.QTableWidgetItem(str(len(self.BLUEblobs))))
        if str(self.fMarker.currentText())  == 'GFP and RFP':
            intermediary_fig = self.REDimage * self.GREENimage.astype(float)
            intermediary_fig = 255*(intermediary_fig - intermediary_fig.min())/ (intermediary_fig.max() - intermediary_fig.min())
            blobs = blob_log(intermediary_fig.astype('uint8'),  max_sigma=int(self.maxSigSpin.text()), num_sigma=10, min_sigma = int(self.minSigSpin.text()),overlap = float(self.log_overlap.text()) ,threshold=float(self.thresholdSpin.text()), exclude_border = squaresize)
            self.table.setItem(int(self.numLayers.text()) + 1 , 4, QtWidgets.QTableWidgetItem(str(len(self.BLUEblobs))))
        if str(self.fMarker.currentText())  == 'Orange':
            blobs = blob_log(self.ORANGEimage.astype('uint8'),  max_sigma=int(self.maxSigSpin.text()), num_sigma=10, min_sigma = int(self.minSigSpin.text()),overlap = float(self.log_overlap.text()) ,threshold=float(self.thresholdSpin.text()), exclude_border = squaresize)
            self.table.setItem(int(self.numLayers.text()) + 1 , 4, QtWidgets.QTableWidgetItem(str(len(self.BLUEblobs))))
        #blobsDAPI = blob_log(self.BLUEimage[squaresize:-squaresize,squaresize:-squaresize],  max_sigma=10, num_sigma=10, min_sigma = 3, threshold=.1)
        self.THEblobs = blobs
        print(blobs.shape)
        self.nMarkedCells.setText(str(len(blobs)))
        self.table.setItem(int(self.numLayers.text()) +1 , 1, QtWidgets.QTableWidgetItem(str(len(blobs))))
        #self.table.setItem(9 , 2, QtWidgets.QTableWidgetItem(str(len(blobsDAPI))))
        if float(self.table.item(int(self.numLayers.text()) +1,2).text()) != 0:
            self.table.setItem(int(self.numLayers.text()) +1 , 3, QtWidgets.QTableWidgetItem(str(float(self.table.item(int(self.numLayers.text()) +1,1).text())/float(self.table.item(int(self.numLayers.text()) +1,2).text()))))
        self.ImgAddPatches()

    def ImgAddPatches(self):
        colors = ['w', 'r', 'g', 'y', 'w', 'r', 'g', 'y', 'orange', 'w', 'r'] *100
        squaresize = self.cropsize
        close(self.fig)
        self.fig, ax = subplots(1, 1)
        ax.imshow(self.THEimage)
        ax.axis('off')
        subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

        while self.table.rowCount() < int(self.numLayers.text())+2: self.table.insertRow(0)
        while self.table.rowCount() > int(self.numLayers.text())+2: self.table.removeRow(0)
        for num, layer in enumerate( [str(x+1) for x in range(int(self.numLayers.text()))] + ['Total selected reg', 'Total image']):
            self.table.setItem(num , 0, QtWidgets.QTableWidgetItem(layer))
            self.table.setItem(num , 1, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 2, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 3, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 4, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(num , 5, QtWidgets.QTableWidgetItem("0"))

        self.table.setItem(int(self.numLayers.text())+1 , 1, QtWidgets.QTableWidgetItem(str(len(self.THEblobs))))
        self.table.setItem(int(self.numLayers.text()) +1 , 4, QtWidgets.QTableWidgetItem(str(len(self.BLUEblobs))))
        if float(self.table.item(int(self.numLayers.text()) +1,4).text()) > 0:
            self.table.setItem(int(self.numLayers.text()) +1 , 5, QtWidgets.QTableWidgetItem(str(float(self.table.item(int(self.numLayers.text()) +1,1).text())/float(self.table.item(int(self.numLayers.text()) +1,4).text()))[:10]))

        if 0 not in self.guidePoints.values():
            ctr = 0
            polygonListCount = array([0 for i in self.polygonList])
            #print('pollistcount before:'+str(polygonListCount))
            for number, blob in enumerate(self.THEblobs):
                y, x, r = blob
                blobPoint = Point(y,x)
                if self.bigpoligon.contains(blobPoint):
                    ctr+= 1
                    whichpolygon = [1  if x.contains(blobPoint) else 0  for x in self.polygonList]
                    polygonListCount += array(whichpolygon)
                    #print('pollistcount:'+str(polygonListCount))
                    #c = Rectangle((x + int(squaresize/2), y + int(squaresize/2)),squaresize,squaresize, color=colors[whichpolygon.index(1)], linewidth=.5, alpha = 0.3)
                    if r - int(self.cellMarkerSize.text()) > 0:
                        c = Circle((x,y), r+ int(self.cellMarkerSize.text()) if r+ int(self.cellMarkerSize.text())<squaresize else squaresize, color=colors[whichpolygon.index(1)], linewidth=2.5, ec = 'red', alpha = 0.15)
                        ax.add_patch(c)
                    ax.text(x,y, polygonListCount[whichpolygon.index(1)], color = 'white', fontsize = 10)
            self.nMarkedCells.setText(str(ctr) )
            self.table.setItem(int(self.numLayers.text()) +1 , 2, QtWidgets.QTableWidgetItem(str(self.imgPolygon.area/self.bigpoligon.area)[:4]))
            self.table.setItem( int(self.numLayers.text()), 2, QtWidgets.QTableWidgetItem(str(int(self.bigpoligon.area/self.bigpoligon.area))))
            self.table.setItem(int(self.numLayers.text()) , 1, QtWidgets.QTableWidgetItem(str(ctr)))

            self.table.setItem(int(self.numLayers.text()) , 3, QtWidgets.QTableWidgetItem(str(ctr)))
            self.table.setItem(int(self.numLayers.text()) +1 , 3, QtWidgets.QTableWidgetItem(str(float(self.table.item(int(self.numLayers.text()) +1,1).text())/float(self.table.item(int(self.numLayers.text()) +1,2).text()))[:6]))

            for n, pol in enumerate(self.polygonList):
                self.table.setItem(n, 2, QtWidgets.QTableWidgetItem(str(pol.area/self.bigpoligon.area)[:4]))
                self.table.setItem(n, 3, QtWidgets.QTableWidgetItem(str(polygonListCount[n]/(pol.area/self.bigpoligon.area))[:6]))
                self.table.setItem(n, 1, QtWidgets.QTableWidgetItem(str(polygonListCount[n])))

            #### add blue cells to dapi count
            ctrDAPI = 0
            polygonListCountDAPI = array([0 for i in self.polygonList])
            for number, blob in enumerate(self.BLUEblobs):
                y, x, r = blob
                blobPoint = Point(y,x)
                if self.bigpoligon.contains(blobPoint):
                    ctrDAPI+= 1
                    whichpolygonDAPI = [1  if x.contains(blobPoint) else 0  for x in self.polygonList]
                    polygonListCountDAPI += array(whichpolygonDAPI)

            self.table.setItem(int(self.numLayers.text()) , 4, QtWidgets.QTableWidgetItem(str(ctrDAPI)))
            if float(self.table.item(int(self.numLayers.text()),4).text())>0: self.table.setItem(int(self.numLayers.text()) , 5, QtWidgets.QTableWidgetItem(str(float(self.table.item(int(self.numLayers.text()),1).text())/ctrDAPI)))

            for n, pol in enumerate(self.polygonList):
                self.table.setItem(n, 5, QtWidgets.QTableWidgetItem(str(polygonListCount[n]/polygonListCountDAPI[n])[:6]))
                self.table.setItem(n, 4, QtWidgets.QTableWidgetItem(str(polygonListCountDAPI[n])))



        if 0 in self.guidePoints.values():
            for number, blob in enumerate(self.THEblobs):
                y, x, r = blob
                #c = Rectangle((x + int(squaresize/2), y + int(squaresize/2)),squaresize,squaresize, color='gray', linewidth=.5, alpha = 0.3)
                if r + int(self.cellMarkerSize.text()) > 0:
                    c = Circle((x,y), r+ int(self.cellMarkerSize.text()) if r+ int(self.cellMarkerSize.text())<squaresize else squaresize, color='gray',ec= 'white' ,linewidth=1,  alpha = 0.3)
                    ax.add_patch(c)
                #c = Circle((x,y), r+10 if r+10<squaresize else squaresize, color='gray', linewidth=.5, alpha = 0.3)

                ax.text(x,y, str(number), color = 'white', fontsize = 6)
        for number, key in enumerate(self.guidePoints):
            if self.guidePoints[key] != 0:
                ax.add_patch(Circle(self.guidePoints[key][::-1], int(self.numLayers.text()), color='w', linewidth=2, fill=True))
                ax.text(self.guidePoints[key][1]-7,self.guidePoints[key][0]+5, key, color = 'firebrick', fontsize = 10) #add here number of guide point

        if self.guidePoints['TR'] != 0 and self.guidePoints['TL'] != 0: ax.plot([self.guidePoints['TR'][1],self.guidePoints['TL'][1]]
                                                                                , [self.guidePoints['TR'][0],self.guidePoints['TL'][0]], '-', color='w', linewidth=2)
        if self.guidePoints['TL'] != 0 and self.guidePoints['BL'] != 0: ax.plot([self.guidePoints['TL'][1],self.guidePoints['BL'][1]]
                                                                                , [self.guidePoints['TL'][0],self.guidePoints['BL'][0]], '-', color='w', linewidth=2)
        if self.guidePoints['BR'] != 0 and self.guidePoints['BL'] != 0: ax.plot([self.guidePoints['BR'][1],self.guidePoints['BL'][1]]
                                                                                , [self.guidePoints['BR'][0],self.guidePoints['BL'][0]], '-', color='w', linewidth=2)
        if self.guidePoints['TR'] != 0 and self.guidePoints['BR'] != 0: ax.plot([self.guidePoints['TR'][1],self.guidePoints['BR'][1]]
                                                                                , [self.guidePoints['TR'][0],self.guidePoints['BR'][0]], '-', color='w', linewidth=2)

        if 0 not in self.guidePoints.values():
            for i in range(len(self.innergridLeft)):
                ax.plot([self.innergridRight[i][1], self.innergridLeft[i][1]], [self.innergridRight[i][0], self.innergridLeft[i][0]], '-', color = 'w', linewidth = 1)
        ax.axis('off')
        subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        for item in [self.fig, ax]:
            item.patch.set_visible(False)
        self.changeFIGURE(self.fig)



    def create_csv(self):
        layer  = np.array([str(self.table.item(i,0).text())  for i in range(self.table.rowCount() ) ])
        fcells  = np.array([str(self.table.item(i,1).text())  for i in range(self.table.rowCount() ) ])
        area  = np.array([str(self.table.item(i,2).text())  for i in range(self.table.rowCount() ) ])
        density  = np.array([str(self.table.item(i,3).text())  for i in range(self.table.rowCount() ) ])
        nucleiCount = np.array([str(self.table.item(i,4).text())  for i in range(self.table.rowCount() ) ])
        transfectedRatio = np.array([str(self.table.item(i,5).text())  for i in range(self.table.rowCount() ) ])
        classtable = DataFrame( np.transpose(np.vstack((layer, fcells,area, density, nucleiCount, transfectedRatio))))#, index=dates, columns=[nome , classe])
        print(classtable)
        saveclassification = classtable.to_csv(self.figname +'_count.csv',index=False,header=['layers','Fluorescent cells'
        , 'Area', 'Density', 'DAPI cell count', 'Transfection efficiency' ])




app = QtWidgets.QApplication(sys.argv)
myWindow = MainWindow()
myWindow.show()
app.exec_()
