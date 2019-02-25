# -*- coding: utf-8 -*-
"""
Spyder Editor

PyDICOM Broswer using PyDICOM and objbrowser
"""


import objbrowser
import pydicom
#import sys
from objbrowser.qtpy import QtWidgets
from objbrowser.version import DEBUGGING, PROGRAM_NAME
from objbrowser.attribute_model import (AttributeModel, safe_data_fn, 
                                        DEFAULT_ATTR_DETAILS, SMALL_COL_WIDTH,
                                        ATTR_MODEL_NAME, ATTR_MODEL_PATH)

ATTR_TAG_KEYWORD = AttributeModel('Tag Name',
    doc         = "The dicom tag keyword if known.", 
    data_fn     = safe_data_fn(lambda obj: obj.keyword),
    col_visible = True,  
    width       = SMALL_COL_WIDTH)

ATTR_DCM_VM = AttributeModel('VM',
    doc         = "DICOM Value Multiplicity.", 
    data_fn     = safe_data_fn(lambda obj: obj.VM),
    col_visible = True,  
    width       = SMALL_COL_WIDTH)

ATTR_DCM_VR = AttributeModel('VR',
    doc         = "DICOM Value Representation. (str, int, etc.)", 
    data_fn     = safe_data_fn(lambda obj: obj.VR),
    col_visible = True,  
    width       = SMALL_COL_WIDTH)

ATTR_DCM_VALUE = AttributeModel('VR',
    doc         = "DICOM Value Representation. (str, int, etc.)", 
    data_fn     = safe_data_fn(lambda obj: str(obj.value)),
    col_visible = True,  
    width       = SMALL_COL_WIDTH)

DEFAULT_DCM_ATTR_COLS = (
    ATTR_MODEL_NAME,
    ATTR_MODEL_PATH,
    ATTR_TAG_KEYWORD, 
    ATTR_DCM_VM,
    ATTR_DCM_VR,
    ATTR_DCM_VALUE
)

class DCMObj_Browser(objbrowser.ObjectBrowser):
    def __init__(self, obj,
                 name = '',
                 attribute_columns = DEFAULT_DCM_ATTR_COLS,
                 attribute_details = DEFAULT_ATTR_DETAILS,
                 show_callable_attributes = False,
                 show_special_attributes = False,
                 auto_refresh = False,
                 refresh_rate = None,  # None uses value from QSettings
                 reset = False):
        """ Constructor
        
            :param obj: any Python object or variable
            :param name: name of the object as it will appear in the root node
            :param attribute_columns: list of AttributeColumn objects that define which columns
                are present in the table and their defaults
            :param attribute_details: list of AttributeDetails objects that define which attributes
                can be selected in the details pane.
            :param show_callable_attributes: if True rows where the 'is attribute' and 'is callable'
                columns are both True, are displayed. Otherwise they are hidden. 
            :param show_special_attributes: if True rows where the 'is attribute' is True and
                the object name starts and ends with two underscores, are displayed. Otherwise 
                they are hidden.
            :param auto_refresh: If True, the contents refershes itsef every <refresh_rate> seconds.
            :param refresh_rate: number of seconds between automatic refreshes. Default = 2 .
            :param reset: If true the persistent settings, such as column widths, are reset. 
        """
        

        
        super(DCMObj_Browser, self).__init__(obj, name, attribute_columns, 
                 attribute_details, show_callable_attributes, 
                 show_special_attributes, auto_refresh, refresh_rate, reset)
    
    def _setup_menu(self):
        """ Sets up the main menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("&Open", self.getDCMtree_dialog, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("C&lose", self.close, "Ctrl+W")
        file_menu.addAction("E&xit", self.quit_application, "Ctrl+Q")
        if DEBUGGING is True:
            file_menu.addSeparator()
            file_menu.addAction("&Test", self.my_test, "Ctrl+T")
        
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction("&Refresh", self.refresh, "Ctrl+R")
        view_menu.addAction(self.toggle_auto_refresh_action)
        
        view_menu.addSeparator()
        self.show_cols_submenu = view_menu.addMenu("Table columns")
        view_menu.addSeparator()
        view_menu.addAction(self.toggle_callable_action)
        view_menu.addAction(self.toggle_special_attribute_action)
        
        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About', self.about)
    
    
    def _setup_menu_open_notused(self):
        
        super(DCMObj_Browser, self)._setup_menu()
        
        openaction = QtWidgets.QAction(self, text="&Open", shortcut="Ctrl+O")
        openaction.triggered.connect(self.getDCMtree_dialog)
    
        filemenu = next((x for x in 
                         self.menuBar().findChildren(QtWidgets.QMenu) 
                         if x.title() == "&File"))
        fm_first = filemenu.findChildren(QtWidgets.QAction)[0]
        newsep = filemenu.insertSeparator(fm_first)
        filemenu.insertAction(openaction, newsep)

    def getDCMtree_dialog(self):
        dcmdata = None
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 
                                   "Select DICOM file to read...", "", 
                                   "DICOM files (*.dcm);;All files (*)")[0]
        try:
            dcmdata = pydicom.dcmread(filename)
        except pydicom.errors.InvalidDicomError:
            pass
        #self._tree_model = objbrowser.treemodel.TreeModel(dcmdata, filename)
        self._tree_model.populateTree(dcmdata, "<root>")
        self.refresh()
        self.setWindowTitle("{} - {}".format(PROGRAM_NAME, filename))
        


if __name__ ==  '__main__':
    
    DCMObj_Browser.browse([])
    