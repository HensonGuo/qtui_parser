#-*- coding:utf8 -*-
from PyQt4 import QtGui, QtCore
import re

class UIProperties(object):
    # ignore the propertys
    Ignores = ["leftMargin", "topMargin", "rightMargin", "bottomMargin"]

    def __init__(self):
        self._logFunc = None
        self._loadedResMap = None

    def setLogFunc(self, func):
        self._logFunc = func

    def setProperty(self, ui, prop):
        prop_name = prop.attrib["name"]
        if prop_name in UIProperties.Ignores:
            return
        func_name = self.getPropertySetterName(prop_name)
        func_value = self.getPropertySetterValue(prop)
        try:
            func = getattr(ui, func_name)
            if func_name == "setStyleSheet":
                func_value = self.replaceStyleSheet2LoadedRes(func_value)
            func(func_value)
            self._logFunc(u"{}.{}({})".format(ui.objectName(), func_name, func_value))
        except Exception:
            # todo 不支持的后续再做支持
            self._logFunc("warning: not support %s" % func_name)

    def getProperty(self, elem, name, default=None):
        return self.findAttrib("property", elem, name, default)

    def findAttrib(self, tag, elememt, name=None, default=None):
        for prop in elememt.findall(tag):
            if not name:
                return prop.text
            if prop.attrib["name"] == name:
                return self.getPropertySetterValue(prop)
        else:
            return default

    def getPropertySetterName(self, prop_name):
        return "set%s%s" % (prop_name[0].upper(), prop_name[1:])

    def getPropertySetterValue(self, prop):
        valueElement = prop[0]
        tag = valueElement.tag
        func_name = self.getPropertyGetterName(tag)
        try:
            func = getattr(self, func_name)
            return func(valueElement)
        except AttributeError, error:
            # todo 不支持的后续再做支持
            self._logFunc("warning: not support %s" % error.message)

    def getPropertyGetterName(self, tag):
        return "get%s%s" % (tag[0].upper(), tag[1:])

    def getString(self, prop, notr=None):
        text = prop.text

        if text is None:
            return ""

        if prop.get('notr', notr) == 'true':
            return text

        disambig = prop.get('comment')
        encoding = QtGui.QApplication.UnicodeUTF8
        translated = QtGui.QApplication.translate("", text,
                disambig, encoding)
        return translated

    def getCstring(self, prop):
        return prop.text

    def getNumber(self, prop):
        return int(prop.text)

    def getDouble(self, prop):
        return float(prop.text)

    def getBool(self, prop):
        return prop.text == 'true'

    def getSize(self, prop):
        return QtCore.QSize(*int_list(prop))

    def getSizef(self, prop):
        return QtCore.QSize(*float_list(prop))

    def getPoint(self, prop):
        return QtCore.QPoint(*int_list(prop))

    def getPointf(self, prop):
        return QtCore.QPointF(*float_list(prop))

    def getRect(self, prop):
        return QtCore.QRect(*int_list(prop))

    def getRectf(self, prop):
        return QtCore.QRectF(*float_list(prop))

    def getCursorShape(self, prop):
        return QtGui.QCursor(getattr(QtCore.Qt, prop.text))

    def getSet(self, prop):
        expr = [self.getQtAttr(v) for v in prop.text.split('|')]

        value = expr[0]
        for v in expr[1:]:
            value |= v

        return value

    def getEnum(self, prop):
        return self.getQtAttr(prop.text)

    def getQtAttr(self, propText):
        try:
            prefix, membername = propText.split("::")
        except Exception:
            prefix = "Qt"
            membername = propText

        try:
            module = eval("QtCore.%s" % prefix)
        except Exception:
            try:
                module = eval("QtGui.%s" % prefix)
            except Exception:
                raise AttributeError("unknown attr %s" % propText)
        return getattr(module, membername)

    def getPixmap(self, prop):
        resPath = prop.text
        if self._loadedResMap and resPath in self._loadedResMap:
            resPath = self._loadedResMap[resPath]
        return QtGui.QPixmap(resPath)

    def getFont(self, prop):
        font = QtGui.QFont()
        family = self.findAttrib("family", prop)
        if family:
            font.setFamily(family)
        pointsize = self.findAttrib("pointsize", prop)
        if pointsize:
            font.setPointSize(int(pointsize))
        weight = self.findAttrib("weight", prop)
        if weight:
            font.setWeight(int(weight))
        italic = self.findAttrib("italic", prop)
        if italic:
            font.setItalic(italic=="true")
        bold = self.findAttrib("bold", prop)
        if bold:
            font.setBold(bold == "true")
        underline = self.findAttrib("underline", prop)
        if underline:
            font.setUnderline(underline == "true")
        strikeout = self.findAttrib("strikeout", prop)
        if strikeout:
            font.setStrikeOut(strikeout == "true")
        return font

    def setResources(self, resMap):
        self._loadedResMap = resMap

    def replaceStyleSheet2LoadedRes(self, stylesheet):
        if not self._loadedResMap:
            return stylesheet
        reg = r"url\(.*?\)"
        results = re.findall(reg, stylesheet)
        for result in results:
            oldRes = result[4:-1]
            loadedRes = self._loadedResMap.get(oldRes)
            if not loadedRes:
                continue
            stylesheet = stylesheet.replace(oldRes, loadedRes)
        return stylesheet

def int_list(prop):
    return [int(child.text) for child in prop]

def float_list(prop):
    return [float(child.text) for child in prop]