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


class FunkyLooperFunction(Function):
    def __init__(self):
        super(FunkyLooperFunction, self).__init__()

    def execute(self, input_result=Result(result_obj={})):
        """
        Required in the input_result is the following keys in the result_obj:
            'Numbers': [num1, num2, ..., numX]
        If 3 or more elements are in the list:
            Add num1 and num2 and set as total. Create a NEW list with num1=total and then add the remainder of the list from num3 to numX
        else:
            Add num1 and num2 and set the 'Total' and set the stop indicator to True
        :param input_result: Result
        :return: Result with a new value of 'Total' set.
        """
        ro = input_result.result_obj
        res = Result(result_obj={'Total': 0}, stop=True)    # Set a save stop
        if 'Numbers' in ro:
            nums = ro['Numbers']
            if isinstance(nums, list):
                if len(nums) > 2:
                    n1 = nums.pop(0)
                    n2 = nums.pop(0)
                    if isinstance(n1, int) and isinstance(n2, int):
                        nums.append(n1+n2)
                        res = Result(result_obj={'Numbers': nums}, stop=False)
                else:
                    total = 0
                    for num in ro['Numbers']:
                        if isinstance(num, int):
                            total += num
                    res = Result(result_obj={'Total': total}, stop=True)
        self.result = res


class DumpResultObj(Function):
    def __init__(self):
        super(DumpResultObj, self).__init__()

    def execute(self, input_result=Result(result_obj={})):
        if isinstance(input_result.result_obj, dict):
            for k,v in input_result.result_obj.items():
                print('DUMP: {}={}'.format(k, v))
        print('--- DUMP DONE ---')
        stop = False
        if 'Stop' in input_result.result_obj:
            if isinstance(input_result.result_obj['Stop'], bool):
                stop = input_result.result_obj['Stop']
                del input_result.result_obj['Stop']
        res = input_result.result_obj
        res['Dumped'] = True
        self.result = Result(result_obj=res, stop=stop)


class TaskOverridingSuccessTask(Function):
    def __init__(self):
        super(TaskOverridingSuccessTask, self).__init__()

    def execute(self, input_result=Result(result_obj={})):
        f = DumpResultObj()
        t = Task(task_name='Dumper Task')
        t.register_function(function=f, success_task=None, err_task=None)
        self.result = Result(result_obj={'Stop': True, 'Message': 'Dumping stuff and stopping the bus'}, override_success_task=t)


class FunctionTests(unittest.TestCase):
    def test_define_function_positive001(self):
        f = PrintFunction()
        f.execute()
        self.assertEqual(f.result.result_obj['Message'], 'Hello World')

    def test_funky_looper_function_positive001(self):
        f = FunkyLooperFunction()
        f.execute(input_result=Result(result_obj={'Numbers': [1, 2, 3]}))
        self.assertEqual(len(f.result.result_obj['Numbers']), 2)
        self.assertEqual(f.result.stop, False)


class TaskTests(unittest.TestCase):
    def test_basic_task_positive001(self):
        f1 = PrintFunction()
        f2 = SetVariableFunction()
        t1 = Task(task_name='Task 1')
        t2 = Task(task_name='Task 2')
        t1.register_function(function=f1, success_task=t2, err_task=None)
        t2.register_function(function=f2, success_task=None, err_task=None)
        t1.run_task(input_result=Result(result_obj={}))
        self.assertEqual(t1.task_result.result_obj['Message'], 'Hello World')
        self.assertEqual(t1.task_result.result_obj['Variable'], 10)

    def test_looping_task_positive001(self):
        f = FunkyLooperFunction()
        t1 = Task(task_name='Task 1')
        t1.register_function(function=f, success_task=t1, err_task=None)
        t1.run_task(input_result=Result(result_obj={'Numbers': [1, 2, 3]}))
        self.assertEqual(t1.task_result.result_obj['Total'], 6)

    def test_task_overriding_positive001(self):
        f = TaskOverridingSuccessTask()
        t = Task(task_name='Task 1')
        t.register_function(function=f, success_task=None, err_task=None)
        t.run_task(input_result=Result(result_obj={}))
        self.assertEqual(t.task_result.result_obj['Message'], 'Dumping stuff and stopping the bus')
        self.assertTrue(t.task_result.result_obj['Dumped'])


class WorkFlowTests(unittest.TestCase):
    def test_basic_workflow_positive001(self):
        f1 = PrintFunction()
        f2 = SetVariableFunction()
        t1 = Task(task_name='Task 1')
        t2 = Task(task_name='Task 2')
        t1.register_function(function=f1, success_task=t2, err_task=None)
        t2.register_function(function=f2, success_task=None, err_task=None)
        wf = WorkFlow(workflow_name='Workflow Test', starter_task=t1)
        result = wf.run_workflow(input_result=Result(result_obj={}))
        self.assertEqual(result.result_obj['Message'], 'Hello World')
        self.assertEqual(result.result_obj['Variable'], 10)


if __name__ == '__main__':
    unittest.main()

# EOF
