#!/usr/bin/python3
import matplotlib
matplotlib.use("Qt4Agg", force = True)
from matplotlib.pyplot import *
from skimage.exposure import adjust_gamma
from skimage.color import rgb2gray
from scipy import misc
import PIL.ImageOps
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
style.use('ggplot')
from sys import argv
import pickle
import glob
from PyQt4 import QtCore, QtGui, uic
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
from ast import literal_eval as make_tuple
import re
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from skimage.feature import blob_dog, blob_log
from skimage import io
from math import sqrt
from scipy import misc
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
matplotlib.style.use('ggplot')





form_class = uic.loadUiType("bycells2.ui")[0]
#form_class2 = uic.loadUiType("bycells_classwindow.ui")[0]

class MainWindow(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.cellpoints = np.array([])
        self.FindCells.clicked.connect(self.Id_cells)
        self.AddClassified.clicked.connect(self.create_csv)
        self.imageviewbutton.clicked.connect(self.openMainFig)
        self.cropsize = 25
        self.fig = Figure()
        self.THEimage = np.array([])
        self.BLUEimage = 0
        self.REDimage = 0
        self.GREENimage = 0
        self.THEblobs = np.array([])
        self.table.setColumnCount(4)
        self.layout.addWidget(self.table, 1, 0)
        self.table.setHorizontalHeaderLabels(['Layer', 'fluorescent cells', 'Area', 'density' ])
        for num, layer in enumerate(['VZ','IZ4','IZ3','IZ2','IZ1','CP3', 'CP2', 'CP1', 'Total selected reg', 'Total image']):
            self.table.insertRow(num)
            self.table.setItem(num , 0, QtGui.QTableWidgetItem(layer))
            self.table.setItem(num , 1, QtGui.QTableWidgetItem("0"))
            self.table.setItem(num , 2, QtGui.QTableWidgetItem("0"))
            self.table.setItem(num , 3, QtGui.QTableWidgetItem("0"))

        self.directory = 'singleCells/'
        self.guidePoints = {'TR': 0, 'TL' : 0, 'BL' : 0, 'BR': 0}
        self.innergridRight = [(self.guidePoints['TR']*i+ self.guidePoints['BR']*(8-i))/8 for i in range(1,9)]
        self.innergridLeft = [(self.guidePoints['TL']*i+ self.guidePoints['BL']*(8-i))/8 for i in range(1,9)]
        self.polygonList = []
        self.bigpoligon = 0
        self.figname = 0
        self.imgPolygon =0
        #self.saveDir.setText('singleCells/')

    def openDIRwindow(self):
        dirwindow = allDirectoriesWindow(self)
        dirwindow.exec_()

    def removeCell(self, cellnumber):
        self.THEblobs[cellnumber:-1] = self.THEblobs[cellnumber+1:]
        self.THEblobs = self.THEblobs[:-1]
        self.ImgAddPatches()


    def chooseDirectory(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self)
        self.saveDir.setText(str(directory) + '/')
        self.DatabaseSize.setText(str( len(glob.glob(str(self.saveDir.text())+ '*.png') ) ) )


    def openMainFig(self):
        if self.THEimage.any() == True:
            self.rmmpl()
            self.THEimage = np.array([])
            self.BLUEimage = 0
            for num, layer in enumerate(['VZ','IZ4','IZ3','IZ2','IZ1','CP3', 'CP2', 'CP1', 'Total selected reg', 'Total image']):
                self.table.insertRow(num)
                self.table.setItem(num , 0, QtGui.QTableWidgetItem(layer))
                self.table.setItem(num , 1, QtGui.QTableWidgetItem("0"))
                self.table.setItem(num , 2, QtGui.QTableWidgetItem("0"))
                self.table.setItem(num , 3, QtGui.QTableWidgetItem("0"))
            self.directory = 'singleCells/'
            self.guidePoints = {'TR': 0, 'TL' : 0, 'BL' : 0, 'BR': 0}
            self.innergridRight = [(self.guidePoints['TR']*i+ self.guidePoints['BR']*(8-i))/8 for i in range(1,9)]
            self.innergridLeft = [(self.guidePoints['TL']*i+ self.guidePoints['BL']*(8-i))/8 for i in range(1,9)]
            self.polygonList = []
            self.bigpoligon = 0
            self.nMarkedCells.setText(str(0))
            self.THEblobs = np.array([])

        name = QtGui.QFileDialog.getOpenFileName(self, 'Single File', '~/Desktop/', "Image files (*.jpg *.png *.tif)")
        self.figname = str(name)
        image = misc.imread(str(name))
        #self.saveNames.setText(str(name).split("/")[-1][:-4] + 'i')
        self.THEimage = image
        self.imgPolygon = Polygon([[0,0],[0,image.shape[1]],[image.shape[0],image.shape[1]],[image.shape[0],0]]  )
        self.BLUEimage = image[:,:,2]
        self.REDimage = image[:,:,0]
        self.GREENimage = image[:,:,1]
        baseimage = self.fig.add_subplot(111)
        baseimage.axis('off')
        baseimage.grid(False)
        baseimage.imshow(image)
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
                self.THEblobs =np.array(self.THEblobs.tolist() + [[int(event.ydata - squaresize), int(event.xdata - squaresize), self.cropsize]])
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
                   self.innergridRight = [(array(self.guidePoints['TR'])*i+ array(self.guidePoints['BR'])*(8-i))/8 for i in range(0,9)]
                   self.innergridLeft = [(array(self.guidePoints['TL'])*i+ array(self.guidePoints['BL'])*(8-i))/8 for i in range(0,9)]
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
                   self.innergridRight = [(array(self.guidePoints['TR'])*i+ array(self.guidePoints['BR'])*(8-i))/8 for i in range(0,9)]
                   self.innergridLeft = [(array(self.guidePoints['TL'])*i+ array(self.guidePoints['BL'])*(8-i))/8 for i in range(0,9)]
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
                   self.innergridRight = [(array(self.guidePoints['TR'])*i+ array(self.guidePoints['BR'])*(8-i))/8 for i in range(0,9)]
                   self.innergridLeft = [(array(self.guidePoints['TL'])*i+ array(self.guidePoints['BL'])*(8-i))/8 for i in range(0,9)]
                   #print(self.innergridLeft, self.innergridRight)
                   self.bigpoligon = Polygon([self.guidePoints['TR'], self.guidePoints['TL'],self.guidePoints['BL'],self.guidePoints['BR']])
                   for i in range(len(self.innergridLeft)-1):
                       self.polygonList += [Polygon([self.innergridRight[i], self.innergridLeft[i],self.innergridLeft[i+1], self.innergridRight[i+1]])]
                self.ImgAddPatches()

            if str(self.rClicktype.currentText()) == 'Add 4th box corner':
                self.guidePoints['BR'] = [int(event.ydata),int(event.xdata)]
                if 0 not in self.guidePoints.values():
                   self.polygonList = []
                   self.innergridRight = [(array(self.guidePoints['TR'])*i+ array(self.guidePoints['BR'])*(8-i))/8 for i in range(0,9)]
                   self.innergridLeft = [(array(self.guidePoints['TL'])*i+ array(self.guidePoints['BL'])*(8-i))/8 for i in range(0,9)]
                   #print(self.innergridLeft, self.innergridRight)
                   self.bigpoligon = Polygon([self.guidePoints['TR'], self.guidePoints['TL'],self.guidePoints['BL'],self.guidePoints['BR']])
                   #print(self.bigpoligon)
                   for i in range(len(self.innergridLeft)-1):
                       self.polygonList += [Polygon([self.innergridRight[i], self.innergridLeft[i],self.innergridLeft[i+1], self.innergridRight[i+1]])]
                self.ImgAddPatches()
            if str(self.rClicktype.currentText()) == 'Remove cell':
                dist = np.sum((self.THEblobs[:,0:2]+self.cropsize+1-[event.ydata,event.xdata])**2,1)
                if min(dist) < 800:
                    line = dist.tolist().index(min(dist))
                    #print(line)
                    self.removeCell(line)
                    self.nMarkedCells.setText(str(int(self.nMarkedCells.text()) - 1))
                #self.ImgAddPatches()


        elif event.button == 2:
            #print(self.THEblobs[:,0:2])
            dist = np.sum((self.THEblobs[:,0:2]+self.cropsize+1-[event.ydata,event.xdata])**2,1)
            if min(dist) < 800:
                line = dist.tolist().index(min(dist))
                #print(line)
                self.removeCell(line)
                self.nMarkedCells.setText(str(int(self.nMarkedCells.text()) - 1))
            #self.ImgAddPatches()




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
        squaresize = self.cropsize
        image_gray = self.BLUEimage
        if str(self.fMarker.currentText())  == 'RFP':
            blobs = blob_log(self.REDimage[squaresize:-squaresize,squaresize:-squaresize],  max_sigma=10, num_sigma=10, min_sigma = 3, threshold=.1)
        if str(self.fMarker.currentText())  == 'GFP':
            blobs = blob_log(self.GREENimage[squaresize:-squaresize,squaresize:-squaresize],  max_sigma=10, num_sigma=10, min_sigma = 3, threshold=.1)
        if str(self.fMarker.currentText())  == 'GFP or RFP':
            jointImage = self.REDimage + self.GREENimage
            blobs = blob_log(jointImage[squaresize:-squaresize,squaresize:-squaresize],  max_sigma=10, num_sigma=10, min_sigma = 3, threshold=.1)
        #blobsDAPI = blob_log(self.BLUEimage[squaresize:-squaresize,squaresize:-squaresize],  max_sigma=10, num_sigma=10, min_sigma = 3, threshold=.1)
        self.THEblobs = blobs
        self.nMarkedCells.setText(str(len(blobs)))
        self.table.setItem(9 , 1, QtGui.QTableWidgetItem(str(len(blobs))))
        #self.table.setItem(9 , 2, QtGui.QTableWidgetItem(str(len(blobsDAPI))))
        if float(self.table.item(9,2).text()) != 0:
            self.table.setItem(9 , 3, QtGui.QTableWidgetItem(str(float(self.table.item(9,1).text())/float(self.table.item(9,2).text()))))
        #self.table.setRowCount(len(blobs))
        #self.table.setColumnCount(3)
        #self.layout.addWidget(self.table, 1, 0)
        #self.table.setHorizontalHeaderLabels(['index', 'auto class', 'manual class'])
        self.ImgAddPatches()

    def ImgAddPatches(self):
        colors = ['w', 'r', 'g', 'y', 'w', 'r', 'g', 'y', 'orange', 'w', 'r']
        squaresize = self.cropsize
        self.fig, ax = subplots(1, 1)
        ax.imshow(self.THEimage)
        #ax.grid(False)
        ax.axis('off')

        if 0 not in self.guidePoints.values():
            ctr = 0
            polygonListCount = array([0 for i in self.polygonList])
            #print('pollistcount before:'+str(polygonListCount))
            for number, blob in enumerate(self.THEblobs):
                y, x, r = blob
                blobPoint = Point(y+ int(squaresize),x+int(squaresize))
                if self.bigpoligon.contains(blobPoint):
                    ctr+= 1
                    whichpolygon = [1  if x.contains(blobPoint) else 0  for x in self.polygonList ]
                    polygonListCount += array(whichpolygon)
                    #print('pollistcount:'+str(polygonListCount))
                    c = Rectangle((x + int(squaresize/2), y + int(squaresize/2)),squaresize,squaresize, color=colors[whichpolygon.index(1)], linewidth=.5, alpha = 0.3)
                    ax.add_patch(c)
                    ax.text(x+squaresize-self.cropsize/2,y+ squaresize+self.cropsize/2, polygonListCount[whichpolygon.index(1)], color = 'white', fontsize = 6)
            self.nMarkedCells.setText(str(ctr) )
            self.table.setItem(9 , 2, QtGui.QTableWidgetItem(str(self.imgPolygon.area/self.bigpoligon.area)[:4]))
            self.table.setItem( 8, 2, QtGui.QTableWidgetItem(str(int(self.bigpoligon.area/self.bigpoligon.area))))
            self.table.setItem(8 , 1, QtGui.QTableWidgetItem(str(ctr)))
            self.table.setItem(8 , 3, QtGui.QTableWidgetItem(str(ctr)))
            self.table.setItem(9 , 3, QtGui.QTableWidgetItem(str(float(self.table.item(9,1).text())/float(self.table.item(9,2).text()))[:6]))
            for n, pol in enumerate(self.polygonList):
                self.table.setItem(n, 2, QtGui.QTableWidgetItem(str(pol.area/self.bigpoligon.area)[:4]))
                self.table.setItem(n, 3, QtGui.QTableWidgetItem(str(polygonListCount[n]/(pol.area/self.bigpoligon.area))[:6]))
                self.table.setItem(n, 1, QtGui.QTableWidgetItem(str(polygonListCount[n])))

        if 0 in self.guidePoints.values():
            for number, blob in enumerate(self.THEblobs):
                y, x, r = blob
                c = Rectangle((x + int(squaresize/2), y + int(squaresize/2)),squaresize,squaresize, color='gray', linewidth=.5, alpha = 0.3)
                ax.add_patch(c)
                ax.text(x+squaresize-self.cropsize/2,y+ squaresize+self.cropsize/2, str(number), color = 'white', fontsize = 4)
        for number, key in enumerate(self.guidePoints):
            if self.guidePoints[key] != 0:
                ax.add_patch(Circle(self.guidePoints[key][::-1], 8, color='w', linewidth=2, fill=True))

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
        self.changeFIGURE(self.fig)



    def create_csv(self):
        layer  = np.array([str(self.table.item(i,0).text())  for i in range(self.table.rowCount() ) ])
        fcells  = np.array([str(self.table.item(i,1).text())  for i in range(self.table.rowCount() ) ])
        area  = np.array([str(self.table.item(i,2).text())  for i in range(self.table.rowCount() ) ])
        density  = np.array([str(self.table.item(i,3).text())  for i in range(self.table.rowCount() ) ])
        classtable = DataFrame( np.transpose(np.vstack((layer, fcells,area, density))))#, index=dates, columns=[nome , classe])
        print(classtable)
        saveclassification = classtable.to_csv(self.figname +'_count.csv',index=False,header=['layers','Fluorescent cells', 'Area', 'Density'])




app = QtGui.QApplication(sys.argv)
myWindow = MainWindow()
myWindow.show()
app.exec_()
