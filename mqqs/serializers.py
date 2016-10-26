from rest_framework import serializers

from mqqs.models import Mqq

class MqqSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mqq
        fields = ('id', 'alias', 'env', 'type', 'deep')