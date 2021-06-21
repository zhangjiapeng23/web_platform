
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions

from .serializers import ProjectSerializer, TestcaseSerializer, TestTaskSerializer, ReportSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly

from . import models


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


class Project(mixins.RetrieveModelMixin,
              mixins.UpdateModelMixin,
              mixins.DestroyModelMixin,
              generics.GenericAPIView):

    queryset = models.Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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


class TestcaseList(generics.ListCreateAPIView):
    queryset = models.Testcase.objects.all()
    serializer_class = TestcaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class Testcase(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Testcase.objects.all()
    serializer_class = TestcaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TestTaskList(generics.ListCreateAPIView):
    queryset = models.TestTask.objects.all()
    serializer_class = TestTaskSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TestTask(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.TestTask.objects.all()
    serializer_class = TestTaskSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


class TestReportList(generics.ListCreateAPIView):
    queryset = models.Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (permissions.AllowAny,)


class TestReport(generics.RetrieveDestroyAPIView):
    queryset = models.Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (IsAdminOrReadOnly,)



