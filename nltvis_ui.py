# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Wed Dec 17 13:35:07 2014
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_Analysis = QtWidgets.QAction(MainWindow)
        self.actionOpen_Analysis.setObjectName("actionOpen_Analysis")
        self.actionOpen_File_to_Analyze = QtWidgets.QAction(MainWindow)
        self.actionOpen_File_to_Analyze.setObjectName("actionOpen_File_to_Analyze")
        self.actionSave_Analysis = QtWidgets.QAction(MainWindow)
        self.actionSave_Analysis.setObjectName("actionSave_Analysis")
        self.actionSave_Image = QtWidgets.QAction(MainWindow)
        self.actionSave_Image.setObjectName("actionSave_Image")
        self.actionNew_Analysis = QtWidgets.QAction(MainWindow)
        self.actionNew_Analysis.setObjectName("actionNew_Analysis")
        self.menuFile.addAction(self.actionNew_Analysis)
        self.menuFile.addAction(self.actionOpen_Analysis)
        self.menuFile.addAction(self.actionSave_Analysis)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_File_to_Analyze)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Image)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "LaVa"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen_Analysis.setText(_translate("MainWindow", "Open Analysis"))
        self.actionOpen_File_to_Analyze.setText(_translate("MainWindow", "Add File to Analysis"))
        self.actionSave_Analysis.setText(_translate("MainWindow", "Save Analysis"))
        self.actionSave_Image.setText(_translate("MainWindow", "Save Image"))
        self.actionNew_Analysis.setText(_translate("MainWindow", "New Analysis"))

