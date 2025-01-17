from django.urls import path
from .views import ValoresApi, PesosApi, ProcesarOperacionApi, CompararEvolucionView

urlpatterns = [
    path('valores/', ValoresApi.as_view(), name='valores-api'),
    path('pesos/', PesosApi.as_view(), name='pesos-api'),
    path('procesar-operacion/', ProcesarOperacionApi.as_view(), name='procesar-operacion-api'),
    path('comparar-evolucion/', CompararEvolucionView.as_view(), name='comparar-evolucion-api'),
]
