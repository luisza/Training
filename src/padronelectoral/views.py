from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from .forms import SearchForm, ElectorForm
from django.contrib.auth.decorators import login_required
from .models import Elector, Province, District, Canton
from django.http import HttpResponse, JsonResponse
from .Serializers import electors_serializer
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.


def loadIndex(request):
    return render(request, 'index.html')

def get_electors(request):
    if request.method == 'POST':
        elector_list = []
        data = request.POST.get('input')
        try:
            data_id = int(data)
            elector = get_object_or_404(Elector, pk=data_id)
            elector_list.append(elector)
        except:
            #Changed to icontains for electors using a second name
            elector_list = Elector.objects.filter(fullName__icontains=data)

        return render(request, 'index.html', {'info': elector_list})



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



def get_canton_data(request,pk):
    canton = get_object_or_404(Canton, pk=pk)
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
    Get the district total males, females and total electors.
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
        district.stats_total = district.stats_female + district.stats_male
        district.save()
    return render(request, 'stats.html', {'totalM': district.stats_male,
                                          'totalF': district.stats_female,
                                          'totalE': district.stats_total,
                                          'location': district})


@login_required
def createElector(request):
    form = ElectorForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('loadIndex')
    return render(request, 'create_elector.html', {'form': form})

#class CantonView(DetailView):
#    template = 'canton_template.html'



def get_district_electors(request,pk):
    """
    used in district data template to pass pk as context to obtain the codelec
    on the javascript
    :param request:
    :param pk: district id
    :return: district name and codelec
    """
    district = get_object_or_404(District,pk=pk)
    return render(request,'district-data.html',{'district':district,'codelec':pk})

class ElectorsOnDistrict(APIViewdd):
    #Class using django rest serializer to return a JSON readable by the datatables

    def get(self,request,pk):
        """
        Returns a JSonResponse with the serialized list and primary key needed for each district data
        :param request:
        :param pk: district id
        :return: Json list readable in datatable ajax method
        """
        elector_list = Elector.objects.filter(codelec=pk)
        serializer = electors_serializer(elector_list,many=True)
        return JsonResponse(serializer.data,safe=False)