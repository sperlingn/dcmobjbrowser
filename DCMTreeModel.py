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

        # Start with dataset
        try:
            if obj.VR == 'SQ':
                # Sequence so children are a list and there are no attributes.
                return [DCMTreeItem(de, i, '{}[{}]'.format(obj_path, i), False)
                        for i, de in enumerate(obj)]
        except AttributeError as e:
            # Ignore attribute error for datasets
            if not isinstance(obj, Dataset):
                raise e

        return [DCMTreeItem(de,
                            '{} --- {}'.format(de.tag, de.keyword),
                            ('{}.{}'.format(obj_path, de.tag) if
                             obj_path != '<root>' else '{}'.format(de.tag)),
                            False,
                            has_children=de.VR == 'SQ')
                for i, de in enumerate(obj)]
