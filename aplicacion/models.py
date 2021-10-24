from django.db import models
from django.db.models.base import ModelStateFieldsCacheDescriptor
from django.db.models.query_utils import refs_expression
from django.core.validators import FileExtensionValidator


# Create your models here.


class medidas(models.Model):
    usuario = models.CharField(max_length=200)
    id_usr = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True) 
    imsi = models.CharField(max_length=200) 
    mcc = models.CharField(max_length=200) 
    mnc = models.CharField(max_length=200) 
    test_name = models.CharField(max_length=200) 
    observacion = models.CharField(max_length=200) 
    operador = models.CharField(max_length=200)
    latitud = models.CharField(max_length=200)
    longitud = models.CharField(max_length=200)
    pot_db = models.CharField(max_length=200)
    rssi = models.CharField(max_length=200) 
    modelo = models.CharField(max_length=200) 
    imei = models.CharField(max_length=200)
    marca = models.CharField(max_length=200)
   
    def __str__(self):
        return f"Datos recolectados en {self.fecha}"
    
    def datepublished(self):
        return self.fecha.strftime("%m/%d/%Y, %H:%M:%S")

class data_bolivia(models.Model):
    mcc = models.CharField(max_length=200)
    mnc = models.CharField(max_length=200)
    operador = models.CharField(max_length=200)
    estado = models.CharField(max_length=200)
    tecnologia_freq = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.operador}"

class user_csvs(models.Model):
    usuario = models.CharField(max_length=200)
    id_usr = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True) 
    titulo = models.CharField(max_length=200)
    comentario = models.CharField(max_length=200)
    archivocsv = models.FileField(upload_to='usr_csv/',validators=[FileExtensionValidator( ['csv'] ) ])

    def __str__(self):
        return self.titulo

    def delete(self, *args, **kwargs):
        self.archivocsv.delete()
        
        super().delete(*args, **kwargs)
    

class torre(models.Model):
    TIPO_TORRE = (
    ('torre','Torre'),
    ('torreta', 'Torreta'),
    ('monopolo','Monopolo'),
  
    )
    OPERADOR_BO = (
    ('Entel','Entel'),
    ('Viva', 'Viva'),
    ('Tigo','Tigo'),
  
    )
    cell_id = models.CharField(max_length=200)
    lac = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True) 
    observacion = models.CharField(max_length=200) 
    mnc = models.CharField(max_length=200) 
    operador = models.CharField(max_length=200, choices=OPERADOR_BO)
    latitud = models.CharField(max_length=200)
    longitud = models.CharField(max_length=200)
    torre = models.CharField(max_length=200, choices=TIPO_TORRE)
    altura = models.CharField(max_length=200)
    def __str__(self):
        return f"Torre {self.cell_id}"  


class torre_measure(models.Model):

    fecha = models.DateTimeField(auto_now_add=True) 
    imsi = models.CharField(max_length=200) 
    mcc = models.CharField(max_length=200) 
    mnc = models.CharField(max_length=200) 
    test_name = models.CharField(max_length=200) 
    observacion = models.CharField(max_length=200) 
    operador = models.CharField(max_length=200)
    latitud = models.CharField(max_length=200)
    longitud = models.CharField(max_length=200)
    pot_db = models.CharField(max_length=200)
    rssi = models.CharField(max_length=200) 
    modelo = models.CharField(max_length=200) 
    torre_name = models.CharField(max_length=200) 
    distancia = models.CharField(max_length=200) 

    def __str__(self):
        return f"Datos recolectados en {self.fecha}"
    
    def datepublished(self):
        return self.fecha.strftime("%m/%d/%Y, %H:%M:%S")