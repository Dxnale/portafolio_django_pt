# Portafolio Django Project

Gestiona un portafolio de inversiones según requerimientos.

## Requisitos

- Python 3.12
- Django 5.0.7
- Otros requisitos especificados en `requirements.txt`

## Instalación

1. Clona el repositorio:

    ```bash
    git clone https://github.com/tu_usuario/portafolio_django_pt.git
    cd portafolio_django_pt
    ```

2. Crea y activa un entorno virtual:

    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # En Windows
    source .venv/bin/activate  # En Unix o MacOS
    ```

3. Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

4. Realiza las migraciones de la base de datos:

    ```bash
    python manage.py migrate
    ```

## Configuración

Asegúrate de que el archivo `config/django/base.py` esté configurado correctamente y que las variables de entorno necesarias estén definidas.

## Carga de Datos

Para cargar los datos iniciales de la aplicación desde excel a la base de datos, ejecuta el siguiente comando:

```bash
python manage.py load_data
```

## Uso

Para ejecutar el servidor de desarrollo:

```bash
python manage.py runserver
```

## Endpoints de la API

### Valores API

- **URL:** `/api/valores/`
- **Método:** `GET`
- **Descripción:** Obtiene los valores de los portafolios en un rango de fechas.
- **Parámetros:**
  - `fecha_inicio` (date): Fecha de inicio.
  - `fecha_fin` (date): Fecha de fin.

### Pesos API

- **URL:** `/api/pesos/`
- **Método:** `GET`
- **Descripción:** Obtiene los pesos de los activos en los portafolios en un rango de fechas.
- **Parámetros:**
  - `fecha_inicio` (date): Fecha de inicio.
  - `fecha_fin` (date): Fecha de fin.

### Procesar Operación API

- **URL:** `/api/procesar-operacion/`
- **Método:** `POST`
- **Descripción:** Procesa una operación de compra y venta de activos.
- **Cuerpo de la solicitud:**
  ```json
  {
    "fecha": "2022-05-15",
    "portafolio": "portafolio1",
    "activo_vender": "EEUU",
    "monto_vender": 200000000,
    "activo_comprar": "Europa",
    "monto_comprar": 200000000
  }
  ```

## Pruebas

Para probar el endpoint `POST` de la API `Procesar Operación` desde PyCharm, crea un archivo `test_procesar_operacion.http` con el siguiente contenido:

```http
POST http://localhost:8000/api/procesar-operacion/
Content-Type: application/json

{
  "fecha": "2022-05-15",
  "portafolio": "portafolio1",
  "activo_vender": "EEUU",
  "monto_vender": 200000000,
  "activo_comprar": "Europa",
  "monto_comprar": 200000000
}
```

## Licencia

Este proyecto no está bajo ninguna licencia, es una prueba técnica :).
```