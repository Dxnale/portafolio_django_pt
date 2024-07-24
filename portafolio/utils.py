from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from portafolio.models import Cantidad


def validar_fechas(fecha_inicio_str, fecha_fin_str):
    if not fecha_inicio_str or not fecha_fin_str:
        return Response(
            {"error": "Por favor, proporcione fecha_inicio y fecha_fin"},
            status=status.HTTP_400_BAD_REQUEST)

    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
    except ValueError:
        return Response(
            {"error": "Formato de fecha inválido. Use YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST)

    if fecha_inicio > fecha_fin:
        return Response(
            {"error": "fecha_inicio debe ser menor que fecha_fin"},
            status=status.HTTP_400_BAD_REQUEST)

    return fecha_inicio, fecha_fin


def extraer_valores_por_portafolio(precios_por_fecha, cantidades_iniciales):
    portafolio1_value = {}
    portafolio2_value = {}

    for precio in precios_por_fecha:
        if precio.fecha not in portafolio1_value:
            portafolio1_value[precio.fecha] = 0
        try:
            valor = precio.precio * cantidades_iniciales.get(
                portafolio__nombre='portafolio 1',
                activo=precio.activo).cantidad
            portafolio1_value[precio.fecha] += valor
        except Cantidad.DoesNotExist:
            pass

        if precio.fecha not in portafolio2_value:
            portafolio2_value[precio.fecha] = 0
        try:
            valor = precio.precio * cantidades_iniciales.get(
                portafolio__nombre='portafolio 2',
                activo=precio.activo).cantidad
            portafolio2_value[precio.fecha] += valor
        except Cantidad.DoesNotExist:
            pass

    return portafolio1_value, portafolio2_value
