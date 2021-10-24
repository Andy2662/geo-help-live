# Generated by Django 3.2.1 on 2021-05-20 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('aplicacion', '0003_delete_medidas'),
    ]

    operations = [
        migrations.CreateModel(
            name='medidas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=200)),
                ('id_usr', models.CharField(max_length=200)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('imsi', models.CharField(max_length=200)),
                ('mcc', models.CharField(max_length=200)),
                ('mnc', models.CharField(max_length=200)),
                ('test_name', models.CharField(max_length=200)),
                ('observacion', models.CharField(max_length=200)),
                ('operador', models.CharField(max_length=200)),
                ('latitud', models.CharField(max_length=200)),
                ('longitud', models.CharField(max_length=200)),
                ('pot_db', models.CharField(max_length=200)),
                ('rssi', models.CharField(max_length=200)),
                ('modelo', models.CharField(max_length=200)),
                ('imei', models.CharField(max_length=200)),
            ],
        ),
    ]
