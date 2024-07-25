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


class ValoresOutputSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    portafolio_1 = serializers.FloatField()
    portafolio_2 = serializers.FloatField()


class PesosOutputSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    portafolio_1 = serializers.DictField()
    portafolio_2 = serializers.DictField()


class ProcesarOperacionInputSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    portafolio = serializers.IntegerField()
    activo_vender = serializers.CharField()
    monto_vender = serializers.FloatField()
    activo_comprar = serializers.CharField()
    monto_comprar = serializers.FloatField()


class ProcesarOperacionOutputSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    portafolio = serializers.CharField()
    valor = serializers.FloatField()

