from django.urls import path
from crpadron import settings
from padronelectoral.views import views

if settings.ACTIVE_DATABASE == "MONGO":
    from padronelectoral.views import views_mongo as views_db
elif settings.ACTIVE_DATABASE == "ORM":
    from padronelectoral.views import views_orm as views_db

urlpatterns = [
    path('', views.load_index, name='index'),
    path('search', views_db.get_electors, name='get_electors'),
    path('stats/province/<int:pk>', views_db.get_province_data, name='get_province_data'),
    path('stats/canton/<int:pk>', views_db.get_canton_data, name='get_canton_data'),
    path('stats/district/<int:pk>', views_db.get_district_data, name='get_district_data'),
    path('datatables/<int:district>', views_db.django_datatable, name="datatables_serversite"),
    path('district-data/<int:pk>', views_db.get_district_electors, name='get_district_data'),
    path('district-electors/<int:pk>', views.ElectorsOnDistrict.as_view(), name='datatables_data'),
    path('newelector', views_db.createElector, name='new_elector')
]
