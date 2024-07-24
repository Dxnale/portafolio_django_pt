# Generated by Django 5.0.7 on 2024-07-24 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portafolio', '0002_alter_peso_peso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cantidad',
            name='cantidad',
            field=models.DecimalField(decimal_places=6, max_digits=20),
        ),
        migrations.AlterField(
            model_name='peso',
            name='peso',
            field=models.DecimalField(decimal_places=6, max_digits=20),
        ),
        migrations.AlterField(
            model_name='portafolio',
            name='valor_inicial',
            field=models.DecimalField(decimal_places=6, max_digits=20),
        ),
        migrations.AlterField(
            model_name='precio',
            name='precio',
            field=models.DecimalField(decimal_places=6, max_digits=20),
        ),
    ]
