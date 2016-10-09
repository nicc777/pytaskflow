from .functions import *
from pytaskflow.taskflow_engine import WorkFlow, Task, Function, Result


def get_error_task():
    t_err = Task(task_name='Error Task')
    t_err.register_function(function=ErrorMessageFunction(), success_task=None, err_task=None)
    return t_err


def get_workflow():
    t1 = Task(task_name='Task 1: Generated List of Numbers')
    t1.register_function(function=GenerateRandomNumberAndAddToList(), success_task=None, err_task=get_error_task())
    t1.success_task = t1
    return WorkFlow(workflow_name='Example Workflow', starter_task=t1)


# EOF