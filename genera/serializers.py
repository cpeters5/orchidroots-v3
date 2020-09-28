from rest_framework import serializers
from django.apps import apps

Genus = apps.get_model('orchiddb', 'Genus')

class GeneraSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Genus
        fields = ('pid','url','genus','author','year')

