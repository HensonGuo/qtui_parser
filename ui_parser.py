#-*- coding:utf8 -*-

from xml.etree.ElementTree import parse
from PyQt4 import QtGui, QtCore
from ui_properties import UIProperties


class UIParser(object):

    def __init__(self):
        super(UIParser, self).__init__()
        self._uiprops = UIProperties()
        self._handerMap = {
            "widget":self.createWidget,
            "layout":self.createLayout,
            "item": self.createItem,
            "spacer": self.createSpacer,
        }
        self._debug = False
        self._widget = None

    def setDebug(self, bool):
        self._debug = bool
        self._uiprops.setDebug(bool)

    def parse(self, uifile, res_prefix, parentWidget=None):
        self._widget = None
        self._resPrefix = res_prefix
        content = parse(uifile)
        root = content.getroot()
        self.everySubTrees(root, parentWidget)
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
        self._uiprops.setProperties(widget, widgetElement)
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

        margin = self._uiprops.getProperty(layoutElement, "margin", 0)
        layout.setMargin(margin)

        self._uiprops.setProperties(layout, layoutElement)
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

    def getObjectName(self, element):
        className = element.attrib["class"]
        objectName = element.attrib["name"]
        if not objectName:
            objectName = className[0].lower() + className[1:]
        return objectName

    def printCreateOject(self, obj, createModule, parent):
        if not self._debug:
            return
        if parent is None:
            return
        if isinstance(obj, QtGui.QSpacerItem):
            orienD = obj.expandingDirections()
            hPolicy = "QtGui.QSizePolicy.Expanding" \
                if orienD == QtCore.Qt.Horizontal else "QtGui.QSizePolicy.Minimum"
            vPolicy = "QtGui.QSizePolicy.Minimum" \
                if orienD == QtCore.Qt.Horizontal else "QtGui.QSizePolicy.Expanding"
            print "\nspacerItem = QtGui.QSpacerItem(%d, %d, %s, %s)" % \
                  (obj.sizeHint().width(), obj.sizeHint().height(), hPolicy, vPolicy)
            print "%s.addItem(spacerItem)" % (parent.objectName())
            return

        print "\n%s = %s" % (obj.objectName(), createModule)
        print "%s.setObjectName(%s)" % (obj.objectName(), obj.objectName())
        if isinstance(parent, QtGui.QLayout):
            if isinstance(obj, QtGui.QLayout):
                print "%s.addLayout(%s)" % (parent.objectName(), obj.objectName())
            else:
                print "%s.addWidget(%s)" % (parent.objectName(), obj.objectName())
        else:
            if isinstance(obj, QtGui.QLayout):
                print "%s.setLayout(%s)" % (parent.objectName(), obj.objectName())
            else:
                print "%s.setParent(%s)" % (obj.objectName(), parent.objectName())




if __name__ == "__main__":
    import sys
    from ui_finder import UiFinder
    app = QtGui.QApplication(sys.argv)
    uiparser = UIParser()
    uiparser.setDebug(True)
    widget = uiparser.parse(r"D:\Work\apps_wonderful\transformer\gamelive\ent_vote\entertainment_vote\ui\mainwidget.ui", None)
    # verticalLayout_3 = UiFinder.findQLayout(widget, "verticalLayout_3")
    # verticalLayout_3.setMargin(0)
    widget.show()
    app.exec_()