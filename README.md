# pytaskflow

<b>Table of Contents</b>

* [Basic Operation and Logic](#basic-operation-and-logic)
    * [Step 1 - Framework Entry point](#step-1---framework-entry-point)
    * [Step 2 - Creating an EntryPoint](#step-2---creating-an-entrypoint)
    * [Step 3 - Starting the Workflow](#step-3---starting-the-workflow)
    * [Step 4 - Framework result processing](#step-4---framework-result-processing)
* [Creating a WorkFlow](#creating-a-workflow)
    * [Step 1 - Create Function's (Task's)](#step-1---create-functions-tasks)
    * [Step 2 - Create a TaskCollection](#step-2---create-a-taskcollection)
    * [Step 3 - Define a WorkFlow](#step-3---define-a-workflow)

I like to play and experiment a lot and that means re-implementing very similar applications (or exavctly the same application) in multiple frameworks (think Django and Flask for web frameworks).

For this reason I have come up with a simple (IMHO) Python library that allow me to define my application logic as a series of tasks that can be executed with some logic that minimizes the effort when swithching the same application between frameworks.

I hope this might be of some benefot to someone else as well.

Updates to this document and others to follow...

## Basic Operation and Logic

The following diagram explains the basic flow through the Workflow engine, assuming your tasks have all been defined (more about this later):

![Diagram 1](https://github.com/nicc777/pytaskflow/blob/master/docs/diagram_01.png)

Step by step walk through is shown below and highlights examples from the `example` directory.

### Step 1 - Framework Entry point
 
If you use a framework (Flask or Django, for example), you will typically map a path to a function.

A typical Flask enpoint could be defined as follow:

    from flask import Flask
    from flask import request, render_template, redirect, make_response
       .
       .
    @app.route('/')
    def home():
        # Render the home page...
            .
            .

Note the second import line: these are the objects we will also pass to the Workflow system via the EntryPoint class.

### Step 2 - Creating an EntryPoint

The EntryPoint provides a consistant reference for the framework which is platform neutral, but at the same time include enough of the framework objects to assist with framework specific functions.

Furthermore, the Entry{Point provides a number of configuration items based on the web request which is framework neutral, for example cookies and the request path.

The framework function may now change to something like the following:

    @app.route('/')
    def home():
        workflow = render_template("xxxxxxx.html", ........)
        other_objects = {
            'redirect': redirect,
            'make_response': make_response
        }
        entry_point = web_framework_factory.flask_entry_point_creator(request_obj=request, response_obj=render_template, other_objs=other_objects)
    
The EntryPoint could have been created manually within the function, but I have created a factory method implementation to create an EntryPoint based on the Flask framework.

The `flask_entry_point_creator` code looks like this (it may change in the examples, but the general idea remains the same):

    def flask_entry_point_creator(request_obj, response_obj, other_objs={}, other_instructions={'WebFramework': 'flask', }):
        try:
            _flask = __import__('flask', globals(), locals(), ['request'], 0)
            if not (inspect.ismodule(_flask) and _flask.__name__ == 'flask'):
                warnings.warn("It doesn't appear that flask is installed, so this function will not be able to construct an EntryPoint")
            else:
                entry_point = EntryPoint(
                    request_path=request_obj.path,
                    request_method=request_obj.method,
                    query_string=request_obj.args,
                    post_data=request_obj.form,
                    cookies=request_obj.cookies,
                    default_template='home',
                    log_handler=LoggingHandler(),
                    framework_request_obj=request_obj,
                    framework_response_obj=response_obj,
                    additional_framework_objects=other_objs,
                    other_instructions=other_instructions,
                )
                return entry_point
        except:
            warnings.warn("It appears flask is not installed. Your app will now probably break...")
        return EntryPoint()

As you can see, there are some basic checks to ensure we are working with the Flask framework. Typically I would create similar factory functions for each web framework.

### Step 3 - Starting the Workflow

Once the entry point is created, the Workflow engine can be kicked into action. A Workflow performs various Task's and should produce a output that is framework friendly.

Returning to the Flask example:

    @app.route('/')
    def home():
           .
           .
        # Run our WorkFlow
        if isinstance(entry_point, EntryPoint):
            workflow = application_workflows.flask_sample_app_workflow(entry_point)
        else:
            warnings.warn("entry_point expected to be EntryPoint but is %s" % type(entry_point))
        return workflow
        
The `flask_sample_app_workflow` contains some logic to deal with the Flask specifics during the execution of the Workflow.

In the `flask_sample_app_workflow` there is a line of code that may look something like this:

    def flask_sample_app_workflow(entry_point):
           .
           .
        app_workflow = WorkFlow("GetSessionFunction", sample_application_task_collection(), entry_point=entry_point)
        result = app_workflow.result
        if isinstance(result, Result):
           .
           .

The WorkFlow constructor takes the following arguments:

* start_task_name: str containing the Task.task_name of the first Task to execute
* task_collection: TaskCollection
* entry_point: EntryPoint

From the example, you will see the TaskCollection is obtained by calling `sample_application_task_collection()` which has the following code:

    from .visit_counter_function import VisitCounterFunction
    from .session_persistence_functions import SaveSessionFunction, GetSessionFunction
    from .template_functions import ServeHomeTemplateFunction
    from pytaskflow.taskflow_engine import *

    visit_counter_task = Task("VisitCounterFunction", VisitCounterFunction())
    get_session_task = Task("GetSessionFunction", GetSessionFunction())
    save_session_task = Task("SaveSessionFunction", SaveSessionFunction())
    serve_home_template_task = Task("ServeHomeTemplateFunction", ServeHomeTemplateFunction())
    
    
    def sample_application_task_collection():
        collection = TaskCollection("HelloWorldApp")
        collection.add_task(get_session_task, "VisitCounterFunction", "ServeHomeTemplateFunction")
        collection.add_task(visit_counter_task, "SaveSessionFunction", "ServeHomeTemplateFunction")
        collection.add_task(save_session_task, "ServeHomeTemplateFunction", "ServeHomeTemplateFunction")
        collection.add_task(serve_home_template_task, None, None)
        return collection

Each task has a name and an implementation of a Task class. The WorkFlow is also provided the name of the starting Task.

In addition, the EntryPoint object is available to each Task to assist in the execution. The EntryPoint is immutable. Your Task implementation must pass variables and other objects through the Result object.

### Step 4 - Framework result processing

Looking at the final part of the example as shown in the previous step, the Flask function "returns" the Workflow result, which is actually a Flask specific function.

The `flask_sample_app_workflow` functions build the final result in these lines:

    def flask_sample_app_workflow(entry_point):
           .
           .
        response = entry_point.framework_response_obj(template_name, .......)
        return response

The `entry_point.framework_response_obj` obtains a copy of the Flask object (`render_template` in this case) which is returned to the main Flask function, which in turn build the response to the request.

Therefore, the example code showing `return workflow` is actually another way of writing this code:
 
    from flask import request, render_template, redirect, make_response
     
    @app.route('/')
    def home():
           .
           .
    return render_template(template_name, .......)

And that is it in a nutshell.

## Creating a WorkFlow

TThe following diagram explains the steps to construct a Workflow for processing and will be explained in more detail below:

![Diagram 2](https://github.com/nicc777/pytaskflow/blob/master/docs/diagram_02.png)

### Step 1 - Create Function's (Task's)

To create a task Function, you need to implement the Function class as shown in this example:

    from pytaskflow.taskflow_engine import *


    class ServeHomeTemplateFunction(Function):
        def __init__(self):
            super(ServeHomeTemplateFunction, self).__init__()

        def result(self, entry_point=EntryPoint(), previous_result=None):
            counter_value = 0
            result_obj = {}
            proceed = True
            if isinstance(previous_result, Result):
                if previous_result.is_error is False:
                    .
                    .
               else:
                    proceed = False
                .
                .
            result_obj['Proceed'] = proceed
            result_obj['TemplateName'] = 'base.html'
            result_obj['Action'] = 'ServeTemplate'
            result = Result(result_obj)
            return result

When a Workflow executes, a Function is called by calling it's `result` method with the EntryPoint and a previous Result as input arguments.

The method must return a Result object. The above implementation will always serve the home page template (via the parameters set in the Result object).

<b>TIP</b>: Think about a Function as a [microservice](http://martinfowler.com/articles/microservices.html)

### Step 2 - Create a TaskCollection

A TaskCollection is a series of Task objects that need to work together to perform a certain function.

An example can be seen in `aaplication_tasks.py`:

    from .visit_counter_function import VisitCounterFunction
    from .session_persistence_functions import SaveSessionFunction, GetSessionFunction
    from .template_functions import ServeHomeTemplateFunction
    from pytaskflow.taskflow_engine import *
    
    visit_counter_task = Task("VisitCounterFunction", VisitCounterFunction())
    get_session_task = Task("GetSessionFunction", GetSessionFunction())
    save_session_task = Task("SaveSessionFunction", SaveSessionFunction())
    serve_home_template_task = Task("ServeHomeTemplateFunction", ServeHomeTemplateFunction())
    
    
    def sample_application_task_collection():
        collection = TaskCollection("HelloWorldApp")
        collection.add_task(get_session_task, "VisitCounterFunction", "ServeHomeTemplateFunction")
        collection.add_task(visit_counter_task, "SaveSessionFunction", "ServeHomeTemplateFunction")
        collection.add_task(save_session_task, "ServeHomeTemplateFunction", "ServeHomeTemplateFunction")
        collection.add_task(serve_home_template_task, None, None)
        return collection

The first 3 lines import all our implemented Functions. After the imports, we define all our Task's.

Finally a TaskCollection is defined that contains all teh Task's as well as the name of the first Task that should execute.

When adding a Task to the TaskCollection, the following parameters are supplied:

* The Task implementation
* The Task name of the next Task to execute on success (no error) of the current Task
* The Task name of the Task to execute when an error condition is raised (Result is set in an error state)

### Step 3 - Define a WorkFlow

Finally, the TaskCollection is combined with an EntryPoint to create a Workflow. This is done in the examples in the `application_workflows.py` file by calling the `flask_sample_app_workflow` function.

    def flask_sample_app_workflow(entry_point):
           .
           .
        if isinstance(entry_point, EntryPoint):
            app_workflow = WorkFlow("GetSessionFunction", sample_application_task_collection(), entry_point=entry_point)
            result = app_workflow.result

The final `result` is actually a Result object. From here the function now calls the appropriate web framework object (Flask's `render_template`) before returning.
