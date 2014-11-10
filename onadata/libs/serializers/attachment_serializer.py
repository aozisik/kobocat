from rest_framework import serializers
from onadata.apps.logger.models.attachment import Attachment
from onadata.libs.utils.decorators import check_obj
from onadata.libs.utils.image_tools import image_url
import json


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='attachment-detail',
                                               lookup_field='pk')
    field_xpath = serializers.SerializerMethodField('get_field_xpath')
    download_url = serializers.SerializerMethodField('get_download_url')
    small_download_url = serializers.SerializerMethodField(
        'get_small_download_url')
    medium_download_url = serializers.SerializerMethodField(
        'get_medium_download_url')
    xform = serializers.Field(source='instance.xform.pk')
    instance = serializers.Field(source='instance.pk')
    filename = serializers.Field(source='media_file.name')

    class Meta:
        fields = ('url', 'filename', 'mimetype', 'field_xpath', 'id', 'xform',
                  'instance', 'download_url', 'small_download_url',
                  'medium_download_url')
        lookup_field = 'pk'
        model = Attachment

    @check_obj
    def get_download_url(self, obj):
        return obj.media_file.url if obj.media_file.url else None

    def get_small_download_url(self, obj):
        if obj.mimetype.startswith('image'):
            return image_url(obj, 'small')

    def get_medium_download_url(self, obj):
        if obj.mimetype.startswith('image'):
            return image_url(obj, 'medium')

    def get_field_xpath(self, obj):
        qa_dict = obj.instance.get_dict()
        if obj.filename not in qa_dict.values():
            return None

        question_name = qa_dict.keys()[qa_dict.values().index(obj.filename)]
        json_for_xform = json.loads(obj.instance.xform.json)['children']

        def get_path(data, num, question):
            if (num + 1) >= len(data):
                return None
            val = data[num]
            if val.get('name') == question:
                return "%s" % val.get('name')
            elif val.get('type') == 'group' and \
                    val.get('children') is not None:
                for a in val.get('children'):
                    if a.get('name') == question:
                        return "%s/%s" % (val.get('name'), a.get('name'))
                return get_path(data, num + 1, question)
            else:
                return get_path(data, num + 1, question)
        return get_path(json_for_xform, 0, question_name)
