
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Peso, Precio, Cantidad
from .services import obtener_pesos, procesar_operacion, comparar_evolucion, obtener_valores
from .utils import validar_fechas
from .serializers import ValoresOutputSerializer, PesosOutputSerializer, ProcesarOperacionOutputSerializer, \
    ProcesarOperacionInputSerializer


class ValoresApi(APIView):
    def get(self, request, *args, **kwargs):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        validacion = validar_fechas(fecha_inicio, fecha_fin)
        if isinstance(validacion, Response):
            return validacion

        fecha_inicio, fecha_fin = validacion
        data = obtener_valores(fecha_inicio, fecha_fin)

        if isinstance(data, Response):
            return data

        return Response(ValoresOutputSerializer(data, many=True).data, status=status.HTTP_200_OK)


class PesosApi(APIView):
    def get(self, request, *args, **kwargs):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        validacion = validar_fechas(fecha_inicio, fecha_fin)
        if isinstance(validacion, Response):
            return validacion

        fecha_inicio, fecha_fin = validacion

        data = obtener_pesos(fecha_inicio, fecha_fin)

        if isinstance(data, Response):
            return data

        return Response(PesosOutputSerializer(data, many=True).data, status=status.HTTP_200_OK)


class ProcesarOperacionApi(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProcesarOperacionInputSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fecha = serializer.validated_data['fecha']
        portafolio_id = serializer.validated_data['portafolio']
        activo_vender_nombre = serializer.validated_data['activo_vender']
        monto_vender = serializer.validated_data['monto_vender']
        activo_comprar_nombre = serializer.validated_data['activo_comprar']
        monto_comprar = serializer.validated_data['monto_comprar']

        data = procesar_operacion(
            fecha,
            portafolio_id,
            activo_vender_nombre,
            monto_vender,
            activo_comprar_nombre,
            monto_comprar
        )

        if isinstance(data, Response):
            return data

        return Response(ProcesarOperacionOutputSerializer(data).data, status=status.HTTP_200_OK)


class CompararEvolucionView(APIView):

    def get(self, request, *args, **kwargs):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        validacion = validar_fechas(fecha_inicio, fecha_fin)
        if isinstance(validacion, Response):
            return validacion

        fecha_inicio, fecha_fin = validacion

        data = comparar_evolucion(fecha_inicio, fecha_fin)

        if isinstance(data, Response):
            return

        return render(self.request, 'comparar_evolucion.html', data)
