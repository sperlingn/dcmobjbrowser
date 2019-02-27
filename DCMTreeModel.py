# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:25:36 2019

@author: nsperling
"""

import objbrowser.treemodel
from objbrowser.treeitem import TreeItem
#import logger
#from collections import OrderedDict
from pydicom.dataset import Dataset, DataElement
#from pydicom.tag import tag_in_exception


class DCMTreeModel(objbrowser.treemodel):
    # Class for pydicom objects to sensibly fetch object children for tree.
    # Should override _fetchObjectChildren to allow reasonable data in tree.
    _TREAT_LIKE_OBJECTS = False
    
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
                tree_items = list([TreeItem(de, i, '{}[{}]'.format(obj_path, i),
                                   False) for i,de in enumerate(obj)])
                return tree_items
            
                # Old tree method.
                obj_children, path_strings, is_attr_list = map(list, 
                                   zip(*[((i,de), '{}[{}]'.format(obj_path, i),
                                          False) for i,de in enumerate(obj)]))
        except AttributeError as e:
            # Ignore attribute error for datasets
            if isinstance(obj, Dataset): 
                raise e

        # All descendents of Dataset and DataElement should be DataElements
        obj_children = []
        path_strings = []
        
        # Method for non sequences. (Treat like attribute?)
        if self._TREAT_LIKE_OBJECTS: # Treat like objects
            obj_children = list([(de.tag, de) for de in obj])
            path_strings = list(['{}.{}'.format(obj_path, de.tag) for de in 
                                 obj])
            is_attr_list = [False] * len(obj_children)
        
        if not self._TREAT_LIKE_OBJECTS: # Treat like attributes
            # handle non-sequence children as attributes
            obj_children = list([(de.tag, de.value) for de in obj  
                                 if de.VR != 'SQ'])
            path_strings = list(['{}.{}'.format(obj_path, de.tag) for de in 
                                 obj if de.VR != 'SQ'])
            is_attr_list = [True] * len(obj_children)
            
            # handle sequence children as objects
            obj_children_sq = list([(de.tag, de) for de in obj])
            path_strings_sq = list(['{}.{}'.format(obj_path, de.tag) for de in
                                    obj])
            is_attr_list_sq = [False] * len(obj_children)
            
            obj_children.append(obj_children_sq)
            path_strings.append(path_strings_sq)
            is_attr_list.append(is_attr_list_sq)
            
        assert len(obj_children) == len(path_strings) == len(is_attr_list), \
                "sanity check"
        tree_items = []
        for item, path_str, is_attr in zip(obj_children, path_strings, is_attr_list):
            name, child_obj = item
            tree_items.append(TreeItem(child_obj, name, path_str, is_attr))
            
        return tree_items    
