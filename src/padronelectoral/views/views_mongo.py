from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from crpadron import settings
from padronelectoral.forms import ElectorForm
from padronelectoral.utils import MongoClientUtil


def mongo_database():
    """
    :return: Return the configuration of the mongoDB
    """
    instance = MongoClientUtil.getInstance()
    return instance.admin


def get_electors(request):
    """
    In this function, we can find the electors data, passing the full name or idCard
    :param request:
    :return: Return the render, either for Mongo or ORM template
    """
    # by default, its important to send the actual database that we are using
    context = {'database': settings.ACTIVE_DATABASE}
    if request.method == 'POST':
        elector_list = []
        data = request.POST.get('input')
        # if the actual database in the configuration is "ORM", we find the information by this way

        # try to convert the input to int. This is because de idCard is always a number
        # and if it is an string value, the search should be by full name
        try:
            data_id = int(data)
            elector = mongo_database().electors.find_one({'idCard': data_id})
            province = find_collection(mongo_database().province, 'id_province', elector)
            canton = find_collection(mongo_database().canton, 'id_canton', elector)
            district = find_collection(mongo_database().district, 'codelec', elector)
            elector['id_district'] = elector['codelec']
            elector['province'] = province['name']
            elector['canton'] = canton['name']
            elector['district'] = district['name']
            elector_list.append(elector)

        # and if it is an string value, the search should be by full name
        except:
            # regex is to define a full name similar by any input data.
            # Data.upper() is necessary because in the database, all the full name are capitalized
            electors = mongo_database().electors.find({'fullName': {'$regex': data.upper()}})
            for element in electors:
                province = find_collection(mongo_database().province, 'id_province', element)
                canton = find_collection(mongo_database().canton, 'id_canton', element)
                district = find_collection(mongo_database().district, 'codelec', element)
                element['id_district'] = element['codelec']
                element['province'] = province['name']
                element['canton'] = canton['name']
                element['district'] = district['name']
                elector_list.append(element)
            context['message'] = "NOTE: This search is sorted by province, canton and full name (in that order)"
        context['info'] = elector_list
        return render(request, 'index.html', context)


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
    # in Mongo, the stats are load in the first command. So, we can use the stats
    # in the current execution
    province = mongo_database().province.find_one({'code': str(pk)})
    return render(request, 'stats.html', {'totalM': province['stats_male'],
                                          'totalF': province['stats_female'],
                                          'totalE': province['stats_total'],
                                          'location': province['name']})


def get_canton_data(request, pk):
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
    # in Mongo, the stats are load in the first commando. So, we can use the stats
    # in the current execution
    province = mongo_database().district.find_one({'code': str(pk)})
    return render(request, 'stats.html', {'totalM': province['stats_male'],
                                          'totalF': province['stats_female'],
                                          'totalE': province['stats_total'],
                                          'location': province['name']})


def get_district_electors(request, pk):
    """
    used in district data template to pass pk as context to obtain the codelec
    on the javascript
    :param request:
    :param pk: district id
    :return: district name and codelec
    """
    district = mongo_database().district.find_one({'code': pk})
    return render(request, 'district-data.html', {'district': district, 'codelec': pk})


def django_datatable(request, district):
    electors = mongo_database().electors.find({'codelec': str(district)}).sort('fullName')
    p = Paginator(electors, 10)
    actual = p.page(1)
    datalist = [[x['idCard'], x['fullName'], x['gender']] for x in electors]
    data = {
        "draw": 1,
        "recordsTotal": electors.count(),
        "recordsFiltered": actual.object_list.count(),
        "data": datalist
    }
    return JsonResponse(data)


@login_required
def createElector(request):
    context = {}
    if request.method == 'POST':
        form = ElectorForm(request.POST)
        find_elector = mongo_database().electors.find_one({'idCard': int(form.data.get('idCard'))})

        if find_elector:
            context['error'] = 'This id card already exist.'

        else:
            codelec = form.data.get('codelec')
            elector = {'idCard': int(form.data.get('idCard')), 'codelec': codelec,
                        'fullName': form.data.get('fullName'), 'gender': form.data.get('gender'),
                       'cad_date': form.data.get('cad_date'), 'board': form.data.get('board'),
                       'id_province': codelec[0], 'id_canton': codelec[:3]}

            mongo_database().electors.save(elector)
            return redirect('index')

    else:
        form = ElectorForm()
    return render(request, 'create_elector.html', {'form': form, 'error': context})
