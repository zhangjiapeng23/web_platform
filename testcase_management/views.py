import json
import time
from threading import Thread, Lock

from rest_framework import mixins, status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .serializers import *
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly

from . import models
from .jenkins_controller.jenkins_controller import JenkinsController
from .jenkins_controller.model import TestTaskModel
from mobile_QA_web_platform.utils.pagination import StandardResultsSetPagination
from mobile_QA_web_platform.utils.views_mixin import BatchCreateModelMixin

lock = Lock()


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


class BatchCreateView(BatchCreateModelMixin, generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TestcaseProjectBatchCreate(BatchCreateView):
    queryset = models.Testcase.objects.all()
    serializer_class = TestcaseProjectCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        project = self.kwargs['project']
        return models.Testcase.objects.filter(project__name=project)

    def perform_create(self, serializer):
        project = self.kwargs['project']
        project_instance = models.Project.objects.get(name=project)
        serializer.save(project=project_instance)


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
    serializer_class = TestTaskListSerializer
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
    serializer_class = TestTaskListSerializer
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


class TaskRecordList(generics.ListCreateAPIView):
    queryset = models.TaskExecuteRecord.objects.all()
    serializer_class = TaskRecordSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        project = self.kwargs['project']
        return models.TaskExecuteRecord.objects.filter(task__project__name=project)


class TaskReportList(generics.ListCreateAPIView):
    queryset = models.Report.objects.all()
    serializer_class = TaskReportSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        build_url = request.data.get('build_url')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report_instance = self.perform_create(serializer)
        task_record_instance = models.TaskExecuteRecord.objects.get(build_url=build_url)
        task_record_instance.report = report_instance
        task_record_instance.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        report_instance = serializer.save()
        return report_instance


class TaskReport(generics.RetrieveDestroyAPIView):
    queryset = models.Report.objects.all()
    serializer_class = TaskReportSerializer
    permission_classes = (IsAdminOrReadOnly,)


@api_view(http_method_names=['POST'])
@permission_classes(permission_classes=(permissions.IsAuthenticated,))
def execute_task(request):
    data = request.data
    job_name = data.get('job_name')
    task_name = data.get('name')
    testcases = data.getlist('testcases')
    test_task = TestTaskModel(job_name=job_name,
                              task_name=task_name,
                              testcases=testcases)
    jenkins = JenkinsController()
    queue_item = jenkins.execute_test_task(test_task)
    task_instance = models.TestTask.objects.get(name=task_name)
    t = Thread(target=record_task_execute,
               args=(jenkins.is_task_executable, queue_item, job_name, task_instance))
    t.start()
    serializer = TestTaskListSerializer(task_instance)
    return Response(serializer.data)


def record_task_execute(func, queue_item, job_name, task_instance):
    while True:
        executable = func(queue_item)
        if executable is False:
            time.sleep(10)
            continue
        else:
            lock.acquire()
            try:
                models.TaskExecuteRecord.objects.get(build_url=executable.get('url'))
            except models.TaskExecuteRecord.DoesNotExist:
                task_record = models.TaskExecuteRecord(job_name=job_name,
                                                       task=task_instance,
                                                       build_id=executable.get('number'),
                                                       build_url=executable.get('url'))
                task_record.save()
                task_instance.execute()

            lock.release()
            break
