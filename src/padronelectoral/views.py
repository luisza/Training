from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from .models import Elector, Province, District, Canton
from .forms import SearchForm
# Create your views here.


def loadIndex(request):
    return render(request, 'index.html')

def get_electors(request):
    if request.method=='POST':
        elector_list = []
        data = request.POST.get('input')
        try:
            data_id = int(data)
            elector = get_object_or_404(Elector, pk=data_id)
            elector_list.append(elector)
        except:
            elector_list = Elector.objects.filter(fullName__istartswith = data)

        return render(request,'index.html',{'info':elector_list})



def get_province_data(request,pk):
    province = get_object_or_404(Province, pk=pk)
    if province.stats_total == None:
        print("--Calculating--")
        elector_list_by_canton = Elector.objects.filter(codelec__canton__province = pk)
        province.stats_female = elector_list_by_canton.filter(gender=2).count()
        province.stats_male = elector_list_by_canton.filter(gender=1).count()
        province.stats_total = province.stats_female + province.stats_male
        province.save()

    return render(request, 'stats.html', {'totalM': province.stats_male,
                                              'totalF': province.stats_female,
                                          'totalE': province.stats_total,
                                          'location': province})
    '''
    elector_prov = Elector.objects.filter(codelec__canton__province=prov)
    m = elector_prov.filter(gender=1).count()
    f = elector_prov.filter(gender=2).count()
    total = elector_prov.count()
    prov = Province.object.all().aggregate(
        sumfemale=Count(canton_district_codelec_gender=2),
        summale=Count(canton_district_codelec_gender=1))

    prov.sumfemale
    prov.summale 
    '''


def get_canton_data(request,pk):
    canton = get_object_or_404(Canton, id=pk)
    if canton.stats_total == None:
        print("--Calculating--")
        elector_list_by_canton = Elector.objects.filter(codelec__canton= canton)
        canton.stats_female = elector_list_by_canton.filter(gender=2).count()
        canton.stats_male = elector_list_by_canton.filter(gender=1).count()
        canton.stats_total = canton.stats_female + canton.stats_male
        canton.save()

    return render(request, 'stats.html',{'totalM': canton.stats_male,
                                    'totalF': canton.stats_female,
                                    'totalE': canton.stats_total,
                                    'location':canton})

def get_district_data(request, pk):
    """
    Get the district stats
    :param request:
    :param pk: The district pk
    :return: The render with the stats.
    """
    district = get_object_or_404(District, pk=pk)
    if district.stats_total == None:
        print ("--Calculating--" )
        elector_list = Elector.objects.filter(codelec = pk)
        district.stats_female = elector_list.filter(gender=2).count()
        district.stats_male = elector_list.filter(gender=1).count()
        district.stats_total = district.stats_female+district.stats_male
        district.save()
    return render(request,'stats.html',{'totalM': district.stats_male,
                                    'totalF': district.stats_female,
                                    'totalE': district.stats_total,
                                    'location':district})



#class CantonView(DetailView):
#    template = 'canton_template.html'