from rest_framework.serializers import (ModelSerializerOptions, ModelSerializer)
 
 
class PostModelSerializerOptions(ModelSerializerOptions):
    """
   Options for PostModelSerializer
   """
 
    def __init__(self, meta):
        super(PostModelSerializerOptions, self).__init__(meta)
        self.postonly_fields = getattr(meta, 'postonly_fields', ())
 
 
class PostModelSerializer(ModelSerializer):
    _options_class = PostModelSerializerOptions
 
    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = {}
 
        for field_name, field in self.fields.items():
            # Ignore all postonly_fields fron serialization
            if field_name in self.opts.postonly_fields:
                continue
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret
 
    def restore_object(self, attrs, instance=None):
        model_attrs, post_attrs = {}, {}
        for attr, value in attrs.iteritems():
            if attr in self.opts.postonly_fields:
                post_attrs[attr] = value
            else:
                model_attrs[attr] = value
        obj = super(PostModelSerializer,
                    self).restore_object(model_attrs, instance)
        # Method to process ignored postonly_fields
        self.process_postonly_fields(obj, post_attrs)
        return obj
 
    def process_postonly_fields(self, obj, post_attrs):
        """
        Placeholder method for processing data sent in POST.
        """