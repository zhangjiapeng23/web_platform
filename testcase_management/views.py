
from rest_framework import mixins, status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .serializers import *
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly

from . import models
from .jenkins_controller.jenkins_controller import JenkinsController
from mobile_QA_web_platform.utils.pagination import StandardResultsSetPagination


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
    lookup_field = 'name'

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


class TestcaseProjectList(generics.ListCreateAPIView):
    queryset = models.Testcase.objects.all()
    serializer_class = TestcaseSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        project = self.kwargs['project']
        return models.Testcase.objects.filter(project__name=project)

    def create(self, request, *args, **kwargs):
        serializer = TestcaseProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        name = self.kwargs['project']
        project = models.Project.objects.get(name=name)
        serializer.save(project=project)


class Testcase(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Testcase.objects.all()
    serializer_class = TestcaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        project = self.kwargs['project']
        return models.Testcase.objects.filter(project__name=project)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = TestcaseUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class TestTaskList(generics.ListCreateAPIView):
    queryset = models.TestTask.objects.all()
    serializer_class = TestTasklistSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_create_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        return TestTaskCreateSerializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_create_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TestTaskProjectList(generics.ListCreateAPIView):
    queryset = models.TestTask.objects.all()
    serializer_class = TestTasklistSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        project = self.kwargs['project']
        return models.TestTask.objects.filter(project__name=project)

    def perform_create(self, serializer):
        project = self.kwargs['project']
        name = models.Project.objects.get(name=project)
        serializer.save(owner=self.request.user, project=name)

    def get_create_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        return TestTaskProjectCreateSerializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_create_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)






class TestTask(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.TestTask.objects.all()
    serializer_class = TestTaskCreateSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


class TestReportList(generics.ListCreateAPIView):
    queryset = models.Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (permissions.AllowAny,)


class TestReport(generics.RetrieveDestroyAPIView):
    queryset = models.Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (IsAdminOrReadOnly,)


@api_view(http_method_names=['GET'])
@permission_classes(permission_classes=(permissions.IsAuthenticated,))
def execute_task(request):
    data = request.data
    jenkins = JenkinsController()
    jenkins.execute_test_task()
    return Response()





