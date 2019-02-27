from django.shortcuts import render
from padronelectoral.models import Elector
from django.http import JsonResponse
from rest_framework.views import APIView


# Create your views here.

def load_index(request):
    """
    This function render the index.html, this is the main page
    :param request:
    :return: Render index.html
    """
    return render(request, 'index.html')


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
