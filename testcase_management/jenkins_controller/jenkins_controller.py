#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/6

from jenkins import Jenkins

from mobile_QA_web_platform.settings.base import JENKINS_SERVER, JENKINS_PASSWORD, JENKINS_USERNAME
from testcase_management.jenkins_controller.model import TestTask

def singleton(cls):
    _instance = {}
    def inner(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return inner


@singleton
class JenkinsController:

    def __init__(self):
        self._jenkins = Jenkins(url=JENKINS_SERVER,
                                username=JENKINS_USERNAME,
                                password=JENKINS_PASSWORD)

    def execute_test_task(self, test_task: TestTask):
        # check job is exist or not
        job = self._jenkins.job_exists(test_task.job_name)
        if job is None:
            # -1 meaning current jenkins server not exist this job name
            return -1
        else:
            queue_item = self._jenkins.build_job(name=test_task.job_name,
                                                 parameters=test_task.testcases)
            print(queue_item)
            resp = self._jenkins.get_queue_item(queue_item)
            return resp


if __name__ == '__main__':
    a = JenkinsController()
    # testcases = ['testcases/login/login_success_test.py::TestCaseLoginSuccess::test_start',
    #              'testcases/register/register_username_blank_test.py::TestCaseRegisterUserNameBlank::test_start']
    # testcases = TestTask(job_name='server_api_test_control_by_web_platform', task_name='123', testcases=testcases)
    # res = a.execute_test_task(test_task=testcases)
    # print(res)
    res = a._jenkins.get_queue_item(171)
    print(res)