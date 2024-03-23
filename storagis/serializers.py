from django.contrib.auth.models import Group, User
from rest_framework import serializers
from storagis.models import progetti


class UserSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = User
    fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Group
    fields = ['url', 'name']

class ImportProjectSerializer(serializers.ModelSerializer):

  file_progetto = serializers.FileField()

  class Meta:
    model = progetti
    fields = [  'file_progetto','nome_progetto',
                     'owner','data_caricamento',
                     'comune','riferimento_remoto'  ]
    read_only_fields = ['owner','data_caricamento','riferimento_remoto']

  def create(self, validated_data):
    self.data.pop('file_progetto')
    validated_data.pop('file_progetto')
    return super(ImportProjectSerializer, self).create(validated_data)
