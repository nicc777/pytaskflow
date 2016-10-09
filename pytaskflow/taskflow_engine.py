import pickle, traceback, tempfile, os, warnings, inspect


TEMP_DIR = tempfile.gettempdir()


class LoggingHandler:
    """
    Default log class. You can safely override this class with your own implementation.
    """
    def __init__(self, max_level="info"):
        self.maxLevel = max_level

    def log(self, level="info", message=None):
        print("[NOT overridden] [%s] %s" % (level, message))


class Result:
    """
    This is the standard Result object that must be generated by every Function and that will also be passed as a
    parameter into every other Function that will be executed as part of a WorkFlow
    """
    def __init__(self, result_obj, is_error=False, err_msg=None, stop=False):
        """
        Initialize the Result
        :param result_obj: dict containing application specific key/value pairs
        :param is_error: bool to indicate if the Result is an error result
        :param err_msg: str containing the error message
        :param stop: bool used by Task to determine if the next Task must be called
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
        self.stop = stop

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


class Function:
    """
    Base class for Function implementation. You need to override the execute() method and set self.result
    """
    def __init__(self):
        self.result = Result(result_obj={})

    def execute(self, input_result=Result(result_obj={})):
        """
        Method you need to override.
        :param input_result: Result containing input parameters
        :return: nothing is returned by this method - you need to set self.result
        """
        self.result = Result(result_obj={})
        raise Exception("This must be overriden by your implementation")


class Task:
    """
    A Task contains a function to execute as well as the next Task to move to after the Function is successfully
    executed. You can also set an error Task to execute should the function set the Result as an error.
    """
    def __init__(self, task_name):
        """
        Initializes the task
        :param task_name: str with the Task name
        """
        self.task_name = task_name
        self.function = None
        self.success_task = None
        self.err_task = None
        self.task_result = None

    def register_function(self, function, success_task, err_task):
        """
        Registers a Function with the task together with the Task to execute on success or failure
        :param function: Function implementation
        :param success_task: Task to execute if the function does not set the Result as error
        :param err_task: Task to execute if the function sets the Result as error
        :return: nothing is returned. Instead, self.task_result is set.
        """
        if function is not None:
            if isinstance(function, Function):
                self.function = function
            else:
                raise Exception("function must be of type Function")
        else:
            raise Exception("function must be supplied")

        if success_task is not None:
            if isinstance(success_task, Task):
                self.success_task = success_task
            else:
                raise Exception("success_task must be of type Task")

        if err_task is not None:
            if isinstance(err_task, Task):
                self.err_task = err_task
            else:
                raise Exception("err_task must be of type Task")

    def run_task(self, input_result=Result(result_obj={})):
        """
        Executes the Function and optionally run the Task set on success or failure of the Function
        :param input_result: Result containing the input parameters
        :return: nothing is returned, but rather self.task_result is set
        """
        self.function.execute(input_result=input_result)
        if not isinstance(self.function.result, Result):
            raise Exception("function result was not of type Result!")
        if self.function.result.is_error:
            if self.err_task is not None:
                self.err_task.run_task(input_result=self.function.result)
                if not isinstance(self.err_task.task_result, Result):
                    self.task_result = Result(result_obj={}, is_error=True, err_msg='Task {} produced an error by the error task {} did not set a valid Result'.format(self.task_name, self.err_task.task_name))
                else:
                    self.task_result = self.err_task.task_result
        else:
            if not self.function.result.stop:
                if self.success_task is not None:
                    self.success_task.run_task(input_result=self.function.result)
                    if isinstance(self.success_task.task_result, Result):
                        self.task_result = self.success_task.task_result
                    else:
                        self.task_result = self.function.result
        if self.task_result is None:
            self.task_result = self.function.result


class WorkFlow:
    """
    A WorkFlow simply defines a Task to start work
    """
    def __init__(self, workflow_name, starter_task):
        """
        Initialize the WorkFlow
        :param workflow_name: str with the WorkFlow name
        :param starter_task: Task to start the WorkFlow
        """
        self.workflow_name = workflow_name
        if isinstance(starter_task, Task):
            self.starter_task = starter_task
        else:
            raise Exception("starter_task must be of type Task")

    def run_workflow(self, input_result=Result(result_obj={})):
        """
        Start the WorkFlow by running the starter Task
        :param input_result: Result continaing the input parameters
        :return: Result with the final result of the last executed Task
        """
        self.starter_task.run_task(input_result=input_result)
        return self.starter_task.task_result



# EOF
