# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:25:36 2019

@author: nsperling
"""

from objbrowser.treemodel import TreeModel
from objbrowser.treeitem import TreeItem
from pydicom.dataset import Dataset, DataElement


class DCMTreeItem(TreeItem):
    """
    Extension of objbrowser.treeitem.TreeItem to allow for initialization with
    no children.  New init function only.
    """

    def __init__(self, obj, name, obj_path, is_attribute,
                 parent=None, has_children=True):

        super().__init__(obj, name, obj_path, is_attribute, parent)

        self.has_children = has_children
        try:
            self.dcm_path = '{}'.format(obj.tag)
        except AttributeError:
            self.dcm_path = ''
        
    def _update_dcmpath(self, item):
        if isinstance(item.obj, Dataset):
            item.dcm_path='{}[{}]'.format(self.dcm_path, item.obj_name)
            item.obj_path='{}[{}]'.format(self.obj_path, item.obj_name)
        else:
            item.dcm_path='{}.{}'.format(self.dcm_path, item.obj.tag)
            item.obj_path='{}.{}'.format(self.obj_path, item.obj.keyword or item.obj.tag)

    def append_child(self, item):
        super().append_child(item)
        self._update_dcmpath(item)

    def insert_children(self, idx, items):
        super().insert_children(idx, items)
        for item in items:
            self._update_dcmpath(item)


class DCMTreeModel(TreeModel):
    # Class for pydicom objects to sensibly fetch object children for tree.
    # Should override _fetchObjectChildren to allow reasonable data in tree.
    _TREAT_LIKE_OBJECTS = True

    def _fetchObjectChildren(self, obj, obj_path):
        """ Fetches the children of a Python object.
            Returns: list of TreeItems
        """
        if not isinstance(obj, (Dataset, DataElement)):
            # Not a dicom data element/dataset.  Use normal process
            return super()._fetchObjectChildren(obj, obj_path)

        if isinstance(obj, Dataset):
            # Datasets don't have properties, just elements.
            return [DCMTreeItem(de,
                        '{} --- {}'.format(de.tag, de.keyword),
                        '{}'.format(de.keyword or de.tag),
                        False,
                        has_children=de.VR == 'SQ')
                    for i, de in enumerate(obj)]
        elif obj.VR == 'SQ':
            # Sequence so children are a list and there are no attributes.
            return [DCMTreeItem(de, i, '{}[{}]'.format(obj_path, i), False)
                    for i, de in enumerate(obj)]
        else:
            # Not a sequence or a dataset, therefor no children
            return None