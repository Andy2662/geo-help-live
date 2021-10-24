from django.forms import widgets
import django_filters
from django_filters.filters import DateRangeFilter
from .models import *
from django_filters import DateFilter, CharFilter
from django import forms


class tablaFilter(django_filters.FilterSet):
    start_date = DateFilter(label='Fecha mayor o igual a  ',field_name="fecha", lookup_expr='date__gte',widget=forms.DateInput(
            attrs={
                'id': 'container',
                'type': 'date'
            }
        ))
    end_date = DateFilter(label='Fecha menor o igual a  ',field_name="fecha", lookup_expr='date__lte',widget=forms.DateInput(
            attrs={
                'id': 'container',
                'type': 'date'
            }
        ))
    observacion = CharFilter(label='Obsevacion  ',field_name='observacion',lookup_expr='icontains')
    id_usr = CharFilter(label='Id usuario  ',field_name='id_usr',lookup_expr='icontains')
    usuario = CharFilter(label='Usuario  ',field_name='usuario',lookup_expr='icontains')
    test_name = CharFilter(label='Nombre del test  ',field_name='test_name',lookup_expr='icontains')
    pot_db = CharFilter(label='Potencia  ',field_name='pot_db',lookup_expr='icontains')
    class Meta:
        model = medidas
        fields = '__all__'
        exclude = ['fecha','imsi','mcc','mnc','latitud',
                    'longitud','rssi','modelo',
                    'imei','marca',]
        widgets = {
            'usuario' : forms.Select(attrs={'class':'form-control'})

        }

class towerFilter(django_filters.FilterSet):
    
    observacion = CharFilter(label='Obsevacion  ',field_name='observacion',lookup_expr='icontains')
    #id_usr = CharFilter(label='Id usuario  ',field_name='id_usr',lookup_expr='icontains')
    nombre = CharFilter(label='Nombre  ',field_name='nombre',lookup_expr='icontains')
    torre = CharFilter(label='Tipo de torre  ',field_name='torre',lookup_expr='icontains')
    operador = CharFilter(label='Operador  ',field_name='operador',lookup_expr='icontains')
    altura = CharFilter(label='Altura de la torre ',field_name='altura',lookup_expr='icontains')

    class Meta:
        model = torre
        fields = '__all__'
        exclude = ['fecha','latitud',
                    'longitud','torre','modelo','nombre',]
        widgets = {
            'usuario' : forms.Select(attrs={'class':'form-control'})

        }

class towermeasureFilter(django_filters.FilterSet):
  
    test_name = CharFilter(label='Nombre del test ',field_name='test_name',lookup_expr='icontains')
    observacion = CharFilter(label='Observaciones ',field_name='observacion',lookup_expr='icontains')
    operador = CharFilter(label='Operador ',field_name='operador',lookup_expr='icontains')
    potencia = CharFilter(label='Potencia ',field_name='pot_db',lookup_expr='icontains')
    distancia = CharFilter(label='Distancia de la torre (m) ',field_name='distancia',lookup_expr='icontains')

    start_date = DateFilter(label='Fecha mayor o igual a  ',field_name="fecha", lookup_expr='date__gte',widget=forms.DateInput(
            attrs={
                'id': 'container',
                'type': 'date'
            }
        ))
    end_date = DateFilter(label='Fecha menor o igual a  ',field_name="fecha", lookup_expr='date__lte',widget=forms.DateInput(
            attrs={
                'id': 'container',
                'type': 'date'
            }
        ))
    
    class Meta:
        model = torre_measure
        fields = '__all__'
        exclude = ['test_name','fecha','imsi','mcc','mnc','rssi','modelo','torre_name',
                    'latitud','longitud','pot_db','operador','observacion','distancia',
                    ]
    
        widgets = {
            'usuario' : forms.Select(attrs={'class':'form-control'})

        }