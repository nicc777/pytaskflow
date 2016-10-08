import unittest
from pytaskflow.taskflow_engine import Function, Result, Task, WorkFlow

# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package


#def test_success():
#    assert True


class PrintFunction(Function):
    def __init__(self):
        super(PrintFunction, self).__init__()

    def execute(self, input_result=Result(result_obj={})):
        ro = input_result.result_obj
        ro['Message'] = 'Hello World'
        self.result = Result(result_obj=ro, is_error=False)


class SetVariableFunction(Function):
    def __init__(self):
        super(SetVariableFunction, self).__init__()

    def execute(self, input_result=Result(result_obj={})):
        ro = input_result.result_obj
        ro['Variable'] = 10
        self.result = Result(result_obj=ro, is_error=False)


class FunctionTests(unittest.TestCase):
    def test_define_function_positive001(self):
        f = PrintFunction()
        f.execute()
        self.assertEqual(f.result.result_obj['Message'], 'Hello World')


class TaskTests(unittest.TestCase):
    def test_basic_task_positive001(self):
        f1 = PrintFunction()
        f2 = SetVariableFunction()
        t1 = Task(task_name='Task 1')
        t2 = Task(task_name='Task 2')
        t2.register_function(function=f1, success_task=None, err_task=None)
        t1.register_function(function=f2, success_task=t2, err_task=None)
        t1.run_task(input_result=Result(result_obj={}))
        self.assertEqual(t1.task_result.result_obj['Message'], 'Hello World')
        self.assertEqual(t1.task_result.result_obj['Variable'], 10)


class WorkFlowTests(unittest.TestCase):
    def test_basic_workflow_positive001(self):
        f1 = PrintFunction()
        f2 = SetVariableFunction()
        t1 = Task(task_name='Task 1')
        t2 = Task(task_name='Task 2')
        t2.register_function(function=f1, success_task=None, err_task=None)
        t1.register_function(function=f2, success_task=t2, err_task=None)
        wf = WorkFlow(workflow_name='Workflow Test', starter_task=t1)
        result = wf.run_workflow(input_result=Result(result_obj={}))
        self.assertEqual(result.result_obj['Message'], 'Hello World')
        self.assertEqual(result.result_obj['Variable'], 10)


if __name__ == '__main__':
    unittest.main()

# EOF
