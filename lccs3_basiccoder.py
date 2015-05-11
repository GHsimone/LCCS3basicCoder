# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LCCS3_BasicCoder
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
from PyQt4.QtCore import * # QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import * # QAction, QIcon
from qgis.core import *
from qgis.gui import *
import os.path
import xml.sax
import config

# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from lccs3_basiccoder_dialog import LCCS3_BasicCoderDialog

class LCCS3_BasicCoder:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        config.myIface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LCCS3_BasicCoder_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LCCS3_BasicCoderDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&LCCS3 Basic Coder')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LCCS3_BasicCoder')
        self.toolbar.setObjectName(u'LCCS3_BasicCoder')


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LCCS3_BasicCoder', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
            #self.toolbar.addAction(action)

        if add_to_menu:
            # self.iface.addPluginToVectorMenu(
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LCCS3_BasicCoder/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Open LCCS3 legend'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&LCCS3 Basic Coder'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        self.dlg.close()


    def run(self):
        """Run method that performs all the real work"""

        #####################################
        # select and load a LCCS3 legend file
        #####################################
        self.dlg.eventSelectLegend()

        #########################
        # load the list of layers
        #########################
        layers = self.iface.legendInterface().layers()
        self.dlg.clearListVecLayers()
        config.DictLayers = dict()
        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                config.DictLayers[layer.name()] = layer
        self.dlg.addListVecLayers()
        #QMessageBox.information(None, config.MyTitle, self.iface.activeLayer())
        
        # show the dialog
        self.dlg.show()
        # self.dlg.setWindowFlags(self.dlg.windowFlags() ^ Qt.WindowStaysOnTopHint)

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

