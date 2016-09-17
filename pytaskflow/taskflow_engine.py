import pickle, traceback, tempfile, os, warnings, inspect
from pytaskflow.framework_factory import flask_actions


STOP_TASK_REDIRECT_VALUE = 'home'
STOP_TASK_CONFIG = {
    'Redirect': True,
    'RedirectUrl': STOP_TASK_REDIRECT_VALUE,
    'Proceed': False,
}
TEMP_DIR = tempfile.gettempdir()
SUPPORTED_FRAMEWORKS = ('flask', )


class PathToTaskCollection:
    def __init__(self):
        self.path_to_task_collection = {}

    def register_path_processor(self, path, first_task_name, task_collection):
        if path not in self.path_to_task_collection:
            self.path_to_task_collection[path] = (first_task_name, task_collection)

class LoggingHandler:
    """
    Default log class. You can safely override this class with your own implementation.
    """
    def __init__(self, max_level="info"):
        self.maxLevel = max_level

    def log(self, level="info", message=None):
        print("[NOT overridden] [%s] %s" % (level, message))


class EntryPoint:
    """
    The EntryPoint class holds information and data about the HTTP request and normalises certain critical request data
    as well as storing the framework request and response objects for full access as required.

    To make your application truly portable, you can think about the following strategies:

        1) Do not rely on the framework request and response objects (as far as possible)
        2) If you have to rely on framework specific request or response objects, create a framework specific
           implementation that can be obtained through a factory pattern implementation. Now, when you implement your
           Function's you call your factory to get the relevant implementation to handle the request or response object.

    When implementing your solution, in your request handler you should have a global implementation that normalises the
    request data to create an EntryPoint object. In flask, you might do the following:

        from flask import request, Response
        .
        .
        def parse_entry_point(request_in):
            rp = '/'
            rm = 'GET'
            qs = None
            pd = None
            c = None
            if isinstance(request_in, request):
                rp = request_in.path
                rm = request_in.method
                qs = request_in.args
                pd = request_in.form
                c = request_in.cookies
            return EntryPoint(
                    request_path=rp,
                    request_method=rm,
                    query_string=qs,
                    post_data=pd,
                    cookies=c,
                    default_template="home",
                    log_handler=LoggingHandler(),
                    framework_request_obj=request_in,
                    framework_response_obj=Response
                )

        .
        .
        @app.route('/hello')
        def api_hello():
            entry_point = parse_entry_point(request)
            .
            .

    """
    def __init__(self, request_path="/", request_method="GET", query_string=None, post_data=None, cookies=None, default_template="home", log_handler=LoggingHandler(), framework_request_obj=None, framework_response_obj=None, additional_framework_objects=None, other_instructions={'WebFramework': 'flask', }):
        """
        Given the following request:

            GET /home?message=Hello
            Host: www.example.com
            Cookies: SESSIONID=abc123

        :param request_path: str containing the request path, for example '/home'
        :param request_method: str contaiing the request method, for example 'GET'
        :param query_string: dict containing the quey string, for example {'message': 'Hello'}
        :param post_data: dict containing the POST data (not used in this example, but similar to the GET example)
        :param cookies: dict contaiing cookies, for example {'SESSIONID': 'abc123'}
        :param default_template: str containing your default template name (for frameworks using templates), for example 'home'
        :param log_handler: LoggingHandler implementation
        :param framework_request_obj: object containing your framework request object, for example: in Flask, the flask.Request class
        :param framework_response_obj: object containing your framework response object, for example: in Flask, the flask.Response class
        :param additional_framework_objects: dict containing any other initialised opjects that may need to be used by the application
        :param other_instructions: dict containing other instruction you can use in your applications.
        """
        self.request_path = request_path
        self.request_method = request_method
        self.query_string = query_string
        self.post_data = post_data
        if isinstance(cookies, dict):
            self.cookies = cookies
        else:
            self.cookies = {}
        self.default_template = default_template
        self.log_handler = log_handler
        self.framework_request_obj = framework_request_obj
        self.framework_response_obj = framework_response_obj
        self.additional_framework_objects = {}
        if isinstance(additional_framework_objects, dict):
            self.additional_framework_objects = additional_framework_objects
        else:
            warnings.warn("additional_framework_objects must be a dict containing the object name as key and the initialised object as value.")
        if isinstance(other_instructions, dict):
            self.other_instructions = other_instructions
        else:
            self.other_instructions = {'WebFramework': 'flask', }
            warnings.warn("other_instructions was not a dictionary when defining the EntryPoint and therefore the default values will be used.")


class Result:
    """
    This is the standard Result object that must be generated by every Function and that will also be passed as a
    parameter into every other Function that will be executed as part of a WorkFlow
    """
    def __init__(self, result_obj, is_error=False, err_msg=None):
        """
        Initialize the Result
        :param result_obj: dict containing application specific key/value pairs
        :param is_error: bool to indicate if the Result is an error result
        :param err_msg: str containing the error message
        """
        self.result_obj = result_obj
        self.is_error = is_error
        self.err_msg = err_msg
        if self.result_obj is None:
            self.result_obj = {
                'FunctionResult': False,    # Default is ERROR
                'FunctionTemplate': '',     # Default
                'RenderTemplate': False,    # Render the default template
                'Redirect': True,           # Must we redirect?
                'RedirectUrl': '/',         # If we need to redirect, whereto?
            }

    def _get_string(self):
        ds = "\n"
        if isinstance(self.result_obj, dict):
            for key, value in self.result_obj.items():
                ds += "\t\t%s=%s\n" % (key, value)
        str = "DUMP\n----\n\tself.resultObj=%s\n\tself.isError=%s\n\tself.errMsg=%s\n\tself.resultObj DATA:%s" % (type(self.result_obj), self.is_error, self.err_msg, ds)
        return str

    def __str__(self):
        return self._get_string()

    def __repr__(self):
        return self._get_string()


class Function:
    """
    Each Task in a WorkFlow will execute a Function. Applications need to implement their own functions which will be
    added to a Task and a TaskCollection will be added to a WorkFlow
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the Function
        :param args:
        :param kwargs:
        """
        self.args = args
        self.kwargs = kwargs

    def result(self, entry_point=EntryPoint(), previous_result=None):
        """
        Each Function must override this method that generates a Result to return
        :param entry_point: EntryPoint
        :param previous_result: Result (optional) from previous Task executions
        :return: Result
        """
        return Result(None, is_error=True, err_msg="Result method must be overridden by your own implementation")


class SessionPersistence:
    """
    Base class to define the persistence API for the application
    """
    def __init__(self, session_token, session_data=None):
        """
        Initialize the class
        :param session_token: str that contains the session ID or token which must be unique for each client
        :param session_data: object that can be serialized (optional). It is strongly advised to use a Result object
        """
        self.session_token = session_token
        self.session_data = session_data

    def get_session_data(self):
        """
        Retrieve a saved session. Will use the token that was used to initialize the class.
        :return: object that was saved during save_session_data() call
        """
        raise Exception("Your session persistance implementation must override this method.")

    def save_session_data(self):
        """
        Save a session using the session_token and session_data that was set during initialisation
        :return: bool True if successful or False if an error occurred
        """
        raise Exception("Your session persistance implementation must override this method.")


class Task:
    def __init__(self, task_name, task_impl):
        """
        The taskObj contains either a Function. The result method will be called and the result stored in Result class.
        :param task_name: str containing a friendly name for the Task
        :param task_impl: Function implementation
        """
        self.task_impl = task_impl
        self.task_name = task_name
        self.can_run = True
        if not isinstance(self.task_impl, Function):
            self.result = Result(None, is_error=True, err_msg="The taskObj parameter must be either a Decision() or Function() implementation")
            self.can_run = False
        else:
            self.result = Result(None, is_error=True, err_msg="You need to override method runTask() properly")

    def run_task(self, entry_point=EntryPoint(), previous_result=None):
        """
        This method will be called during WorkFlow execution.
        :param entry_point: EntryPoint object
        :param previous_result: Result from previous Task (default = None)
        :return: Result
        """
        result = None
        if isinstance(previous_result, Result):
            result = previous_result
        try:
            if self.can_run:
                self.result = self.task_impl.result(entry_point=entry_point, previous_result=result)
        except:
            self.result = Result(None, is_error=True, err_msg="EXCEPTION: %s" % traceback.format_exc())
            warnings.warn("EXCEPTION: %s" % traceback.format_exc())
        return self.result


class StopTask(Task):
    """
    Task implementation called when a serious error occurred. Forces a pre-defined/configurable default action
    """
    def __init__(self, debug_message=""):
        self.debug_message = debug_message
        super(StopTask, self).__init__("StopperTask", Function())

    def run_task(self, entry_point=EntryPoint(), previous_result=None):
        stop_task_conf = STOP_TASK_CONFIG
        stop_task_conf['DebugMessage'] = self.debug_message
        self.result = Result(stop_task_conf, is_error=False, err_msg=None)


class TaskCollection:
    """
    TaskCollection contains a series of Task objects that defines a WorkFlow
    """
    def __init__(self, collection_name):
        """
        Initialization of the class
        :param collection_name: str with a friendly name for the TaskCollection
        """
        self.collection_name = collection_name
        self.tasks = {}
        self.task_names = []
        self.add_task(StopTask(), None, None)

    def add_task(self, task, success_task_name, err_task_name):
        """
        Add a Task to the collection
        :param task: Task implementation
        :param success_task_name: str with the Task.task_name to call when no errors occur (Result.is_error == False)
        :param err_task_name: str with the Task.task_name to call when an error occured (Result.is_error == True)
        """
        if self._validate(task=task):
            self.tasks[task.task_name] = (task, success_task_name, err_task_name)
            self.task_names.append(task.task_name)

    def get_task(self, task_name):
        """
        Get a Task based on a Task.task_name
        :param task_name: str containing the Task to obtain
        :return: Task (or StopTask which is a Task implementation)
        """
        if task_name in self.task_names:
            for task_name_in, value_tuple in self.tasks.items():
                if task_name_in == task_name:
                    return value_tuple[0]
        return StopTask(
            debug_message="TaskCollection default stop message returned. Redirecting to STOP_TASK_REDIRECT_VALUE entry point. Reason: task_name '%s' was not found in this collection." % task_name)

    def get_next_task_name(self, task_name, get_err_task=False):
        """
        Get the next Task in the task collection to execute.
        :param task_name: str containing the Task.task_name to retrieve
        :param get_err_task: bool (default=False). If set, return the Task defined as error task
        :return: str containing the next Task.task_name to execute
        """
        if task_name in self.task_names:
            for task_name_in, value_tuple in self.tasks.items():
                if task_name_in == task_name:
                    if get_err_task:
                        return value_tuple[2]
                    else:
                        return value_tuple[1]
        return "StopperTask"

    def _validate(self, task):
        """
        Validate that all Task objects are defined (for every named task a task implementation is registered).
        :return: bool True if validation is successful otherwise return False
        """
        # TODO implement...
        final_result = True
        if not isinstance(task.task_impl, Function):
            final_result = False
        return final_result


class WorkFlow:
    """
    Defines a WorkFlow and should be called within a end-point method or class using a TaskCollection as a work flow
    configuration. The final Result will be set in WorkFlow.result
    """
    def __init__(self, start_task_name, task_collection, entry_point=EntryPoint()):
        """
        Initialized the WorkFlow and immediately starts the execution
        :param start_task_name: str containing the Task.task_name of the first Task to execute
        :param task_collection: TaskCollection
        :param entry_point: EntryPoint
        """
        self.result = Result({'Redirect': True, 'RedirectUrl': 'home', 'DebugMessage': "WorkFlow failed (default redirect home)"}, is_error=False, err_msg=None)
        task_name = start_task_name
        task = task_collection.get_task(task_name)
        result = task.run_task(entry_point=entry_point, previous_result=None)
        if isinstance(result, Result):
            if 'Proceed' in result.result_obj:
                run = result.result_obj['Proceed']
                loop_count = 0
                while run:
                    loop_count += 1
                    entry_point.log_handler.log(level="debug", message="WorkFlow loop_count: %s" % loop_count)
                    if loop_count > 1000:    # Apply the breaks at a 1000 loops...
                        entry_point.log_handler.log(level="error", message="WorkFlow looped more then a 1000 times. Forcing an exit.")
                        break
                    next_task = task_collection.get_next_task_name(task_name, result.is_error)
                    entry_point.log_handler.log(level="debug", message="next_task: %s (error: %s)" % (next_task, result.is_error))
                    run = False
                    task = task_collection.get_task(next_task)
                    task_name = next_task
                    result = task.run_task(entry_point=entry_point, previous_result=result)
                    if isinstance(result, Result):
                        if 'Proceed' in result.result_obj:
                            run = result.result_obj['Proceed']
                    else:
                        result = Result({'Redirect': True, 'RedirectUrl': 'home', 'Proceed': False}, is_error=True, err_msg="WorkFlow FAILED!")
        else:
            result = Result(None)
            warnings.warn("Result was not set properly in the initial task and we therefore fallback on the default Result()")
        self.result = result    # Store final result...


class FileBasedSessionPersistence(SessionPersistence):
    """
    A generic file based SessionPersistence implementation
    """
    def __init__(self, session_token, session_data=None):
        """
        Initialise the SessionPersistence object.
        :param session_token: str (see SessionPersistence)
        :param session_data: object (see SessionPersistence)
        """
        self.can_persist = True
        if session_token is None:
            self.can_persist = False
        filename = TEMP_DIR + os.sep + session_token + ".pickle"
        super(FileBasedSessionPersistence, self).__init__(filename, session_data)

    def get_session_data(self):
        try:
            if self.can_persist:
                return pickle.load(open(self.session_token, "rb"))
        except:
            warnings.warn("EXCEPTION: %s" % traceback.format_exc())
        return None

    def save_session_data(self):
        if self.session_data is not None and self.can_persist:
            try:
                pickle.dump(self.session_data, open(self.session_token, "wb"))
                return True
            except:
                warnings.warn("EXCEPTION: %s" % traceback.format_exc())
        return False


class FinalResult:
    """
    The FinalResult class is used to implement the processing of the final Result() that your web framework (like Flask)
    should be able to handle.

    For example, in Flask you could return a template as follow:

        return render_template('show_entries.html', entries=entries) # taken from http://flask.pocoo.org/docs/0.11/tutorial/views/ (2016-08-11)

    Your FinalResult implementation would therefore be called like such (in Flask):

        this_page_entrypoint = EntryPoint(...)
        some_page_workflow = WorkFlow("MyFunction", this_page_task_collection, entryPoint=this_page_entrypoint)
        final_result = MyFinalResultImpl(some_page_workflow.result)
        return final_result.return_value()
    """
    def __init__(self, result=Result(None)):
        """
        Initialize the class

        :param result: Result containing the final result from the WorkFlow() implementation.
        """
        self.result = Result(None)
        if isinstance(result, Result):
            self.result = result

    def return_value(self):
        raise Exception("You must override this method and return something your web framework will know how to interpret.")


class WebFrameworkResult:
    def __init__(self, framework='flask'):
        if framework not in SUPPORTED_FRAMEWORKS:
            raise Exception("Framework not supported")
        self.framework = framework

    def process_result(self, result=Result(None), entry_point=EntryPoint()):
        result_obj = self._get_result_obj(result)
        if self.framework == 'flask':
            if 'WebFramework' in entry_point.other_instructions:
                if entry_point.other_instructions['WebFramework'] == 'flask':
                    if result_obj['Action'] == 'Redirect':
                        return flask_actions(action='Redirect', context=None, template_name=None, redirect_url=result_obj['RedirectURL'], cookies=entry_point.cookies)
                    else:
                        return flask_actions(action='RenderTemplate', context=result_obj, template_name=result_obj['TemplateName'], redirect_url=None, cookies=entry_point.cookies)
        raise Exception("Cannot process web framework result")

    def _get_result_obj(self, result):
        result_obj = {
            'Action': 'Redirect',
            'RedirectURL': '/',
        }
        if isinstance(result, Result):
            result_obj = result.result_obj
            if 'Action' in result_obj:
                if result_obj['Action'] == 'Redirect':
                    if not 'RedirectURL' in result_obj:
                        result_obj['RedirectURL'] = '/'
            if 'TemplateName' in result_obj:
                if not isinstance(result_obj['TemplateName'], str):
                    result_obj['TemplateName'] = 'index.html'
        return result_obj


def run_workflow(path_to_task_collection=PathToTaskCollection(), entry_point=EntryPoint(), framework_processor=WebFrameworkResult(framework='flask')):
        result_obj = {}
        result = Result(None)
        first_task_name = 'NotSupplied'
        task_collection = None
        if isinstance(entry_point, EntryPoint):
            if entry_point.request_path in path_to_task_collection.path_to_task_collection:
                task_collection = path_to_task_collection.path_to_task_collection[entry_point.request_path][1]
                first_task_name = path_to_task_collection.path_to_task_collection[entry_point.request_path][0]
            app_workflow = WorkFlow(first_task_name, task_collection, entry_point=entry_point)
            result = app_workflow.result
            if isinstance(result, Result):
                result_obj = result.result_obj
                if 'Action' in result_obj:
                    if result_obj['Action'] == 'Redirect':
                        if 'RedirectURL' not in result_obj:
                            result_obj['RedirectURL'] = '/'
                else:
                    result_obj = {
                        'Action': 'Redirect',
                        'RedirectURL': '/',
                    }
                if 'TemplateName' in result_obj:
                    result_obj['Action'] = 'ServeTemplate'
                    if not isinstance(result_obj['TemplateName'], str):
                        result_obj['TemplateName'] = 'index.html'
            else:
                warnings.warn("result was expected to be Result() but is %s" % type(result))
                result_obj = {
                    'Action': 'Redirect',
                    'RedirectURL': '/',
                }
        else:
            result_obj = {
                'Action': 'Redirect',
                'RedirectURL': '/',
            }
            entry_point = EntryPoint()
        result.result_obj = result_obj
        return framework_processor.process_result(result=result, entry_point=entry_point)


class WebFrameworkActionsFactory:
    def __init__(self, framework='flask'):
        self.framework = framework
        self.FRAMEWORK_ERR = 0
        try:
            from flask import render_template, make_response, redirect
        except:
            self.FRAMEWORK_ERR = 1
        self.FRAMEWORKS = {
            'flask': self._flask_actions
        }

    def get_action_for_framework(self, framework='flask'):
        if framework in self.FRAMEWORKS:
            return self.FRAMEWORKS['framework']

    def _flask_actions(self, action='RenderTemplate', context=None, template_name='index.html', redirect_url='/', cookies=None, response_objects={}):
        # For flask, response_obj must contain make_response, render_template and redirect ...
        if self.FRAMEWORK_ERR > 0:
            raise Exception("Flask could not be loaded...")
        if not isinstance(cookies, dict):
            cookies = None
        if action == 'RenderTemplate':
            if context is not None:
                response = response_objects['make_response'](response_objects['render_template'](template_name, context=context))
            else:
                response = response_objects['make_response'](response_objects['render_template'](template_name))
        else:
            response = response_objects['make_response'](response_objects['redirect'](redirect_url))
        if cookies is not None:
            for key, value in cookies.items():
                response.set_cookie(key, value)
        return response


class WebFrameworkEndpointFactory:
    def __init__(self, framework='flask'):
        self.framework = framework
        self.FRAMEWORK_ERR = 0
        try:
            from flask import render_template, make_response, redirect
        except:
            self.FRAMEWORK_ERR = 1

    def endpoint_creator(self, request_obj, other_objs={}, other_instructions={}):
        if self.FRAMEWORK_ERR == 0:
            return self._flask_endpoint_creator(request_obj=request_obj, other_objs=other_objs, other_instructions=other_instructions)
        raise Exception("Framework '{s}' not yet supported".format(self.framework))

    def _flask_endpoint_creator(self, request_obj, other_objs={}, other_instructions={}):
        try:
            _flask = __import__('flask', globals(), locals(), ['request'], 0)
            if not (inspect.ismodule(_flask) and _flask.__name__ == 'flask'):
                warnings.warn(
                    "It doesn't appear that flask is installed, so this function will not be able to construct an EntryPoint")
            else:
                other_instructions['WebFramework'] = 'flask'
                entry_point = EntryPoint(
                    request_path=request_obj.path,
                    request_method=request_obj.method,
                    query_string=request_obj.args,
                    post_data=request_obj.form,
                    cookies=request_obj.cookies,
                    default_template='index.html',
                    log_handler=LoggingHandler(),
                    framework_request_obj=request_obj,
                    framework_response_obj=None,
                    additional_framework_objects=other_objs,
                    other_instructions=other_instructions,
                )
                return entry_point
        except:
            warnings.warn("It appears flask is not installed. Your app will now probably break...")
        return EntryPoint()


# EOF
