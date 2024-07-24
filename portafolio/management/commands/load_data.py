import pandas as pd
from django.core.management.base import BaseCommand
from portafolio.models import Activo, Portafolio, Precio, Cantidad


class Command(BaseCommand):
    help = 'Carga los datos de excel a la base de datos'

    def handle(self, *args, **options):

        df_pesos = pd.read_excel('data/datos.xlsx', sheet_name='weights')
        df_precios = pd.read_excel('data/datos.xlsx', sheet_name='Precios')
        valor_inicial = 1000000000

        # Crear portafolios
        for _ in [1, 2]:
            if not Portafolio.objects.filter(nombre=f'portafolio {_}').exists():
                Portafolio.objects.create(nombre=f'portafolio {_}', valor_inicial=valor_inicial)

        # Crear activos
        for activo in df_precios.columns[1:]:
            if not Activo.objects.filter(nombre=activo).exists():
                Activo.objects.create(nombre=activo)

        # Crear precios
        for index, row in df_precios.iterrows():
            for activo in df_precios.columns[1:]:
                if not Precio.objects.filter(
                        activo__nombre=activo,
                        fecha=row['Dates']
                ).exists():
                    Precio.objects.create(
                        activo=Activo.objects.get(
                            nombre=activo),
                        fecha=row['Dates'],
                        precio=row[activo]
                    )

        # Crear pesos y asignar activos a portafolios
        for index, row in df_pesos.iterrows():
            for _ in [1, 2]:
                portafolio = Portafolio.objects.get(nombre=f'portafolio {_}')
                fecha = row['Fecha']
                activo = Activo.objects.get(nombre=row['activos'])
                peso = row[f'portafolio {_}']

                if not portafolio.peso_set.filter(activo=activo, fecha=fecha).exists():
                    portafolio.peso_set.create(activo=activo, peso=peso, fecha=fecha)

                if not portafolio.activos.filter(id=activo.id).exists() and peso > 0:
                    portafolio.activos.add(activo)

        # Crear cantidades
        for _ in [1, 2]:
            portafolio = Portafolio.objects.get(nombre=f'portafolio {_}')
            fecha = df_pesos['Fecha'].min()
            for activo in portafolio.activos.all():
                peso = portafolio.peso_set.get(activo=activo, fecha=fecha).peso
                precio = Precio.objects.get(activo=activo, fecha=fecha).precio
                cantidad = (peso * portafolio.valor_inicial) / precio

                if not Cantidad.objects.filter(portafolio=portafolio, activo=activo, fecha=fecha).exists():
                    Cantidad.objects.create(portafolio=portafolio, activo=activo, cantidad=cantidad, fecha=fecha
                                            )

        self.stdout.write(self.style.SUCCESS('Datos cargados exitosamente'))
