#-*- coding:utf8 -*-
from PyQt4 import QtGui, QtCore


class UIProperties(object):
    # ignore the propertys
    Ignores = ["leftMargin", "topMargin", "rightMargin", "bottomMargin"]

    def __init__(self, parent):
        self._debug = False

    def setDebug(self, bool):
        self._debug = bool

    def setProperties(self, widget, elem):
        for prop in elem.findall("property"):
            prop_name = prop.attrib["name"]
            if prop_name in UIProperties.Ignores:
                continue
            func_name = self.getPropertySetterName(prop_name)
            func_value = self.getPropertySetterValue(prop)
            try:
                func = getattr(widget, func_name)
                func(func_value)
                if self._debug:
                    print u"{}.{}({})".format(widget.objectName(), func_name, func_value)
            except Exception:
                # todo 不支持的后续再做支持
                print "not support %s" % func_name

    def getProperty(self, elem, name, default=None):
        return self._getChild("property", elem, name, default)

    def _getChild(self, elem_tag, elem, name, default=None):
        for prop in elem.findall(elem_tag):
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
            if tag == "set":
                return func(valueElement, prop.attrib["name"])
            else:
                return func(valueElement)
        except AttributeError:
            # todo 不支持的后续再做支持
            print "not support %s" % func_name

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

    def getSet(self, prop, propName):
        if propName == "alignment":
            alignment = prop.text
            align_flags = None
            for qt_align in alignment.split('|'):
                _, qt_align = qt_align.split('::')
                align = getattr(QtCore.Qt, qt_align)
                if align_flags is None:
                    align_flags = align
                else:
                    align_flags |= align
            return align_flags
        else:
            pass

def int_list(prop):
    return [int(child.text) for child in prop]

def float_list(prop):
    return [float(child.text) for child in prop]