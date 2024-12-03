# Generated by Django 5.1.3 on 2024-11-28 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orden',
            name='status',
            field=models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('ENVIADO', 'Enviado'), ('ENTREGADO', 'Entregado')], default='PENDIENTE', max_length=20),
        ),
    ]
