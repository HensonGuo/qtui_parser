# -*- coding:utf8 -*-
from PyQt4 import QtCore, QtGui


class UiFinder(QtCore.QObject):

    @staticmethod
    def findQWidget(object, objectName):
        """
        :rtype : QtGui.QWidget
        """
        return object.findChild(QtGui.QWidget, objectName)

    @staticmethod
    def findQLabel(object, objectName):
        """
        :rtype: QtGui.QLabel
        """
        return object.findChild(QtGui.QLabel, objectName)

    @staticmethod
    def findQPushButton(object, objectName):
        """
        :rtype : QtGui.QPushButton
        """
        return object.findChild(QtGui.QPushButton, objectName)

    @staticmethod
    def findQCheckBox(object, objectName):
        """
        :rtype: QtGui.QCheckBox
        """
        return object.findChild(QtGui.QCheckBox, objectName)

    @staticmethod
    def findQComboBox(object, objectName):
        """
        :rtype: QtGui.QComboBox
        """
        return object.findChild(QtGui.QComboBox, objectName)

    @staticmethod
    def findQListView(object, objectName):
        """
        :rtype: QtGui.QListView
        """
        return object.findChild(QtGui.QListView, objectName)

    @staticmethod
    def findQRadioButton(object, objectName):
        """
        :rtype: QtGui.QRadioButton
        """
        return object.findChild(QtGui.QRadioButton, objectName)

    @staticmethod
    def findQScrollBar(object, objectName):
        """
        :rtype: QtGui.QScrollBar
        """
        return object.findChild(QtGui.QScrollBar, objectName)

    @staticmethod
    def findQTextEdit(object, objectName):
        """
        :rtype: QtGui.QTextEdit
        """
        return object.findChild(QtGui.QTextEdit, objectName)

    @staticmethod
    def findQStackedWidget(object, objectName):
        """
        :rtype: QtGui.QStackedWidget
        """
        return object.findChild(QtGui.QStackedWidget, objectName)