from rest_framework import serializers
from .models import Elector


class electors_serializer(serializers.ModelSerializer):
    class Meta():
        model = Elector
        # Current fields for testing purposes
        fields = ('idCard', 'fullName', 'gender')
