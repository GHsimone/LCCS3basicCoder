# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LCCS3_BasicCoderDialog
                                 A QGIS plugin
 The plugin loads a LCCS3 legend, creates a form with all LCCS3 classes and allows the user to code selected polygons
                             -------------------
        begin                : 2015-04-16
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Simone Maffei
        email                : simone.maffei@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui, uic
from qgis.core import *
from qgis.gui import *

import os
import config
import xml.sax
import time

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'lccs3_basiccoder_dialog_base.ui'))


class LCCS3_BasicCoderDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(LCCS3_BasicCoderDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # remove "?" tool button	
        flags = self.windowFlags()
        helpFlag = QtCore.Qt.WindowContextHelpButtonHint
        flags = flags & (~helpFlag)
        self.setWindowFlags(flags)

        # make connections between CUSTOM ACTIONS and FUNCTIONS
        self.actionSelectLegend.triggered.connect(self.eventSelectLegend)
        self.actionSelectClass.triggered.connect(self.eventSelectClass)
        self.actionReloadColumns.triggered.connect(self.eventRefreshAttributes)
        self.actionSelectColumn.triggered.connect(self.eventSelectColumn)

    def clearListClasses(self):
        self.lstClasses.clear()
    def addListClasses(self):
        n = 0
        if len(config.LCCS3classes) > 0:
            for aClass in config.LCCS3classes:
                n = n + 1
                #self.lstClasses.addItem(aClass.mapcode)
                if aClass.dominantuuid is None:
                    self.lstClasses.addItem(aClass.mapcode + ' (' + aClass.name + ')')
                else:
                    self.lstClasses.addItem(aClass.mapcode + ' (MIXED: ' + aClass.name + ')')
                self.lstClasses.item(n-1).setToolTip(aClass.description)
                QgsMessageLog.logMessage(aClass.mapcode + ' - ' + aClass.name + ' (' + aClass.description + ')')

    def clearListVecLayers(self):
        config.DictLayers = dict()
        self.cbLayers.clear()
        self.cbLayers.addItem(config.myNone)
    def addListVecLayers(self):
        if len(config.DictLayers) > 0:
            for aName, aLayer in  config.DictLayers.iteritems():
                self.cbLayers.addItem(aLayer.name())
                QgsMessageLog.logMessage(aLayer.name())
    def getVecLayer(self):
        return self.cbLayers.currentText()

    def clearListAttributes(self):
        config.CurLayerAttributes = []
        self.cbAttributes.clear()
        self.cbAttributes.addItem(config.myNone)
    def addListAttributes(self):
        if len(config.CurLayerAttributes) > 0:
            for aAttr in config.CurLayerAttributes:
                self.cbAttributes.addItem(aAttr)
                QgsMessageLog.logMessage(aAttr)
    def getAttribute(self):
        return self.cbAttributes.currentText()

    def setStatusMessage(self, amsg):
        self.lbStatusBar.setText(amsg)
    def clearStatusMessage(self):
        self.lbStatusBar.clear()

    # --------------------------------------------------

    #####################################
    # select and load a LCCS3 legend file
    #####################################
    def eventSelectLegend(self):

        # select LCCS3 legend file
        # ------------------------
        aFileFilter = config.FileFilter
        config.LCCS3legendFile = QtGui.QFileDialog.getOpenFileName(None,config.SelectLCCS3legend,config.LCCS3legendFile,aFileFilter)
        if not os.path.isfile(config.LCCS3legendFile):
            config.LCCS3legendFile = ''
            QtGui.QMessageBox.information(None, config.MyTitle, config.NoFileSelected)
            return
        QgsMessageLog.logMessage(config.SelectedLegend + ': ' + config.LCCS3legendFile)
        QtGui.QMessageBox.information(None, config.MyTitle, str(config.SelectedLegend + ': ' + config.LCCS3legendFile))
        self.btLegend.setText(os.path.basename(config.LCCS3legendFile))

        # read selected LCCS3 legend file
        # -------------------------------
        # create an XMLReader
        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        # override the default ContextHandler
        Handler = LCC3legendHandler()
        parser.setContentHandler( Handler )
        # launch the parsing   
        config.LCCS3classes = []
        parser.parse(config.LCCS3legendFile)
        QgsMessageLog.logMessage(config.NumberOfClasses + ': '+ str(config.NumClasses))

        # load LCCS3 classes into dialog's list
        # -------------------------------------
        self.clearListClasses()
        self.addListClasses()
        if config.NumClasses > 0:
            self.setStatusMessage(config.ClassesLoaded + ': ' + str(config.NumClasses))
        else:
            self.setStatusMessage('Ready')
        
    def eventRefreshAttributes(self):
        self.clearListAttributes()
        config.LCCS3columnId = -1
        if self.cbLayers.currentText() != "" and self.cbLayers.currentText() != config.myNone:
            config.LCCS3layer = config.DictLayers[self.cbLayers.currentText()]
            config.myIface.setActiveLayer(config.LCCS3layer)
            fields = config.LCCS3layer.pendingFields()
            config.NumAttributes = 0
            for field in fields:
                if (field.type() == 10): # only strings
                    config.NumAttributes = config.NumAttributes + 1
                    config.CurLayerAttributes.append(field.name())
            self.addListAttributes()
            QgsMessageLog.logMessage(config.CodingSettings + ': ' + config.LCCS3layer.name() + "/" + config.LCCS3column + '(' + str(config.LCCS3columnId) + ')')
            
    def eventSelectColumn(self):
        if self.cbAttributes.currentText() != "" and self.cbAttributes.currentText() != config.myNone:
            config.LCCS3column = self.cbAttributes.currentText()
            fields = config.LCCS3layer.pendingFields()
            aid = -1
            config.LCCS3columnId = -1
            for field in fields:
                aid = aid + 1
                if (field.name() == config.LCCS3column):
                    config.LCCS3columnId = aid
            QgsMessageLog.logMessage(config.CodingSettings + ': ' + config.LCCS3layer.name() + "/" + config.LCCS3column + '(' + str(config.LCCS3columnId) + ')')

    def eventSelectClass(self):
        if self.cbLayers.currentText() != "" and self.cbLayers.currentText() != config.myNone and self.cbAttributes.currentText() != "" and self.cbAttributes.currentText() != config.myNone:
            caps = config.LCCS3layer.dataProvider().capabilities()
            selected_features = config.LCCS3layer.selectedFeatures()

            if caps & QgsVectorDataProvider.ChangeAttributeValues and config.LCCS3columnId >= 0 and len(selected_features) > 0:

                self.setStatusMessage(config.StartCoding)
                self.lbStatusBar.setStyleSheet("QLabel { background-color : green; color : white; }")
                self.lbStatusBar.repaint()
                QgsMessageLog.logMessage(config.StartCoding)

                aList = self.lstClasses.currentItem().text().split(' (')
                config.LCCS3code = aList[0] # self.lstClasses.currentItem().text()
                self.setStatusMessage(config.Coding)
                self.lbStatusBar.repaint()

                # SIMONE: this version does not require layer in editing mode
                #         and update/save the values immediately, but ...
                #         it is much slower
                #attrs = { config.LCCS3columnId : config.LCCS3code }
                #for a_feature in selected_features:
                #    config.LCCS3layer.dataProvider().changeAttributeValues({ a_feature.id() : attrs })

                # SIMONE: this version requires layer in editing mode, and the user
                #         MUST save manually the values. It is much faster
                if not config.LCCS3layer.isEditable():
                    config.LCCS3layer.startEditing()
                for a_feature in selected_features:
                    config.LCCS3layer.changeAttributeValue(a_feature.id(),config.LCCS3columnId,config.LCCS3code,True)

                self.setStatusMessage(str(len(selected_features)) + ' ' + config.FeaturesCodedWithCode + ' ' + str(config.LCCS3code))
                time.sleep(0.3)
                self.lbStatusBar.setStyleSheet("QLabel { }")
                QgsMessageLog.logMessage(str(len(selected_features)) + ' ' + config.FeaturesCodedWithCode + ' ' + str(config.LCCS3code))
            else:
                self.setStatusMessage(config.NoFeatureCoded)
                self.lbStatusBar.setStyleSheet("QLabel { background-color : red; color : white; }")
                self.lbStatusBar.repaint()
                time.sleep(0.3)
                self.lbStatusBar.setStyleSheet("QLabel { }")
                QgsMessageLog.logMessage(config.NoFeatureCoded)


class LCC3legendHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.CurrentData = ''
        self.name = ''
        self.description = ''
        self.mapcode = ''
        self.uuid = ''
        self.ended = True
        config.NumClasses = 0

    # Call when a LCCS3 class starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == 'LC_LandCoverClass':
            if len(attributes) == 3:
                QgsMessageLog.logMessage('**************** ' + config.ClassFound + ' ****************')
                self.name = '<empty>'
                self.description = '<empty>'
                self.mapcode = '<empty>'
                self.uuid = attributes["uuid"]
                self.domuuid = None
                QgsMessageLog.logMessage(config.UUID + ': ' + self.uuid)
                self.ended = False
        elif tag == 'LC_MixedClass':
            if len(attributes) == 4:
                QgsMessageLog.logMessage('**************** ' + config.ClassFound + ' ****************')
                self.name = '<empty>'
                self.description = '<empty>'
                self.mapcode = '<empty>'
                self.uuid = attributes["uuid"]
                self.domuuid = attributes["dominant"]
                QgsMessageLog.logMessage(config.UUID + ': ' + self.uuid + ' (' + self.domuuid + ')')
                self.ended = False

    # Call when an elements ends
    def endElement(self, tag):
        if not self.ended:
            if self.CurrentData == "name":
                QgsMessageLog.logMessage(config.Name + ': ' + self.name)
            elif self.CurrentData == "description":
                QgsMessageLog.logMessage(config.Description + ': ' + self.description)
            elif self.CurrentData == "map_code":
                QgsMessageLog.logMessage(config.MapCode + ': ' + self.mapcode)
                config.NumClasses = config.NumClasses + 1
                config.LCCS3classes.append(LCCS3class(int(config.NumClasses),self.name, self.description, self.mapcode, self.uuid, self.domuuid))
                self.ended = True
        self.CurrentData = ""

    # Call when a character is read
    def characters(self, content):
        if self.CurrentData == "name":
            if self.name == '<empty>':
                self.name = content
        elif self.CurrentData == "description":
            if self.description == '<empty>':
                self.description = content
        elif self.CurrentData == "map_code":
            if self.mapcode == '<empty>':
                self.mapcode = content

class LCCS3class(object):
    """__init__() functions as the class constructor"""
    def __init__(self, item=None, name=None, description=None, mapcode=None, uuid=None, domuuid=None):
        self.item = item
        self.name = name
        self.description = description
        self.mapcode = mapcode
        self.uuid = uuid
        self.dominantuuid = domuuid
