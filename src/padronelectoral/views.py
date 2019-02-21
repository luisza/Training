from django.shortcuts import render, get_object_or_404, redirect

from padronelectoral.loader.MongoLoader import *
from .forms import ElectorForm
from django.contrib.auth.decorators import login_required
from .models import Elector, Province, District, Canton
from django.http import JsonResponse
from .Serializers import electors_serializer
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.conf import settings


# Create your views here.


def actual_database():
    """
    :return: Return the name of the active database
    """
    return settings.ACTIVE_DATABASE


def mongo_database():
    """
    :return: Return the configuration of the mongoDB
    """
    instance = MongoDB()
    return instance.database


def django_datatable(request, district):
    electors = Elector.objects.filter(codelec=district)
    p = Paginator(electors, 10)
    actual = p.page(1)
    datalist = [[x.idCard, x.fullName, x.gender] for x in actual.object_list]

    data = {
        "draw": 1,
        "recordsTotal": electors.count(),
        "recordsFiltered": len(actual.object_list),
        "data": datalist
    }
    return JsonResponse(data)


def load_index(request):
    """
    This function render the index.html, this is the main page
    :param request:
    :return: Render index.html
    """
    return render(request, 'index.html')


def get_electors(request):
    """
    In this function, we can find the electors data, passing the full name or id_card
    :param request:
    :return: Return the render, either for Mongo or ORM template
    """
    # by default, its important to send the actual database that we are using
    context = {'database': actual_database()}
    if request.method == 'POST':
        elector_list = []
        data = request.POST.get('input')
        # if the actual database in the configuration is "ORM", we find the information by this way
        if actual_database() == "ORM":
            # try to convert the input to int. This is because de id_card is always a number
            try:
                data_id = int(data)
                elector = get_object_or_404(Elector, pk=data_id)
                elector_list.append(elector)
            except:
                # the list of electors similar to the input value. Ordered by codelec
                elector_list = Elector.objects.filter(fullName__icontains=data).order_by('codelec')
                context['message'] = "NOTE: This search is sorted by province, canton and full name (in that order)"
            context['info'] = elector_list
            return render(request, 'index.html', context)

        elif actual_database() == "MONGO":
            # try to convert the input to int. This is because de id_card is always a number
            # and if it is an string value, the search should be by full name
            try:
                data_id = int(data)
                elector = mongo_database().electors.find_one({'id_card': data_id})
                province = find_collection(mongo_database().province, 'id_province', elector)
                canton = find_collection(mongo_database().canton, 'id_canton', elector)
                district = find_collection(mongo_database().district, 'id_district', elector)
                elector['province'] = province['name']
                elector['canton'] = canton['name']
                elector['district'] = district['name']
                elector_list.append(elector)

            # and if it is an string value, the search should be by full name
            except:
                # regex is to define a full name similar by any input data.
                # Data.upper() is necessary because in the database, all the full name are capitalized
                electors = mongo_database().electors.find({'full_name': {'$regex': data.upper()}})
                for element in electors:
                    province = find_collection(mongo_database().province, 'id_province', element)
                    canton = find_collection(mongo_database().canton, 'id_canton', element)
                    district = find_collection(mongo_database().district, 'id_district', element)
                    element['province'] = province['name']
                    element['canton'] = canton['name']
                    element['district'] = district['name']
                    elector_list.append(element)
                context['message'] = "NOTE: This search is sorted by province, canton and full name (in that order)"
            context['info'] = elector_list
            return render(request, 'index_mongo.html', context)


def find_collection(table, id_to_find, elector):
    """
    This return the table information. In this way, we can use the name to add in the elector data
    :param table: Collection to find
    :param id_to_find: By this id we can find the data in the collection or table
    :param elector: This is the elector object to add the name of (province, canton or district)
    :return: Return the object (province, canton or district)
    """
    return table.find_one({'code': elector[id_to_find]})


def get_province_data(request, pk):
    """
    This function is to get the province stats
    :param request:
    :param pk: In this context, pk is the code in Province
    :return: Return the stats of the province filtering by this pk
    """
    if actual_database() == "ORM":
        province = get_object_or_404(Province, pk=pk)
        # By default, in the database. All the provinces have a -1 in the stats
        if province.stats_total == -1:
            print("--Calculating--")
            elector_list_by_canton = Elector.objects.filter(codelec__canton__province=pk)
            province.stats_female = elector_list_by_canton.filter(gender=2).count()
            province.stats_male = elector_list_by_canton.filter(gender=1).count()
            province.stats_total = province.stats_female + province.stats_male
            province.save()

        return render(request, 'stats.html', {'totalM': province.stats_male,
                                              'totalF': province.stats_female,
                                              'totalE': province.stats_total,
                                              'location': province})
    elif actual_database() == "MONGO":
        # in Mongo, the stats are load in the first command. So, we can use the stats
        # in the current execution
        province = mongo_database().province.find_one({'code': str(pk)})
        return render(request, 'stats.html', {'totalM': province['stats_male'],
                                              'totalF': province['stats_female'],
                                              'totalE': province['stats_total'],
                                              'location': province['name']})


def get_canton_data(request, pk):
    if actual_database() == "ORM":
        canton = get_object_or_404(Canton, pk=pk)
        if canton.stats_total == -1:
            print("--Calculating--")
            elector_list_by_canton = Elector.objects.filter(codelec__canton=canton)
            canton.stats_female = elector_list_by_canton.filter(gender=2).count()
            canton.stats_male = elector_list_by_canton.filter(gender=1).count()
            canton.stats_total = canton.stats_female + canton.stats_male
            canton.save()

        return render(request, 'stats.html', {'totalM': canton.stats_male,
                                              'totalF': canton.stats_female,
                                              'totalE': canton.stats_total,
                                              'location': canton})
    elif actual_database() == "MONGO":
        # in Mongo, the stats are load in the first command. So, we can use the stats
        # in the current execution
        province = mongo_database().canton.find_one({'code': str(pk)})
        return render(request, 'stats.html', {'totalM': province['stats_male'],
                                              'totalF': province['stats_female'],
                                              'totalE': province['stats_total'],
                                              'location': province['name']})

def get_district_data(request, pk):
    """
    Get the district total males, females and total electors.
    :param request:
    :param pk: The district pk
    :return: The render with the stats.
    """
    if actual_database() == "ORM":
        district = get_object_or_404(District, pk=pk)
        if district.stats_total == None:
            print("--Calculating--")
            elector_list = Elector.objects.filter(codelec=pk)
            district.stats_female = elector_list.filter(gender=2).count()
            district.stats_male = elector_list.filter(gender=1).count()
            district.stats_total = district.stats_female + district.stats_male
            district.save()
        return render(request, 'stats.html', {'totalM': district.stats_male,
                                              'totalF': district.stats_female,
                                              'totalE': district.stats_total,
                                              'location': district})
    elif actual_database() == "MONGO":
        # in Mongo, the stats are load in the first commando. So, we can use the stats
        # in the current execution
        province = mongo_database().district.find_one({'code': str(pk)})
        return render(request, 'stats.html', {'totalM': province['stats_male'],
                                              'totalF': province['stats_female'],
                                              'totalE': province['stats_total'],
                                              'location': province['name']})

@login_required
def createElector(request):
    if request.method == 'POST':
        form = ElectorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('loadIndex')

    else:
        form = ElectorForm()
    return render(request, 'create_elector.html', {'form': form})


def get_district_electors(request, pk):
    """
    used in district data template to pass pk as context to obtain the codelec
    on the javascript
    :param request:
    :param pk: district id
    :return: district name and codelec
    """
    district = get_object_or_404(District, pk=pk)
    return render(request, 'district-data.html', {'district': district, 'codelec': pk})


class ElectorsOnDistrict(APIView):
    # Class using django rest serializer to return a JSON readable by the datatables

    def get(self, request, pk):
        """
        Returns a JSonResponse with the serialized list and primary key needed for each district data
        :param request:
        :param pk: district id
        :return: Json list readable in datatable ajax method
        """
        elector_list = Elector.objects.filter(codelec=pk)
        serializer = electors_serializer(elector_list, many=True)
        return JsonResponse(serializer.data, safe=False)
