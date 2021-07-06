#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/6

class TestTask:

    def __init__(self, job_name, task_name, testcases):
        '''
        :param job_name: corresponding jenkins job name
        :param task_name: task name
        :param testcases: iterable, test cases collection
        '''
        self._job_name = job_name
        self._task_name = task_name
        self._testcases = list(testcases)

    @property
    def job_name(self):
        return self._job_name

    @property
    def task_name(self):
        return self._task_name

    @property
    def testcases(self):
        testcases_str = ' '.join(self._testcases)
        return {'testcases': testcases_str}