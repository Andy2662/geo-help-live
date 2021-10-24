from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),

 
    path('app/',views.userMaps,name="app"),
    path('delete/',views.delete_data_t),
    path('app/tables/',views.maps_app,name="tablas"),
    path('app/torres/',views.tower_location,name="torres"),
    path('app/torres/manual/',views.tower_location_manual,name="torres_manual"),
    path('app/torres/delete_tower/<int:pk>/',views.delete_tower,name="borrar_torre"),
    path('app/torres/tower_details/<int:pk>/',views.tower_info,name="tower_details"),
  
    path('app/tablesV1/',views.maps_appV1,name="tablasV1"),
    #path('user_csv/',views.cargar_csv,name="cargar_csv"),

    path('user_csv/',views.lista_csv,name="user_csv"),
    path('user_csv/subir_csv/',views.cargarusr_csv,name="subir_csv"),
    path('user_csv/<int:pk>/',views.borrarcsv,name="borrar_csv"),
    path('user_csv/ver_csv/<int:pk>/',views.vermap,name="ver_csv"),

    path('register/',views.registerPage, name="register"),
    path('login/',views.loginPage, name="login"),
    path('logout/',views.logoutUser, name="logout"),
    path('poweroff/',views.turnoffserver, name="poweroff"),

 
]   
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)