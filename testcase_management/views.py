
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions

from .serializers import ProjectSerializer
from .permissions import IsOwnerOrReadOnly

from . import models


@api_view(['GET', 'POST'])
def project_list(request):
    if request.method == 'GET':
        projects = models.Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = models.Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args,  **kwargs)

    # def get(self, request):
    #     projects = models.Project.objects.all()
    #     serializer = ProjectSerializer(projects, many=True)
    #     return Response(serializer.data)
    #
    # def post(self, request):
    #     serializer = ProjectSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Project(mixins.RetrieveModelMixin,
              mixins.UpdateModelMixin,
              mixins.DestroyModelMixin,
              generics.GenericAPIView):

    queryset = models.Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    # def get_object(self, pk):
    #     try:
    #         return models.Project.objects.get(pk=pk)
    #     except models.Project.DoesNotExist:
    #         raise Http404
    #
    # def get(self, request, pk):
    #     project = self.get_object(pk)
    #     serializer = ProjectSerializer(project)
    #     return Response(serializer.data)
    #
    # def put(self, request, pk):
    #     project = self.get_object(pk)
    #     serializer = ProjectSerializer(project, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk):
    #     project = self.get_object(pk)
    #     project.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)






