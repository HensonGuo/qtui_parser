#-*- coding:utf8 -*-

from PyQt4 import QtGui, QtCore
from xml.etree.ElementTree import parse, XMLParser, TreeBuilder
from ui_properties import UIProperties
from ui_finder import UiFinder
import time


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

    def getXmlTree(self, uifile):
        file = QtCore.QFile(uifile)
        if not file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text):
            return None
        source = file.readAll()
        file.close()
        parser = XMLParser(target=TreeBuilder())
        parser.feed(source)
        return parser.close()

    def parse(self, uifile, loadRes=False, parentWidget=None, debug=False):
        uifile= uifile.replace("\\", "/")
        self.setDebug(debug)
        self._widget = None
        self._xmlTree = self.getXmlTree(uifile)
        past = time.time()
        if loadRes:
            self.readResources(self._xmlTree.find("resources"), uifile[0:uifile.rfind("/")])
        self.createWidget(self._xmlTree.find("widget"), parentWidget)
        cost = time.time() - past
        self.printLog("\ncreate widgets cost %ds" % cost)
        self.createConnections(self._xmlTree.find("connections"))
        del self._xmlTree
        self._xmlTree = None
        return self._widget

    def everySubTrees(self, widgetElement, parent):
        for child in iter(widgetElement):
            try:
                handler = self._handerMap[child.tag]
            except KeyError:
                continue
            handler(child, parent)

    def handleZOrder(self, widgetElement):
        zorders = widgetElement.findall("zorder")
        if not zorders:
            return
        childWidgetMap = {}
        insertChildIndex = -1
        for index, child in enumerate(widgetElement.getchildren()):
            if child.tag == "widget":
                childWidgetMap[child.attrib["name"]] = child
            if insertChildIndex == -1:
                insertChildIndex = index
        for zorder in zorders:
            name = zorder.text
            widget = childWidgetMap.get(name)
            if not widget:
                continue
            widgetElement.remove(widget)
            widgetElement.insert(insertChildIndex, widget)
            insertChildIndex += 1

    def createWidget(self, widgetElement, parent):
        self.handleZOrder(widgetElement)
        className = widgetElement.attrib["class"]
        objName = self.getObjectName(widgetElement)
        if className == "Line":
            return self.createLine(widgetElement, parent)
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

    def createLine(self, lineElement, parent):
        line = QtGui.QFrame(parent)
        line.setObjectName(self.getObjectName(lineElement))
        orientation = self._uiprops.findAttrib("property", lineElement, "orientation")
        if orientation == QtCore.Qt.Horizontal:
            line.setFrameShape(QtGui.QFrame.HLine)
        else:
            line.setFrameShape(QtGui.QFrame.VLine)
        self.printCreateOject(line, "QtGui.QFrame", parent)
        self.everySubTrees(lineElement, line)

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

    def createConnections(self, connections):
        for element in iter(connections):
            senderName = self._uiprops.findAttrib("sender", element)
            sender = UiFinder.findQWidget(self._widget, senderName)
            signalName = self._uiprops.findAttrib("signal", element)
            receiverName = self._uiprops.findAttrib("receiver", element)
            receiver = UiFinder.findQWidget(self._widget, receiverName)
            slotName = self._uiprops.findAttrib("slot", element)
            getattr(sender, signalName[0:-2]).connect(getattr(receiver, slotName[0:-2]))

    def applyProperty(self, propertyElement, target):
        self._uiprops.setProperty(target, propertyElement)

    def applyAttribute(self, attrElement, target):
        attribName =  attrElement.attrib["name"]
        if attribName == "buttonGroup":
            buttonGroupName = self._uiprops.getPropertySetterValue(attrElement)
            buttonGroup = self.getButtonGroup(buttonGroupName)
            if not buttonGroup:
                self.printLog("warning: not exist buttongroup %s" % buttonGroupName)
                return
            buttonGroup.addButton(target)
        else:
            # todo 不支持的后续再做支持
            self.printLog("warning: not support attrib %s" % attribName)

    def readResources(self, resElement, resDir):
        self._resMap = {}
        for item in iter(resElement):
            location = item.attrib.get("location")
            self.loadQrcFile(location, resDir)
        self._uiprops.setResources(self._resMap)

    def loadQrcFile(self, qrcFile, resDir):
        qrcFilePath = resDir + "/" + qrcFile
        xmlTree = self.getXmlTree(qrcFilePath)
        for resItem in iter(xmlTree):
            prefix = resItem.attrib.get("prefix")
            self.recordResources(prefix, resItem, qrcFilePath[0:qrcFilePath.rfind("/")])

    def recordResources(self, prefix, qrcElements, resDir):
        for element in iter(qrcElements):
            self._resMap[":/%s/%s" % (prefix, element.text)] = "%s/%s" % (resDir.replace("\\", "/"), element.text)

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
    # import img_rc
    widget = uiparser.parse(r"D:\Work\apps_wonderful\resource\gamelive_right_region\fan_badge\fans_club.ui", loadRes=True, debug=True)
    widget.show()
    widget.move(500, 500)
    app.exec_()