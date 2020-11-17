# -*- coding:utf8 -*-
from PyQt4 import QtCore, QtGui


class UiFinder(QtCore.QObject):

    @staticmethod
    def findQWidget(object, objectName):
        """
        :rtype : QtGui.QWidget
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QWidget, objectName)

    @staticmethod
    def findQLabel(object, objectName):
        """
        :rtype: QtGui.QLabel
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QLabel, objectName)

    @staticmethod
    def findQPushButton(object, objectName):
        """
        :rtype : QtGui.QPushButton
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QPushButton, objectName)

    @staticmethod
    def findQCheckBox(object, objectName):
        """
        :rtype: QtGui.QCheckBox
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QCheckBox, objectName)

    @staticmethod
    def findQComboBox(object, objectName):
        """
        :rtype: QtGui.QComboBox
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QComboBox, objectName)

    @staticmethod
    def findQListView(object, objectName):
        """
        :rtype: QtGui.QListView
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QListView, objectName)

    @staticmethod
    def findQRadioButton(object, objectName):
        """
        :rtype: QtGui.QRadioButton
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QRadioButton, objectName)

    @staticmethod
    def findQScrollBar(object, objectName):
        """
        :rtype: QtGui.QScrollBar
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QScrollBar, objectName)

    @staticmethod
    def findQTextEdit(object, objectName):
        """
        :rtype: QtGui.QTextEdit
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QTextEdit, objectName)

    @staticmethod
    def findQStackedWidget(object, objectName):
        """
        :rtype: QtGui.QStackedWidget
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QStackedWidget, objectName)

    @staticmethod
    def findQLayout(object, objectName):
        """
        :rtype: QtGui.QLayout
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QLayout, objectName)

    @staticmethod
    def findQButtonGroup(object, objectName):
        """
        :rtype: QtGui.QButtonGroup
        """
        if object.objectName() == objectName:
            return object
        return object.findChild(QtGui.QButtonGroup, objectName)