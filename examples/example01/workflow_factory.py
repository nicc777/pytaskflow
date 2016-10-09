from .functions import *
from pytaskflow.taskflow_engine import WorkFlow, Task


def get_error_task():
    t_err = Task(task_name='Error Task')
    t_err.register_function(function=ErrorMessageFunction(), success_task=None, err_task=None)
    return t_err


def get_workflow():
    t4 = Task(task_name='Task 3: Dump All Variables')
    t4.register_function(function=DumpResultObj(), success_task=None, err_task=None)
    t3 = Task(task_name='Task 2: Calculate Sum Total of a List of Numbers')
    t3.register_function(function=CalcSumOfListOfNumbers(), success_task=t4, err_task=get_error_task())
    t2 = Task(task_name='Task Debug:')
    t2.register_function(function=DumpResultObj(), success_task=t3, err_task=get_error_task())
    t1 = Task(task_name='Task 1: Generated List of Numbers')
    t1.register_function(function=GenerateRandomNumberAndAddToList(), success_task=t2, err_task=get_error_task(), globals_dict={'GenerateRandomNumberAndAddToListTask': t1})
    return WorkFlow(workflow_name='Example Workflow', starter_task=t1)


# EOF