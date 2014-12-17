# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dimension_dialog.ui'
#
# Created: Wed Dec 17 13:35:07 2014
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DimensionDialog(object):
    def setupUi(self, DimensionDialog):
        DimensionDialog.setObjectName("DimensionDialog")
        DimensionDialog.resize(400, 215)
        self.verticalLayout = QtWidgets.QVBoxLayout(DimensionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(DimensionDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.spinBox = QtWidgets.QSpinBox(DimensionDialog)
        self.spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox.setMaximum(10000)
        self.spinBox.setProperty("value", 1000)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(DimensionDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(DimensionDialog)
        self.spinBox_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox_2.setMaximum(10000)
        self.spinBox_2.setProperty("value", 1000)
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout.addWidget(self.spinBox_2, 1, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(DimensionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(DimensionDialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_5 = QtWidgets.QLabel(DimensionDialog)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(DimensionDialog)
        self.doubleSpinBox.setProperty("value", 4.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(DimensionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DimensionDialog)
        self.buttonBox.accepted.connect(DimensionDialog.accept)
        self.buttonBox.rejected.connect(DimensionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DimensionDialog)

    def retranslateUi(self, DimensionDialog):
        _translate = QtCore.QCoreApplication.translate
        DimensionDialog.setWindowTitle(_translate("DimensionDialog", "Dialog"))
        self.label.setText(_translate("DimensionDialog", "Please enter desired image options."))
        self.spinBox.setSuffix(_translate("DimensionDialog", " px"))
        self.label_2.setText(_translate("DimensionDialog", "Width"))
        self.spinBox_2.setSuffix(_translate("DimensionDialog", " px"))
        self.label_3.setText(_translate("DimensionDialog", "x"))
        self.label_4.setText(_translate("DimensionDialog", "Height"))
        self.label_5.setText(_translate("DimensionDialog", "Min. Pixel Size"))
        self.doubleSpinBox.setSuffix(_translate("DimensionDialog", " px"))

