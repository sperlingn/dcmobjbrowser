# -*- coding: utf-8 -*-
"""
Spyder Editor

PyDICOM Broswer using PyDICOM and objbrowser
@author: Nicholas Sperling <Nicholas.Sperling@utoledo.edu>
"""


import objbrowser
import pydicom
from objbrowser.qtpy import QtWidgets
from objbrowser.version import DEBUGGING, PROGRAM_NAME
from objbrowser.attribute_model import (AttributeModel, safe_data_fn,
                                        SMALL_COL_WIDTH, MEDIUM_COL_WIDTH,
                                        ATTR_MODEL_NAME, ATTR_MODEL_PATH,
                                        ATTR_MODEL_REPR)
from DCMTreeModel import DCMTreeModel


def safe_element_value(de):
    if de.VR == 'SQ':
        return str(de.keyword)
    else:
        return str(de.value)


VMVR_COL_WIDTH = 20

ATTR_DCM_KEYWORD = AttributeModel('Tag Name',
    doc         = "The dicom tag keyword if known.", 
    data_fn     = safe_data_fn(lambda obj: obj.keyword),
    col_visible = True,  
    width       = MEDIUM_COL_WIDTH)

ATTR_DCM_VM = AttributeModel('VM',
    doc         = "DICOM Value Multiplicity.", 
    data_fn     = safe_data_fn(lambda obj: obj.VM),
    col_visible = True,  
    width       = VMVR_COL_WIDTH)

ATTR_DCM_VR = AttributeModel('VR',
    doc         = "DICOM Value Representation. (str, int, etc.)", 
    data_fn     = safe_data_fn(lambda obj: obj.VR),
    col_visible = True,  
    width       = VMVR_COL_WIDTH)

ATTR_DCM_VALUE = AttributeModel('Value',
    doc         = "Element Value", 
    data_fn     = safe_data_fn(safe_element_value),
    col_visible = True,  
    width       = SMALL_COL_WIDTH)

DEFAULT_DCM_ATTR_COLS = (
    ATTR_MODEL_NAME,
    ATTR_DCM_VM,
    ATTR_DCM_VR,
    ATTR_DCM_KEYWORD,
    ATTR_DCM_VALUE
)

DEFAULT_ATTR_DETAILS = (
        ATTR_MODEL_PATH,
        ATTR_DCM_KEYWORD,
        ATTR_DCM_VALUE,
        ATTR_MODEL_REPR
)


class DCMObj_Browser(objbrowser.ObjectBrowser):
    def __init__(self, obj=[],
                 name='',
                 attribute_columns=DEFAULT_DCM_ATTR_COLS,
                 attribute_details=DEFAULT_ATTR_DETAILS,
                 show_callable_attributes=False,
                 show_special_attributes=False,
                 auto_refresh=False,
                 refresh_rate=None,  # None uses value from QSettings
                 reset=False):

        super(DCMObj_Browser, self).__init__(obj, name, attribute_columns,
                                             attribute_details,
                                             show_callable_attributes,
                                             show_special_attributes,
                                             auto_refresh, refresh_rate, reset)

        self._tree_model = DCMTreeModel(obj, name, attr_cols=self._attr_cols)

        self._proxy_tree_model.setSourceModel(self._tree_model)

    __init__.__doc__ == objbrowser.ObjectBrowser.__init__.__doc__

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

    def _setup_views(self):
        """ Override creation of setup views to enable StretchLastSection
        """
        super()._setup_views()
        self.obj_tree.header().setStretchLastSection(True)

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
        title = "Select DICOM file to read..."
        filefilter = "DICOM files (*.dcm);;All files (*)"
        filename = QtWidgets.QFileDialog.getOpenFileName(self, title, "",
                                                         filefilter)[0]

        self.update_file(filename)

    def update_file(self, filename):
        try:
            dcmdata = pydicom.dcmread(filename)
        except pydicom.errors.InvalidDicomError:
            pass
        # self._tree_model = objbrowser.treemodel.TreeModel(dcmdata, filename)
        self._tree_model.populateTree(dcmdata, "<root>")
        self.refresh()
        self.setWindowTitle("{} - {}".format(PROGRAM_NAME, filename))




if __name__ == '__main__':
    from sys import argv, exit
    if len(argv) > 1:
        filename=argv[1]
        try:
            dcmdata = pydicom.dcmread(filename)
            DCMObj_Browser.browse(dcmdata, filename+"<root>")
            exit()
        except (pydicom.errors.InvalidDicomError, FileNotFoundError) as e:
            pass
    DCMObj_Browser.browse()

