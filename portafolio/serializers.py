from rest_framework import serializers
from .models import Peso, Cantidad, Portafolio, Activo


class PesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Peso
        fields = ['portafolio', 'activo', 'peso', 'fecha']


class CantidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cantidad
        fields = ['portafolio', 'activo', 'cantidad', 'fecha']
