#-*- coding:utf8 -*-

from PyQt4 import QtGui, QtCore
from xml.etree.ElementTree import parse
from ui_properties import UIProperties
from ui_finder import UiFinder


class UIParser(object):

    def __init__(self):
        super(UIParser, self).__init__()
        self._uiprops = UIProperties()
        self._uiprops.setLogFunc(self.printLog)

        self._handerMap = {
            "widget":self.createWidget,
            "layout":self.createLayout,
            "item": self.createItem,
            "spacer": self.createSpacer,
            "property": self.applyProperty,
            "attribute": self.applyAttribute,
        }

        self._debug = False
        self._xmlTree = None
        self._widget = None

    def setDebug(self, bool):
        self._debug = bool

    def clear(self):
        if self._xmlTree:
            self._xmlTree.deleteLater()
            self._xmlTree = None
        self._widget = None

    def parse(self, uifile, res_prefix, parentWidget=None):
        self._widget = None
        self._resPrefix = res_prefix
        content = parse(uifile)
        self._xmlTree = content.getroot()
        self.createWidget(self._xmlTree.find("widget"), parentWidget)
        return self._widget

    def everySubTrees(self, widgetElement, parent):
        for child in iter(widgetElement):
            try:
                handler = self._handerMap[child.tag]
            except KeyError:
                continue
            handler(child, parent)

    def createWidget(self, widgetElement, parent):
        className = widgetElement.attrib["class"]
        objName = self.getObjectName(widgetElement)
        module = "QtGui.%s()" % className
        widget = eval(module)
        if not self._widget:
            self._widget = widget
        widget.setObjectName(objName)
        if isinstance(parent, QtGui.QLayout) or isinstance(parent, QtGui.QStackedWidget):
            parent.addWidget(widget)
        else:
            widget.setParent(parent)
        self.printCreateOject(widget, module, parent)
        self.everySubTrees(widgetElement, widget)
        return widget

    def createLayout(self, layoutElement, parent):
        className = layoutElement.attrib["class"]
        objName = self.getObjectName(layoutElement)
        module = "QtGui.%s()" % className
        layout = eval(module)
        layout.setObjectName(objName)
        if isinstance(parent, QtGui.QLayout):
            parent.addLayout(layout)
        else:
            parent.setLayout(layout)
        self.printCreateOject(layout, module, parent)

        left = self._uiprops.getProperty(layoutElement, 'leftMargin', -1)
        top = self._uiprops.getProperty(layoutElement, 'topMargin', -1)
        right = self._uiprops.getProperty(layoutElement, 'rightMargin', -1)
        bottom = self._uiprops.getProperty(layoutElement, 'bottomMargin', -1)
        layout.setContentsMargins(left, top, right, bottom)

        margin = self._uiprops.getProperty(layoutElement, "margin", -1)
        if margin == -1:
            layout.setMargin(0)

        self.everySubTrees(layoutElement, layout)
        return layout

    def createItem(self, itemElement, parent):
        if isinstance(parent, QtGui.QLayout):
            self.everySubTrees(itemElement, parent)

    def createSpacer(self, spacerElement, parent):
        sizeType = self._uiprops.getProperty(spacerElement, "sizeType", QtGui.QSizePolicy.Expanding)
        orientation = self._uiprops.getProperty(spacerElement, "orientation")
        size = self._uiprops.getProperty(spacerElement, "sizeHint")
        if orientation == QtCore.Qt.Horizontal:
            spacerItem = QtGui.QSpacerItem(size.width(), size.height(), sizeType, QtGui.QSizePolicy.Minimum)
        else:
            spacerItem = QtGui.QSpacerItem(size.width(), size.height(), QtGui.QSizePolicy.Minimum, sizeType)
        if not isinstance(parent, QtGui.QLayout):
            return
        parent.addItem(spacerItem)
        self.printCreateOject(spacerItem, "QtGui.QSpacerItem", parent)
        return spacerItem

    def createButtonGroup(self, groupName, parent):
        groupElements = self._xmlTree.find("buttongroups")
        for element in iter(groupElements):
            if element.tag != 'buttongroup':
                continue
            objectMame = self.getObjectName(element)
            if objectMame != groupName:
                continue
            buttonGroup = QtGui.QButtonGroup(parent)
            buttonGroup.setObjectName(self.getObjectName(element))
            self.printCreateOject(buttonGroup, "QtGui.QButtonGroup", parent)
            return buttonGroup

    def applyProperty(self, propertyElement, target):
        self._uiprops.setProperties(target, propertyElement)

    def applyAttribute(self, attrElement, target):
        attribName =  attrElement.attrib["name"]
        if attribName == "buttonGroup":
            buttonGroupName = self._uiprops.getPropertySetterValue(attrElement)
            buttonGroup = self.getButtonGroup(buttonGroupName)
            if not buttonGroup:
                self.printLog("not exist buttongroup %s" % buttonGroupName)
                return
            buttonGroup.addButton(target)
        else:
            # todo 不支持的后续再做支持
            self.printLog("not support attrib %s" % attribName)

    def getObjectName(self, element):
        objectName = element.attrib["name"]
        if not objectName:
            className = element.attrib["class"]
            objectName = className[0].lower() + className[1:]
        return objectName

    def getButtonGroup(self, objectName):
        buttonGroup = UiFinder.findQButtonGroup(self._widget, objectName)
        if buttonGroup:
            return buttonGroup
        return self.createButtonGroup(objectName, self._widget)

    def printCreateOject(self, obj, createModule, parent):
        if not self._debug:
            return
        parentObjName = parent.objectName() if parent is not None else "None"
        if isinstance(obj, QtGui.QSpacerItem):
            orienD = obj.expandingDirections()
            hPolicy = "QtGui.QSizePolicy.Expanding" \
                if orienD == QtCore.Qt.Horizontal else "QtGui.QSizePolicy.Minimum"
            vPolicy = "QtGui.QSizePolicy.Minimum" \
                if orienD == QtCore.Qt.Horizontal else "QtGui.QSizePolicy.Expanding"
            self.printLog("\nspacerItem = QtGui.QSpacerItem(%d, %d, %s, %s)" % \
                  (obj.sizeHint().width(), obj.sizeHint().height(), hPolicy, vPolicy))
            self.printLog("%s.addItem(spacerItem)" % (parentObjName))
            return

        self.printLog("\n%s = %s" % (obj.objectName(), createModule))
        self.printLog("%s.setObjectName(%s)" % (obj.objectName(), obj.objectName()))
        if isinstance(parent, QtGui.QLayout):
            if isinstance(obj, QtGui.QLayout):
                self.printLog("%s.addLayout(%s)" % (parentObjName, obj.objectName()))
            else:
                self.printLog("%s.addWidget(%s)" % (parentObjName, obj.objectName()))
        else:
            if isinstance(obj, QtGui.QLayout):
                self.printLog("%s.setLayout(%s)" % (parentObjName, obj.objectName()))
            else:
                self.printLog("%s.setParent(%s)" % (obj.objectName(), parentObjName))

    def printLog(self, msg):
        if self._debug:
            print msg




if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    uiparser = UIParser()
    uiparser.setDebug(True)
    import img_rc
    widget = uiparser.parse(r"D:\Work\apps_wonderful\transformer\gamelive\ent_vote\entertainment_vote\ui\createform.ui", None)
    stackedWidget = UiFinder.findQStackedWidget(widget, "stackedWidget")
    stackedWidget.setCurrentIndex(1)
    widget.show()
    widget.move(500, 500)
    app.exec_()