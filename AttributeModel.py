from objbrowser.attribute_model import AttributeModel as AttributeModel_O


class AttributeModel(AttributeModel_O):
    def __init__(self, name, *args, 
                 editable=False, 
                 data_write_fn=None, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.editable = editable
        self.data_write_fn = data_write_fn

    __init__.__doc__ = AttributeModel_O.__init__.__doc__
