import decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from .models import Peso, Precio, Cantidad, Portafolio, Activo
from .utils import validar_fechas, extraer_valores_por_portafolio


class ValoresApi(APIView):
    class OutputSerializer(serializers.Serializer):
        fecha = serializers.DateField()
        portafolio_1 = serializers.FloatField()
        portafolio_2 = serializers.FloatField()

    def get(self, request, *args, **kwargs):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        validacion = validar_fechas(fecha_inicio, fecha_fin)
        if isinstance(validacion, Response):
            return validacion

        fecha_inicio, fecha_fin = validacion

        precios_por_fecha = Precio.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
        if not precios_por_fecha.exists():
            return Response(
                {"error": "No se encontraron datos para las fechas proporcionadas"},
                status=status.HTTP_404_NOT_FOUND
            )

        cantidades_iniciales = Cantidad.objects.all()
        portafolio1_value, portafolio2_value = extraer_valores_por_portafolio(
            precios_por_fecha, cantidades_iniciales
        )

        data = [
            {
                "fecha": fecha,
                "portafolio_1": portafolio1_value[fecha],
                "portafolio_2": portafolio2_value[fecha],
            }
            for fecha in portafolio1_value
        ]

        return Response(self.OutputSerializer(data, many=True).data, status=status.HTTP_200_OK)


class PesosApi(APIView):
    class OutputSerializer(serializers.Serializer):
        fecha = serializers.DateField()
        portafolio_1 = serializers.DictField()
        portafolio_2 = serializers.DictField()

    def get(self, request, *args, **kwargs):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        validacion = validar_fechas(fecha_inicio, fecha_fin)
        if isinstance(validacion, Response):
            return validacion

        fecha_inicio, fecha_fin = validacion

        pesos_iniciales = Peso.objects.all()
        cantidades_iniciales = Cantidad.objects.all()
        precios_por_fecha = Precio.objects.filter(fecha__range=[fecha_inicio, fecha_fin])

        if not precios_por_fecha.exists() or not cantidades_iniciales.exists() or not pesos_iniciales.exists():
            return Response(
                {"error": "No se encontraron datos para las fechas proporcionadas"},
                status=status.HTTP_404_NOT_FOUND
            )

        portafolio1_value, portafolio2_value = extraer_valores_por_portafolio(
            precios_por_fecha, cantidades_iniciales
        )

        data = []
        for precio in precios_por_fecha:
            try:
                peso_fecha_p1 = (
                    precio.precio * cantidades_iniciales.get(
                        portafolio__nombre='portafolio 1', activo=precio.activo
                    ).cantidad
                ) / portafolio1_value[precio.fecha]
                peso_fecha_p2 = (
                    precio.precio * cantidades_iniciales.get(
                        portafolio__nombre='portafolio 2', activo=precio.activo
                    ).cantidad
                ) / portafolio2_value[precio.fecha]
                data.append({
                    "fecha": precio.fecha,
                    "portafolio_1": {
                        "activo": precio.activo.nombre,
                        "peso": peso_fecha_p1
                    },
                    "portafolio_2": {
                        "activo": precio.activo.nombre,
                        "peso": peso_fecha_p2
                    }
                })
            except Cantidad.DoesNotExist:
                pass

        return Response(self.OutputSerializer(data, many=True).data, status=status.HTTP_200_OK)


class ProcesarOperacionApi(APIView):
    class InputSerializer(serializers.Serializer):
        fecha = serializers.DateField()
        portafolio = serializers.IntegerField()
        activo_vender = serializers.CharField()
        monto_vender = serializers.FloatField()
        activo_comprar = serializers.CharField()
        monto_comprar = serializers.FloatField()

    class OutputSerializer(serializers.Serializer):
        fecha = serializers.DateField()
        portafolio = serializers.CharField()
        valor = serializers.FloatField()

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fecha = serializer.validated_data['fecha']
        portafolio_id = serializer.validated_data['portafolio']
        activo_vender_nombre = serializer.validated_data['activo_vender']
        monto_vender = serializer.validated_data['monto_vender']
        activo_comprar_nombre = serializer.validated_data['activo_comprar']
        monto_comprar = serializer.validated_data['monto_comprar']

        try:
            activo_vender = Activo.objects.get(nombre=activo_vender_nombre)
            activo_comprar = Activo.objects.get(nombre=activo_comprar_nombre)
            portafolio = Portafolio.objects.get(id=portafolio_id)
        except Portafolio.DoesNotExist:
            return Response({"error": "Portafolio no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Activo.DoesNotExist:
            return Response({"error": "Activo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar cantidades
        try:
            cantidad_vender = Cantidad.objects.get(portafolio=portafolio, activo=activo_vender)
            cantidad_comprar = Cantidad.objects.get(portafolio=portafolio, activo=activo_comprar)
        except Cantidad.DoesNotExist:
            return Response(
                {"error": "Cantidad no encontrada para el portafolio y activo especificado"},
                status=status.HTTP_404_NOT_FOUND
            )

        precio_vender = Precio.objects.get(fecha=fecha, activo=activo_vender).precio
        precio_comprar = Precio.objects.get(fecha=fecha, activo=activo_comprar).precio

        cantidad_vender.cantidad -= decimal.Decimal(monto_vender) / precio_vender
        cantidad_comprar.cantidad += decimal.Decimal(monto_comprar) / precio_comprar

        cantidad_vender.save()
        cantidad_comprar.save()

        # Recalcular valores
        cantidades_iniciales = Cantidad.objects.filter(portafolio=portafolio)
        precios_por_fecha = Precio.objects.filter(fecha=fecha)

        portafolio1_value, portafolio2_value = extraer_valores_por_portafolio(precios_por_fecha, cantidades_iniciales)

        data = {
            "fecha": fecha,
            "portafolio": portafolio.nombre,
            "valor": portafolio1_value[fecha] if portafolio.nombre == 'portafolio 1' else portafolio2_value[fecha]
        }

        return Response(self.OutputSerializer(data).data, status=status.HTTP_200_OK)
