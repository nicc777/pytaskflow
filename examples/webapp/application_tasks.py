from .visit_counter_function import VisitCounterFunction
from .session_persistence_functions import SaveSessionFunction, GetSessionFunction
from pytaskflow.taskflow_engine import *

visit_counter_task = Task("VisitCounterFunction", VisitCounterFunction())
get_session_task = Task("GetSessionFunction", GetSessionFunction())
save_session_task = Task("SaveSessionFunction", SaveSessionFunction())


def sample_application_task_collection():
    collection = TaskCollection("HelloWorldApp")
    collection.add_task(get_session_task, "VisitCounterFunction", "ServeHomeTemplateFunction")
    collection.add_task(visit_counter_task, "SaveSessionFunction", "ServeHomeTemplateFunction")
    collection.add_task(save_session_task, "ServeHomeTemplateFunction", "ServeHomeTemplateFunction")
    return collection


# ./end of file