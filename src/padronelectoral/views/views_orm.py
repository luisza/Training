from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse

from crpadron import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings

from padronelectoral.forms import ElectorForm
from padronelectoral.models import Elector, Province, Canton, District


def get_electors(request):
    """
    In this function, we can find the electors data, passing the full name or id_card
    :param request:
    :return: Return the render, either for Mongo or ORM template
    """
    # by default, its important to send the actual database that we are using
    context = {'database':settings.ACTIVE_DATABASE}
    if request.method == 'POST':
        elector_list = []
        data = request.POST.get('input')
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


def get_province_data(request, pk):
    """
    This function is to get the province stats
    :param request:
    :param pk: In this context, pk is the code in Province
    :return: Return the stats of the province filtering by this pk
    """
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


def get_canton_data(request, pk):
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


def get_district_data(request, pk):
    """
    Get the district total males, females and total electors.
    :param request:
    :param pk: The district pk
    :return: The render with the stats.
    """
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


def django_datatable(request, district):
    electors = Elector.objects.filter(codelec=district).order_by('fullName')
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


@login_required
def createElector(request):
    if request.method == 'POST':
        form = ElectorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')

    else:
        form = ElectorForm()
    return render(request, 'create_elector.html', {'form': form})