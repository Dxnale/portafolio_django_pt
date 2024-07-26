from datetime import datetime
from rest_framework.response import Response
from rest_framework import status


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

