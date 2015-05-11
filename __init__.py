# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LCCS3_BasicCoder
                                 A QGIS plugin
 The plugin loads a LCCS3 legend, creates a form with all LCCS3 classes and allows the user to code selected polygons
                             -------------------
        begin                : 2015-04-16
        copyright            : (C) 2015 by Simone Maffei
        email                : simone.maffei@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load LCCS3_BasicCoder class from file LCCS3_BasicCoder.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .lccs3_basiccoder import LCCS3_BasicCoder
    return LCCS3_BasicCoder(iface)
