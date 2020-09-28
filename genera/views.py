from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import GeneraSerializer
from django.apps import apps
Genus = apps.get_model('orchiddb', 'Genus')

class GeneraView(viewsets.ModelViewSet):
    queryset = Genus.objects.all()
    serializer_class = GeneraSerializer


@api_view(['GET'])
def view_genus(request):
    genera = Genus.objects.all()
    results = [genus.to_json() for genus in genera]
    return Response(results, status=status.HTTP_201_CREATED)

