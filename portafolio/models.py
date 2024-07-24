from django.db import models


# Create your models here.
class Activo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Portafolio(models.Model):
    nombre = models.CharField(max_length=100)
    valor_inicial = models.DecimalField(max_digits=20, decimal_places=6)
    activos = models.ManyToManyField(Activo)

    def __str__(self):
        return self.nombre


class Precio(models.Model):
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE)
    fecha = models.DateField()
    precio = models.DecimalField(max_digits=20, decimal_places=6)

    def __str__(self):
        return f'{self.activo.nombre} - {self.fecha} - {self.precio}'

    class Meta:
        unique_together = ['activo', 'fecha']


class Cantidad(models.Model):
    portafolio = models.ForeignKey(Portafolio, on_delete=models.CASCADE)
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=20, decimal_places=6)
    fecha = models.DateField()

    def __str__(self):
        return f'{self.portafolio.nombre} - {self.activo.nombre} - {self.cantidad}'

    class Meta:
        unique_together = ['portafolio', 'activo']


class Peso(models.Model):
    portafolio = models.ForeignKey(Portafolio, on_delete=models.CASCADE)
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=20, decimal_places=6)
    fecha = models.DateField()

    def __str__(self):
        return f'{self.portafolio.nombre} - {self.activo.nombre} - {self.peso}'

    class Meta:
        unique_together = ['portafolio', 'activo', 'fecha']
