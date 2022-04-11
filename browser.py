# -*- coding: utf-8 -*-
"""
PyDICOM Broswer using PyDICOM and objbrowser.
@author: Nicholas Sperling <Nicholas.Sperling@utoledo.edu>
"""

"""TODO:

    Reordering the list of items.
    Edit items in the main list
    Add items
    Image viewer
    Diffs
"""



PROGRAM_NAME = "Python DICOM file browser and editor."
PROGRAM_VERSION = 1.0


import objbrowser
import pydicom
#from objbrowser.qtpy import QtWidgets
from PyQt5 import QtWidgets, QtCore
from objbrowser.version import DEBUGGING
from objbrowser.attribute_model import (safe_data_fn, tio_call,
                                        SMALL_COL_WIDTH, MEDIUM_COL_WIDTH,
                                        ATTR_MODEL_NAME, ATTR_MODEL_PATH,
                                        ATTR_MODEL_REPR, logger)
from DCMTreeModel import DCMTreeModel
from AttributeModel import AttributeModel


def element_editable(de):
    try:
        if isinstance(de, pydicom.Dataset) or de.VR == 'SQ':
            return False
        if de.VR in pydicom.dataelem.BINARY_VR_VALUES:
            try:
                if len(de.value) > de.maxBytesToDisplay:
                    return False
            except TypeError:
                pass
            return True
        return isinstance(de, pydicom.dataelem.DataElement)
    except (AttributeError, ValueError) as e:
        print(e)
        pass
    return False


def safe_element_value(de):
    if de.VR == 'SQ':
        return str(de.keyword)
    if not element_editable(de):
        return str(de.repval)
    return str(de.value)


def safe_ti_attribute(tree_item, attr, log_exceptions=False):
    """
    Call getattr(tree_item,attr).

    Returns empty string in case of an error.
    """
    try:
        return str(getattr(tree_item, attr))
    except AttributeError as ex:
        if log_exceptions:
            logger.exception(ex)
        return ""


def safe_ti_write_value(tree_item, value, log_exceptions=False):
    de = tree_item.obj
    try:
        if (isinstance(de, pydicom.dataelem.DataElement) and de.VR != 'SQ' and
                de.VR not in ['OB', 'OD', 'OF', 'OW']):
            de.value = value
    except AttributeError as ex:
        if log_exceptions:
            logger.exception(ex)


VMVR_COL_WIDTH = 20

ATTR_DCM_PATH   = AttributeModel('Dicom Path',
    doc         = "The full path to the item.", 
    data_fn     = lambda tree_item: safe_ti_attribute(tree_item, "dcm_path"),
    col_visible = True,  
    width       = MEDIUM_COL_WIDTH)

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
    data_write_fn = safe_ti_write_value,
    col_visible = True,  
    width       = SMALL_COL_WIDTH,
    editable    = lambda tree_item: tio_call(element_editable, tree_item))

DEFAULT_DCM_ATTR_COLS = (
    ATTR_MODEL_NAME,
    ATTR_DCM_VM,
    ATTR_DCM_VR,
    ATTR_DCM_KEYWORD,
    ATTR_DCM_VALUE
)

DEFAULT_ATTR_DETAILS = (
        ATTR_MODEL_PATH,
        ATTR_DCM_PATH,
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

        self._tree_model = DCMTreeModel(obj, '', attr_cols=self._attr_cols)

        self._proxy_tree_model.setSourceModel(self._tree_model)

        bg_color = self.palette().color(self.palette().Background).name()
        self.setStyleSheet("""[readOnly="true"] {{ background-color: {} }}""".format(bg_color))
        self.file_modified = False
        self.name = name
        self.obj = obj

    __init__.__doc__ = objbrowser.ObjectBrowser.__init__.__doc__


    def _setup_menu(self):
        """ Sets up the main menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("&Open", self.getDCMtree_dialog, "Ctrl+O")
        file_menu.addAction("&Save", self._save_data, "Ctrl+S")
        file_menu.addAction("Save &as", self._saveas_prompt, "F12")
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


    def toggle_editable(self):
        """ Toggles the edit tool to enable editing.
        """
        editable = self.edit_button.isChecked()
        self.editor.setReadOnly(not editable)
        self.modify_widget.setVisible(editable)
        if editable:
            self.editor.setFocus()
        else:
            self.obj_tree.setFocus()
        
        self._change_details_field()


    def cancel_edit(self):
        if self.edit_button.isChecked():
            self.edit_button.click()
        self._change_details_field()


    def apply_edit(self):
        current_index = self.obj_tree.selectionModel().currentIndex()
        tree_item = self._proxy_tree_model.treeItem(current_index)
        button_id = self.button_group.checkedId()
        assert button_id >= 0, "No radio button selected. Please report this bug."

        try:
            editable = self._attr_details[button_id].editable(tree_item)
            print(editable)
        except TypeError as e:
            print(e)
            editable = self._attr_details[button_id].editable
        except AttributeError as e:
            print(e)
            editable = False

        if editable:
            # If this box is marked as editable either through fn or definition, allow write.
            attr_details = self._attr_details[button_id]
            if callable(attr_details.data_write_fn):
                attr_details.data_write_fn(tree_item, self.editor.toPlainText())
            self._tree_model._auxRefreshTree(self._proxy_tree_model.mapToSource(current_index))
            self.edit_button.click()
            self.file_modified = True


    def _setup_views(self):
        """ Override creation of setup views to enable StretchLastSection
        """
        super()._setup_views()
        self.obj_tree.header().setStretchLastSection(True)

        radio_layout = self.button_group.button(0).parent().layout()

        editable_widget = QtWidgets.QWidget()
        editable_layout = QtWidgets.QHBoxLayout()
        editable_layout.setContentsMargins(2, 2, 2, 2)
        editable_widget.setLayout(editable_layout)

        self.edit_button = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView),
                                                 "&Edit")
        self.edit_button.setCheckable(True)
        self.edit_button.clicked.connect(self.toggle_editable)

        modify_widget = QtWidgets.QWidget()
        modify_widget.setVisible(False)
        modify_layout = QtWidgets.QHBoxLayout()
        modify_layout.setContentsMargins(2, 2, 2, 2)
        modify_widget.setLayout(modify_layout)

        apply_button = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton), "")
        apply_button.setShortcut("Ctrl+Return")
        apply_button.clicked.connect(self.apply_edit)

        cancel_button = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton), "")
        cancel_button.setShortcut("Esc")
        cancel_button.clicked.connect(self.cancel_edit)

        modify_layout.addWidget(apply_button)
        modify_layout.addWidget(cancel_button)

        editable_layout.addWidget(self.edit_button)
        editable_layout.addWidget(modify_widget)

        radio_layout.insertWidget(0, editable_widget)

        self.modify_widget = modify_widget

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


    def _file_modified_prompt(self):
        """ File modified since last saved or .  Prompt user.
        """
        title = "Unsaved Changes in {}".format(self.name)
        message = '\n'.join(["There are unsaved changes in the file \"{}\".",
                             "Do you want to save your changes?"]).format(self.name)
        buttons = (QtWidgets.QMessageBox.Save |
                   QtWidgets.QMessageBox.Discard |
                   QtWidgets.QMessageBox.Cancel)
        default_button = QtWidgets.QMessageBox.Save

        return QtWidgets.QMessageBox.warning(self, title, message,
                                             buttons, default_button)


    def _saveas_prompt(self):
        title = "Save as..."
        filefilter = "DICOM files (*.dcm);;All files (*)"
        filename = QtWidgets.QFileDialog.getSaveFileName(self,
                                                         title,
                                                         self.name,
                                                         filefilter)[0]
        if filename == '':
            return False

        self.name = filename

        return self._save_data()


    def _save_data(self):

        try:
            self.obj.save_as(self.name)
        except (AttributeError, ValueError) as e:
            logger.exception(e)
            return False

        self.file_modified = False
        return True


    def getDCMtree_dialog(self):
        if self.file_modified or self.edit_button.isChecked():
            result = self._file_modified_prompt()
            if result == QtWidgets.QMessageBox.Cancel:
                return
            if result == QtWidgets.QMessageBox.Save:
                if not self._saveas_prompt():
                    return

        self._tree_model.beginResetModel()
        self._tree_model.populateTree([], '')
        self._tree_model.endResetModel()

        self.refresh()
        title = "Select DICOM file to read..."
        filefilter = "DICOM files (*.dcm);;All files (*)"
        filename = QtWidgets.QFileDialog.getOpenFileName(self, title, "",
                                                         filefilter)[0]

        if filename != '':
            self.update_file(filename)


    def update_file(self, filename):
        try:
            dcmdata = pydicom.dcmread(filename)
        except pydicom.errors.InvalidDicomError:
            pass
        # self._tree_model = objbrowser.treemodel.TreeModel(dcmdata, filename)
        self.obj = dcmdata
        self.name = '{}'.format(filename)

        self._tree_model.populateTree(dcmdata, '')

        self.refresh()
        self.setWindowTitle("{} - {}".format(PROGRAM_NAME, filename))


    def _update_details_for_item(self, tree_item):
        super()._update_details_for_item(tree_item)

        button_id = self.button_group.checkedId()

        # If this box is marked as editable either through fn or definition, allow write.
        try:
            editable = self._attr_details[button_id].editable(tree_item)
        except TypeError as e:
            print(e)
            editable = self._attr_details[button_id].editable
        except AttributeError as e:
            print(e)
            editable = False

        if self.edit_button.isChecked() and not editable:
            self.edit_button.click()
        self.edit_button.setCheckable(editable)
        self.edit_button.setEnabled(editable)
        # If this box is marked as editable either through fn or definition, allow write.

    """

    def _change_details_field(self, _button_id=None):
        super()._change_details_field(_button_id)

        attr_details = self._attr_details[_button_id]
    """


if __name__ == '__main__':
    from sys import argv, exit
    if len(argv) > 1:
        filename = argv[1]
        try:
            dcmdata = pydicom.dcmread(filename)
            DCMObj_Browser.browse(dcmdata, filename)
            exit()
        except (pydicom.errors.InvalidDicomError, FileNotFoundError) as e:
            print("File not found: %s" % e)
    DCMObj_Browser.browse()
