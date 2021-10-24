from django.shortcuts import render, redirect
from subprocess import call

from colour import Color
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import *
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from .filters import *
from folium import plugins, features
from folium.plugins import *
from django.core.files.storage import FileSystemStorage
from numpy import interp
#from geopy.distance import geodesic


import pandas as pd
import folium
import numpy as np


import branca.colormap as cm
#import mariadb
import sys
import pynmea2
import serial
import time
import re
import csv
import math
import logging

@login_required(login_url='login')
def home(request):
    return render(request,'aplicacion/dashboard.html')

@unauthenticated_user
def registerPage(request):

    form = CreateUserForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Cuenta creada para '+ user)
            return redirect('login')
    context = {'form':form}
    return render(request, 'aplicacion/register.html', context)

@unauthenticated_user
def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Usuario o Contraseña son incorrectos.')
                

        
    context = {}
    return render(request, 'aplicacion/login.html', context) 

def logoutUser(request):
    logout(request)

    return redirect('login')
    
def userMaps(request):
    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=2.0)
    modem = serial.Serial('/dev/ttyUSB2', 9600, timeout=2.0)
    m = folium.Map(
            width='100%', 
            height='100%', 
            zoom_start=10,
            location=(-17.4140, -66.1653)
            
            )
    m = m._repr_html_()


    form = medidasForm(request.POST or None)
    username = request.user.username
    user_id = request.user.id
    
    context={'nombre':username, 'userid':user_id,
                'form':form, 'map':m,
                    }
    if form.is_valid():
        flag = 1
        while flag==1:
                    try:
                        line = ser.readline().decode('ISO-8859-1')
                        msg = pynmea2.parse(line)
                        if msg.sentence_type == "RMC":
                            lati=round(float(msg.latitude),6)
                            longi=round(float(msg.longitude),6)
                            modem.write(b'AT+CFUN=1\r')
                            time.sleep(0.9)
                            modem.write(b'AT+CSQ\r')
                            time.sleep(0.9)
                            modem.write(b'AT+CIMI\r')
                            time.sleep(0.9)
                            modem.write(b'ATI\r')
                            time.sleep(0.9)
                            modem.write(b'AT+ZRSSI\r')
                            time.sleep(0.9)
                            at=modem.readlines()
                            atc=str(at).replace("\\"," ")
                            atcc=atc.replace("'"," ")
                            #print(atcc)
                            m = re.findall('CSQ: (.+?) ',str(atcc))
                            m1 = re.findall('ZRSSI: (.+?),',str(atcc))
                            man = re.findall('Manufacturer: (.+?) r',str(atcc))
                            mod = re.findall('Model: (.+?) ',str(atcc))
                            ime = re.findall('IMEI: (.+?) ',str(atcc))
                            x = str(re.findall('CIMI r r n , b (.+?) ',str(atcc)))
                            imsi = re.findall('[0-9]+',str(x))[0]
                            #print(imsi)
                            mcc=str(imsi)[0:3]
                            mnc=str(imsi)[3:5]
                            mm=m[0].replace(",",".")
                            mm1=m1[0].replace(",",".")
                            #print(mm)
                            y=round(float(mm))
                            y1=round(float(mm1))
                            manufacturer=str(man[0])
                            model=str(mod[0])
                            imei=str(ime[0])
                            operador = data_bolivia.objects.get(mnc=mnc)
                            #print(manufacturer,model,imei)
                            if y==100 or y==0 or y==99 or lati==0.0 or longi==0.0:
                                print("Sin Conexion")
                            else:
                                #ydbm=(-113+((y)*2))
                                ydbm=(y1*-1)
                                print("RED: ",operador.operador)
                                print("MODELO: ",model)
                                print("FABRICANTE: ",manufacturer)
                                print("IMEI: ",imei)
                                print("IMSI: ",imsi)
                                print("MCC: ",mcc)
                                print("MNC: ",mnc)
                                print("RSSI:",y)
                                print("Potencia:",ydbm,"dBm")
                                print("Latitud:",lati,"Longitud:",longi)
                                print("-----------------------------------------")

                                flag=6
                    except serial.SerialException as e:
                        print('Error de conexion: {}'.format(e))
                        break
                    except pynmea2.ParseError as e:
                        print('Data error: {}'.format(e))
                        continue
        test_name = form.cleaned_data.get('test_name')
        observacion = form.cleaned_data.get('observacion')
        instance = form.save(commit=False)
        instance.test_name = test_name
        instance.observacion = observacion
        instance.usuario = username
        instance.id_usr = user_id
        instance.imsi = imsi
        instance.mcc = mcc
        instance.mnc = mnc
        instance.operador = operador.operador
        instance.latitud = lati
        instance.longitud = longi
        instance.pot_db = ydbm
        instance.rssi = y
        instance.modelo = model
        instance.imei = imei
        instance.marca = manufacturer
        instance.save()
        data_display = medidas.objects.filter(test_name=test_name).order_by('-id')
    
        m = folium.Map(
            width='100%', 
            height='100%', 
            location=(lati,longi),
            zoom_start=14,
            )
        if mnc=='01':
            color_icon='green'
        elif mnc=='02':
            color_icon='blue'
        elif mnc=='03':
            color_icon='darkblue'
        folium.Marker(
            location=[lati, longi],
            popup='Tu ubicacion actual...',
            icon = folium.Icon(color=color_icon),
            
        ).add_to(m)  
        m = m._repr_html_()
        datos_p = data_display

        context={'nombre':username, 'userid':user_id, 
                'form':form, 'map':m,  'datos':datos_p,
                }


    return render(request,'aplicacion/mapas.html', context)

def maps_app(request):

    data_display = medidas.objects.all().order_by('-id')
    rootcsv='maps.csv'
    rootcsv1='maps1.csv'
    rootxlxs = 'maps.xlsx'



    mediFitro = tablaFilter(request.GET, queryset=data_display)
    datos = mediFitro.qs
    

    with open(rootcsv, 'w') as crearcsv:
        writer = csv.writer(crearcsv)
        writer.writerow([
            'latitud', 
            'longitud',
            'pot',
            'usuario',
            'fecha',
            'test_name',
            'observacion',
            'operador',
            'rssi',
            'marca',
            'imsi',
            'modelo',
            

            ])
        for dat in datos.values_list(
            'latitud',
            'longitud',
            'pot_db',
            'usuario',
            'fecha',
            'test_name',
            'observacion',
            'operador',
            'rssi',
            'marca',
            'imsi',
            'modelo'

            
            ):

            writer.writerow(dat)

    
    newd_csv=pd.read_csv(rootcsv)
    newd_csv["pot_db"]=newd_csv['pot'].apply(lambda x: interp(x,[-120,-90],[0.4,1.0]))
    newd_csv.to_csv(rootcsv1, index=False)
    datos_csv=pd.read_csv(rootcsv1)
    datos_csv1=pd.read_csv(rootcsv)
    datos_csv1.to_excel(rootxlxs,index = None, header=True)
    if(datos_csv.empty):
        default_lat = -17.4140
        default_lon = -66.1653
    else:
        default_lat= datos_csv['latitud'].mean()
        default_lon= datos_csv['longitud'].mean()

    print(default_lat, default_lon)
  
    
    m = folium.Map(
            width='100%', 
            height='100%', 
            location=(default_lat, default_lon),
            tiles='OpenStreetMap',
            control_scale=True,
            min_zoom=14, 
            max_zoom=16,
            zoom_start=14,
            #scaleRadius= True,
            #scale_radius=True,
            
            
            )
    lat_lon=datos_csv[['latitud','longitud','pot_db']].values
    
    
    colormap = cm.LinearColormap(colors=[ 'blue', 'cyan', 'yellow', 'orange', 'red'],
                             index=[-120, -110, -100, -95, -90], vmin=-120, vmax=-90,
                             caption='Gradiente de la señal en dBm 4G')

    m.add_child(colormap);                     

    mapa_calor=HeatMap(
                
                #[lat_,lon_,pot_], 
                
                lat_lon,
                
                name='Mapa de Calor', 
                min_opacity=0, 
                max_zoom=14,
                radius=7.2, 
                blur=2, 
                
                gradient=None, 
                overlay=True, 
                control=True, 
                show=True
                )
    mapa_calor.add_to(m)
    m.save('map_filtro.html')
    m = m._repr_html_()
    
    context = {
        'filtro':mediFitro,
        'datos':datos,
        'map':m,
    }
    

    return render(request, 'aplicacion/api_maps.html', context)

def cargar_csv(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)

    return render(request, 'aplicacion/user_csv.html', context)

def lista_csv(request):
    user_id = request.user.id
    csvs = user_csvs.objects.filter(id_usr=user_id)
    datos_csv = csvs
    context = {
        'datos':datos_csv,

    }
    return render(request, 'aplicacion/csv_list.html', context)

def cargarusr_csv(request):

    
    if request.method == 'POST':
        form = csvForm(request.POST, request.FILES)
        username = request.user.username
        user_id = request.user.id
        if form.is_valid():
            instance = form.save(commit=False)
            instance.usuario = username
            instance.id_usr = user_id
            instance.save()
            

            return redirect('user_csv')
    else:
        form = csvForm()
    return render(request, 'aplicacion/cargar_csv.html',{
        'form': form
    })

def borrarcsv(request, pk):
    if request.method == 'POST':
        
        csvfile = user_csvs.objects.get(pk=pk)
        csvfile.delete()
        return redirect('user_csv')

def vermap(request, pk):
    
    csvfile = user_csvs.objects.get(pk=pk)
    

    datos_csv=pd.read_csv(csvfile.archivocsv)
    data_html=datos_csv.to_html()
    if(datos_csv.empty):
        default_lat = -17.4140
        default_lon = -66.1653
    else:
        default_lat= datos_csv['latitud'].mean()
        default_lon= datos_csv['longitud'].mean()
    m = folium.Map(
            width='100%', 
            height='100%', 
            max_zoom=18, 
            min_zoom=18,
            zoom_start=18, 
            location=(default_lat, default_lon),
            
            )
    lat_lon=datos_csv[['latitud','longitud','pot']].values
    valcsv = datos_csv[['latitud','longitud','pot']].values
    mapa_calor=HeatMap(
                lat_lon, 
                name='Mapa de Calor', 
                min_opacity=0.5, 
                max_zoom=18, 
                radius=0, 
                blur=0, 
                gradient=None, 
                overlay=True, 
                control=True, 
                show=True)
    mapa_calor.add_to(m)
    m.save('/home/pi/Public/p1_v1/static/user_maps/user_map.html')
    m = m._repr_html_()
    context={
        'map':m,
        'data':csvfile,
        'datos':valcsv,
        'tabla':data_html,
        'csv_col':datos_csv.columns,
        'csv_row':datos_csv.to_dict('records'),

    }
    return render(request, 'aplicacion/usermap.html', context)

def turnoffserver(request):
    
    call("sudo poweroff", shell=True)
    return redirect(request,'login')


def tower_location(request):

    
    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=2.0)
    
    rootcsv='/home/pi/Public/p1_v1/static/CSV/towermap.csv'
    rootxlxs = '/home/pi/Public/p1_v1/static/CSV/towermap.xlsx'
    form = towerForm(request.POST or None)

    if form.is_valid():
    
    
        flag = 1
        while flag==1:
                    try:
                        line = ser.readline().decode('ISO-8859-1')
                        msg = pynmea2.parse(line)
                        if msg.sentence_type == "RMC":
                            lati=round(float(msg.latitude),6)
                            longi=round(float(msg.longitude),6)
                            if lati==0.0 or longi==0.0:
                                print("Sin Conexion")
                            
                            else:
                                print("Latitud:",lati,"Longitud:",longi)
                                print("-----------------------------------------")
                                flag=6
                    except serial.SerialException as e:
                        print('Error de conexion: {}'.format(e))
                        break
                    except pynmea2.ParseError as e:
                        print('Data error: {}'.format(e))
                        continue
        cell_id = form.cleaned_data.get('cell_id')
        observacion = form.cleaned_data.get('observacion')
        operador = form.cleaned_data.get('operador')
        torre_type = form.cleaned_data.get('torre')
        altura = form.cleaned_data.get('altura')
        instance = form.save(commit=False)
        instance.cell_id = cell_id
        instance.observacion = observacion
        instance.operador = operador
        instance.torre = torre_type
        instance.altura = altura
        instance.latitud = lati
        instance.longitud = longi
        instance.save()
        print("funco")
        print("funco")
    data_display_tower = torre.objects.all().order_by('-id')
    tower_filt = towerFilter(request.GET, queryset=data_display_tower)
    datos = tower_filt.qs
    with open(rootcsv, 'w') as crearcsv:
        writer = csv.writer(crearcsv)
        writer.writerow([
            'cell_id',
            'lac',
            'mnc',
            'latitud', 
            'longitud',
            'fecha',
            'observacion',
            'operador',
            ])
        for dat in datos.values_list(
            'cell_id',
            'lac',
            'mnc',
            'latitud', 
            'longitud',
            'fecha',
            'observacion',
            'operador',
            ):
            writer.writerow(dat)

    datos_csv=pd.read_csv(rootcsv)
    if(datos_csv.empty):
        default_lat = -17.4140
        default_lon = -66.1653
    else:
        default_lat= datos_csv['latitud'].mean()
        default_lon= datos_csv['longitud'].mean()
    


    m = folium.Map(
            width='100%', 
            height='100%', 
            location=(default_lat, default_lon),
            tiles='OpenStreetMap',
            control_scale=True,
            #min_zoom=14, 
            #max_zoom=18,
            zoom_start=14,
            )
    tower_icon = folium.CustomIcon(
        '/home/pi/Public/p1_v1/static/icons/tower.png',
        icon_size=(14,14), 
        icon_anchor=None, 
        shadow_image=None, 
        shadow_size=None, 
        shadow_anchor=None, 
        popup_anchor=None)

    
    
    for index, data in datos_csv.iterrows():
        tower_icon = folium.CustomIcon(
        '/home/pi/Public/p1_v1/static/icons/tower.png',
        icon_size=(14,14), 
        icon_anchor=None, 
        shadow_image=None, 
        shadow_size=None, 
        shadow_anchor=None, 
        popup_anchor=None)
        lat_lon = [data['latitud'], data['longitud']]
        if data['mnc'] == 1:
            operador_mnc = "Viva"
        if data['mnc'] == 2:
            operador_mnc = "Entel"
        if data['mnc'] == 3:
            operador_mnc = "Tigo"
        folium.Marker(lat_lon,
                popup = f'Cell ID:{data["cell_id"]}\n Operador:{operador_mnc}\n Lac:{data["lac"]}',
                icon = tower_icon,

                ).add_to(m)
              
    
    m.save('/home/pi/Public/p1_v1/static/Maps/towermap-F.html')
    m = m._repr_html_()

    context = {
        'form':form,
        'filtro':tower_filt,
        'datos':datos,
        'map':m,
    }
    

    return render(request, 'aplicacion/torre.html', context)

def delete_tower(request, pk):
    if request.method == 'POST':
        torre_id = torre.objects.get(pk=pk)
        torre_id.delete()
    return redirect('torres')

def tower_info(request, pk):

    
    torre_id = torre.objects.get(pk=pk)
    lati_t=torre_id.latitud
    longi_t=torre_id.longitud
    print(lati_t, longi_t)
    map_v = folium.Map(
        width='100%', 
        height='100%', 
        location=(lati_t,longi_t),
        tiles='OpenStreetMap',
        control_scale=True,
        #min_zoom=14, 
        #max_zoom=18,
        zoom_start=14,
        )
    tower_icon = folium.CustomIcon(
        '/home/pi/Public/p1_v1/static/icons/tower.png',
        icon_size=(14,14), 
        icon_anchor=None, 
        shadow_image=None, 
        shadow_size=None, 
        shadow_anchor=None, 
        popup_anchor=None)
    folium.Marker([lati_t,longi_t],
        popup="%s" %torre_id.cell_id, 
        name = "antena",
        tooltip=None, 
        icon=tower_icon, 
        control=True,
        
        ).add_to(map_v)
   
    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=2.0)
    modem = serial.Serial('/dev/ttyUSB2', 9600, timeout=2.0)
    form = tdataForm(request.POST or None)
 
  
    if form.is_valid():
        flag = 1
        while flag==1:
                    try:
                        line = ser.readline().decode('ISO-8859-1')
                        msg = pynmea2.parse(line)
                        if msg.sentence_type == "RMC":
                            lati=round(float(msg.latitude),6)
                            longi=round(float(msg.longitude),6)
                            modem.write(b'AT+CFUN=1\r')
                            time.sleep(0.9)
                            modem.write(b'AT+CSQ\r')
                            time.sleep(0.9)
                            modem.write(b'AT+CIMI\r')
                            time.sleep(0.9)
                            modem.write(b'ATI\r')
                            time.sleep(0.9)
                            modem.write(b'AT+ZRSSI\r')
                            time.sleep(0.9)
                            at=modem.readlines()
                            atc=str(at).replace("\\"," ")
                            atcc=atc.replace("'"," ")
                            #print(atcc)
                            m = re.findall('CSQ: (.+?) ',str(atcc))
                            m1 = re.findall('ZRSSI: (.+?),',str(atcc))
                            man = re.findall('Manufacturer: (.+?) r',str(atcc))
                            mod = re.findall('Model: (.+?) ',str(atcc))
                            ime = re.findall('IMEI: (.+?) ',str(atcc))
                            x = str(re.findall('CIMI r r n , b (.+?) ',str(atcc)))
                            imsi = re.findall('[0-9]+',str(x))[0]
                            #print(imsi)
                            mcc=str(imsi)[0:3]
                            mnc=str(imsi)[3:5]
                            mm=m[0].replace(",",".")
                            mm1=m1[0].replace(",",".")
                            #print(mm)
                            y=round(float(mm))
                            y1=round(float(mm1))
                            manufacturer=str(man[0])
                            model=str(mod[0])
                            imei=str(ime[0])
                            operador = data_bolivia.objects.get(mnc=mnc)
                            #print(manufacturer,model,imei)
                            if y==100 or y==99 or lati==0.0 or longi==0.0:
                                print("Sin Conexion")
                            else:
                                #ydbm=(-113+((y)*2))
                                ydbm=(y1*-1)
                                print("RED: ",operador.operador)
                                print("MODELO: ",model)
                                print("FABRICANTE: ",manufacturer)
                                print("IMEI: ",imei)
                                print("IMSI: ",imsi)
                                print("MCC: ",mcc)
                                print("MNC: ",mnc)
                                print("RSSI:",y)
                                print("Potencia:",ydbm,"dBm")
                                print("Latitud:",lati,"Longitud:",longi)
                                print("-----------------------------------------")
                                print(y1)
                                flag=6
                    except serial.SerialException as e:
                        print('Error de conexion: {}'.format(e))
                        break
                    except pynmea2.ParseError as e:
                        print('Data error: {}'.format(e))
                        continue
        point1 = (lati,longi)
        #point1 = (-17.357008,-66.198296)
        point2 = (lati_t, longi_t)
        #distance = round(((geodesic(point1, point2).km)/1000), 2)
        #distance = round(geodesic(point1, point2).meters, 2)
        #print(distance)
        test_name = form.cleaned_data.get('test_name')
        observacion = form.cleaned_data.get('observacion')
        instance = form.save(commit=False)
        instance.test_name = test_name
        instance.observacion = observacion
        instance.imsi = imsi
        instance.mcc = mcc
        instance.mnc = mnc
        instance.operador = operador.operador
        instance.latitud = lati
        instance.longitud = longi
        instance.pot_db = ydbm
        instance.rssi = y
        instance.modelo = model
        #instance.distancia = distance
        instance.torre_name = torre_id.cell_id
        instance.save()

    data_display = torre_measure.objects.filter(torre_name="%s" %torre_id.cell_id).order_by('-id')
    filtro = towermeasureFilter(request.GET, queryset=data_display)
    datos_p = filtro.qs

    rootcsv='/home/pi/Public/p1_v1/static/CSV/towermap_area.csv'
    rootxlxs = '/home/pi/Public/p1_v1/static/CSV/towermap_area.xlsx'

    with open(rootcsv, 'w') as crearcsv:
        writer = csv.writer(crearcsv)
        writer.writerow([
            'torre_name', 'pot_db', 'distancia', 'latitud', 'longitud', 'fecha', 'observacion',
            'operador','imsi', 'modelo',
            ])
        for dat in data_display.values_list(
            'torre_name', 'pot_db', 'distancia', 'latitud', 'longitud', 'fecha', 'observacion',
            'operador', 'imsi', 'modelo',
            ):
            writer.writerow(dat)
    
    datos_csv=pd.read_csv(rootcsv)
    datos_csv["pot_intp"]=datos_csv['pot_db'].apply(lambda x: interp(x,[-90,-50],[0,29]))
    datos_csv.to_csv(rootcsv, index=False)
    
    datos_csv=pd.read_csv(rootcsv)
    datos_csv=datos_csv.sort_values(by=["distancia"],ascending=False)

    areaentel = folium.FeatureGroup(name='Entel', control=True)
    areatigo = folium.FeatureGroup(name='Tigo', control=True)
    areaviva = folium.FeatureGroup(name='Viva', control=True)

    for i, r in datos_csv.iterrows():
        if r['operador'] == "Entel":
            group = areaentel
            print(r['operador'])   
        elif r['operador'] == "Tigo":
            group = areatigo  
            print(r['operador'])   
        elif r['operador'] == "Viva":
            group = areaviva 
            print(r['operador'])     

        blue = Color("blue")
        colors = list(blue.range_to(Color("red"),30))
        cvalue = colors[round(float(r['pot_intp']))]
        print(cvalue)
        radio_t = round(float(r['distancia']))    
        folium.Circle([r['latitud'],r['longitud']],
                        radius=radio_t,
                        
                        fill=True,
                        fill_opacity = 0.6,
                        fill_color = '%s' %cvalue,
                        stroke = False,
                        interactive = True,
                        bubblingMouseEvents = True,
                        tooltip = "%s metros, %sdBm" %(r['distancia'],r['pot_db']),
                        control = True,
                        name = "%s" %(r['operador']),
                    ).add_to(group)   
     

    map_v.add_child(areaentel)
    map_v.add_child(areatigo)
    map_v.add_child(areaviva)
    folium.LayerControl().add_to(map_v)
    
    map_v.save('/home/pi/Public/p1_v1/static/Maps/towermeasure.html')
    map_v = map_v._repr_html_()
    #datos_p = data_display
    
    context={
            'map':map_v, 
            'tower_d':torre_id,
            'form':form, 
            'datos':datos_p,
            'filtro':filtro,
            }
        
    return render(request, 'aplicacion/torre_data.html', context)



def tower_location_manual(request):
    data = {}
    if "GET" == request.method:
        return render(request, 'aplicacion/torre_manual.html', data)
    # if not GET, then proceed
    try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return redirect("torres_manual")
        #if file is too large, return
        
        file_data = pd.read_csv(csv_file)
        row_iter = file_data.iterrows()

        objs = [

            torre(

                cell_id = row['cell_id'],
                lac  = row['lac'],
                observacion  = "ninguna",
                mnc  = row['operador'],
                torre  = "torre",
                latitud  = row['latitud'],
                longitud  = row['longitud'],

            )

            for index, row in row_iter

        ]

        torre.objects.bulk_create(objs)

    except Exception as e:
        logging.getLogger("error_logger").error("No se pudo cargar el archivo. "+repr(e))
        messages.error(request,"No se pudo cargar el archivo. "+repr(e))

    return redirect("torres_manual") 


def delete_data_t(request):
    torre.objects.all().delete()
    return redirect('home')





































def maps_appV1(request):

    data_display = medidas.objects.all().order_by('-id')
    rootcsv='mapsV1.csv'
    rootcsv1='maps1V1.csv'
    rootxlxs = 'mapsV1.xlsx'



    mediFitro = tablaFilter(request.GET, queryset=data_display)
    datos = mediFitro.qs
    

    with open(rootcsv, 'w') as crearcsv:
        writer = csv.writer(crearcsv)
        writer.writerow([
            'latitud', 
            'longitud',
            'pot',
            'usuario',
            'fecha',
            'test_name',
            'observacion',
            'operador',
            'rssi',
            'marca',
            'imsi',
            'modelo',
            

            ])
        for dat in datos.values_list(
            'latitud',
            'longitud',
            'pot_db',
            'usuario',
            'fecha',
            'test_name',
            'observacion',
            'operador',
            'rssi',
            'marca',
            'imsi',
            'modelo'

            
            ):

            writer.writerow(dat)

    
    newd_csv=pd.read_csv(rootcsv)
    newd_csv["pot_db"]=newd_csv['pot'].apply(lambda x: interp(x,[-120,-50],[0,29]))
    newd_csv.to_csv(rootcsv1, index=False)
    datos_csv=pd.read_csv(rootcsv1)
    datos_csv1=pd.read_csv(rootcsv)
    datos_csv1.to_excel(rootxlxs,index = None, header=True)
    if(datos_csv.empty):
        default_lat = -17.4140
        default_lon = -66.1653
    else:
        default_lat= datos_csv['latitud'].mean()
        default_lon= datos_csv['longitud'].mean()

    print(default_lat, default_lon)
  
    
    m = folium.Map(
            width='100%', 
            height='100%', 
            location=(default_lat, default_lon),
            tiles='OpenStreetMap',
            control_scale=True,
            min_zoom=10, 
            max_zoom=16,
            zoom_start=14,
            #scaleRadius= True,
            #scale_radius=True,
            
            
            )
    lat_lon=datos_csv[['latitud','longitud','pot_db']].values
    lat_lon1=datos_csv[['latitud','longitud','pot_db']].values
    
    
    colormap = cm.LinearColormap(colors=[ 'blue', 'cyan', 'yellow', 'orange', 'red'],
                             index=[-120, -110, -100, -95, -90], vmin=-120, vmax=-90,
                             caption='Gradiente de la señal en dBm 4G')

    m.add_child(colormap);  
    pp=0
    for i, r in datos_csv.iterrows():

        
        blue = Color("blue")
        colors = list(blue.range_to(Color("red"),30))
        cvalue = colors[round(float(r['pot_db']))]
        print(cvalue)
        
        pp += 1
        folium.Circle([r['latitud'],r['longitud']],
                        radius=100,
                        fill=True,
                        #color = 'grey',
                        fill_opacity = 0.2,
                        #fill_color = '#48c6dd',
                        fill_color = '%s' %cvalue,
                        stroke = False,
                        interactive = True,
                        bubblingMouseEvents = True,
                        tooltip = '%s' %pp,
                    ).add_to(m)                   

    m.save('map_filtroV1.html')
    m = m._repr_html_()
    
    context = {
        'filtro':mediFitro,
        'datos':datos,
        'map':m,
    }
    

    return render(request, 'aplicacion/api_mapsV1.html', context)