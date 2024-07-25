import decimal
import base64
import matplotlib.pyplot as plt
import pandas as pd

from io import BytesIO

from rest_framework import status
from rest_framework.response import Response

from .models import Precio, Cantidad, Portafolio, Activo, Peso
from .utils import extraer_valores_por_portafolio


def obtener_valores(fecha_inicio, fecha_fin):

    precios_por_fecha = Precio.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
    if not precios_por_fecha.exists():
        return Response(
            {"error": "No se encontraron datos para las fechas proporcionadas"},
            status=status.HTTP_404_NOT_FOUND
        )

    cantidades_iniciales = Cantidad.objects.all()
    portafolio1_value, portafolio2_value = extraer_valores_por_portafolio(precios_por_fecha, cantidades_iniciales)

    data = [
        {
            "fecha": fecha,
            "portafolio_1": portafolio1_value[fecha],
            "portafolio_2": portafolio2_value[fecha],
        }
        for fecha in portafolio1_value
    ]
    return data


def obtener_pesos(fecha_inicio, fecha_fin):
    pesos_iniciales = Peso.objects.all()
    cantidades_iniciales = Cantidad.objects.all()
    precios_por_fecha = Precio.objects.filter(fecha__range=[fecha_inicio, fecha_fin])

    if not precios_por_fecha.exists() or not cantidades_iniciales.exists() or not pesos_iniciales.exists():
        return Response(
            {"error": "No se encontraron datos para las fechas proporcionadas"},
            status=status.HTTP_404_NOT_FOUND
        )
    precios_por_fecha = Precio.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
    if not precios_por_fecha.exists():
        return Response(
            {"error": "No se encontraron datos para las fechas proporcionadas"},
            status=status.HTTP_404_NOT_FOUND
        )

    cantidades_iniciales = Cantidad.objects.all()
    portafolio1_value, portafolio2_value = extraer_valores_por_portafolio(precios_por_fecha, cantidades_iniciales)

    data = []
    for precio in precios_por_fecha:
        try:
            peso_p1 = (precio.precio * cantidades_iniciales.get(
                portafolio__nombre='portafolio 1', activo=precio.activo
            ).cantidad) / portafolio1_value[precio.fecha]
            peso_p2 = (precio.precio * cantidades_iniciales.get(
                portafolio__nombre='portafolio 2', activo=precio.activo
            ).cantidad) / portafolio2_value[precio.fecha]
            data.append({
                "fecha": precio.fecha,
                "portafolio_1": {
                    "activo": precio.activo.nombre,
                    "peso": peso_p1
                },
                "portafolio_2": {
                    "activo": precio.activo.nombre,
                    "peso": peso_p2
                }
            })
        except Cantidad.DoesNotExist:
            pass
    return data


def procesar_operacion(fecha, portafolio_id, activo_vender_nombre, monto_vender, activo_comprar_nombre, monto_comprar):
    try:
        activo_vender = Activo.objects.get(nombre=activo_vender_nombre)
        activo_comprar = Activo.objects.get(nombre=activo_comprar_nombre)
        portafolio = Portafolio.objects.get(id=portafolio_id)
    except Portafolio.DoesNotExist:
        return Response(
            {"error": "Portafolio no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Activo.DoesNotExist:
        return Response(
            {"error": "Activo no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        cantidad_vender = Cantidad.objects.get(portafolio=portafolio, activo=activo_vender)
        cantidad_comprar = Cantidad.objects.get(portafolio=portafolio, activo=activo_comprar)
    except Cantidad.DoesNotExist:
        return Response(
            {"error": "No se encontraron cantidades iniciales para los activos"},
            status=status.HTTP_404_NOT_FOUND
        )

    precio_vender = Precio.objects.get(fecha=fecha, activo=activo_vender).precio
    precio_comprar = Precio.objects.get(fecha=fecha, activo=activo_comprar).precio

    cantidad_vender.cantidad -= decimal.Decimal(monto_vender) / precio_vender
    cantidad_comprar.cantidad += decimal.Decimal(monto_comprar) / precio_comprar

    cantidad_vender.save()
    cantidad_comprar.save()

    cantidades_iniciales = Cantidad.objects.filter(portafolio=portafolio)
    precios_por_fecha = Precio.objects.filter(fecha=fecha)

    portafolio1_value, portafolio2_value = extraer_valores_por_portafolio(precios_por_fecha, cantidades_iniciales)

    data = {
        "fecha": fecha,
        "portafolio": portafolio.nombre,
        "valor": portafolio1_value[fecha] if portafolio.nombre == 'portafolio 1' else portafolio2_value[fecha]
    }
    return data


def comparar_evolucion(fecha_inicio, fecha_fin):
    all_precios_por_fecha = Precio.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
    if not all_precios_por_fecha.exists():
        return Response(
            {"error": "No se encontraron datos para las fechas proporcionadas"},
            status=status.HTTP_404_NOT_FOUND
        )

    cantidades_iniciales = Cantidad.objects.all()
    p1_values_por_fecha, p2_values_por_fecha = extraer_valores_por_portafolio(all_precios_por_fecha,
                                                                              cantidades_iniciales)

    all_pesos_portafolio1 = []
    all_pesos_portafolio2 = []

    for precio in all_precios_por_fecha:
        try:
            peso_p1 = (precio.precio * cantidades_iniciales.get(
                portafolio__nombre='portafolio 1',
                activo=precio.activo
            ).cantidad) / p1_values_por_fecha[precio.fecha]
        except Cantidad.DoesNotExist:
            peso_p1 = 0

        try:
            peso_p2 = (precio.precio * cantidades_iniciales.get(
                portafolio__nombre='portafolio 2',
                activo=precio.activo
            ).cantidad) / p2_values_por_fecha[precio.fecha]
        except Cantidad.DoesNotExist:
            peso_p2 = 0

        all_pesos_portafolio1.append({
            "fecha": precio.fecha,
            "activo": precio.activo.nombre,
            "peso": peso_p1
        })
        all_pesos_portafolio2.append({
            "fecha": precio.fecha,
            "activo": precio.activo.nombre,
            "peso": peso_p2
        })

    df_p1 = pd.DataFrame(all_pesos_portafolio1)
    df_p2 = pd.DataFrame(all_pesos_portafolio2)

    df_p1['peso'] = pd.to_numeric(df_p1['peso'], errors='coerce').fillna(0)
    df_p2['peso'] = pd.to_numeric(df_p2['peso'], errors='coerce').fillna(0)

    df_p1_pivot = df_p1.pivot(index='fecha', columns='activo', values='peso')
    df_p2_pivot = df_p2.pivot(index='fecha', columns='activo', values='peso')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(list(p1_values_por_fecha.keys()), list(p1_values_por_fecha.values()), label='Portafolio 1')
    ax.plot(list(p2_values_por_fecha.keys()), list(p2_values_por_fecha.values()), label='Portafolio 2')
    ax.set_title('Evolución de los valores de cada portafolio')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Valor')
    ax.legend()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    fig, ax = plt.subplots(figsize=(10, 6))
    df_p1_pivot.plot.area(ax=ax, stacked=True)
    ax.set_title('Evolución de los pesos en el tiempo (Portafolio 1)')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Peso')
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64_p1 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    fig, ax = plt.subplots(figsize=(10, 6))
    df_p2_pivot.plot.area(ax=ax, stacked=True)
    ax.set_title('Evolución de los pesos en el tiempo (Portafolio 2)')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Peso')
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64_p2 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    data = {
        'image_base64': image_base64,
        'image_base64_p1': image_base64_p1,
        'image_base64_p2': image_base64_p2,
    }
    return data
