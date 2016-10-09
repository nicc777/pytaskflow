# pytaskflow

<b>Table of Contents</b>

* [Example01 Quick Start](#example01-quick-start)
* [Example01 Walk Through](#example01-walk-through)
    * [Step 1 - Implement Functions](#step-1---implement-functions)
        * [The GenerateRandomNumberAndAddToList Function](#the-generaterandomnumberandaddtolist-function)
        * [The DumpResultObj Function](#the-dumpresultobj-function)
        * [Other Functions](#other-functions)
    * [Step 2 - Create a Work Flow](#step-2---create-a-work-flow)
    * [Step 3 - Execute the Work Flow](#step-3---execute-the-work-flow)

This is a simple code-defined task flow engine I built to help me experiment with different web frameworks without having to change the logic of my application.

My first attempt at this had a lot of "framework" logic built in, but I decided to keep it more generic, and now this version is a major rewrite from the original.

Documentation is provided as an example walk through

## Example01 Quick Start

Have a look at the examples directory. If you run the code from `example01/example01.py`, you should get something like the following:

    DUMP: Numbers=[33, 33, 48, 14, 86, 81, 33, 48, 92, 60]
    --- DUMP DONE ---
    DUMP: Stop=True
    DUMP: Total=528
    --- DUMP DONE ---
    RESULT: Total=528

Your numbers will probably be different. 
 
In essence, the work flow goes through 4 steps:

* Step 1 : Generate 10 random integer numbers
* Step 2 : Debug task to dump the 10 numbers
* Step 3 : Calculate the sum total of the numbers
* Step 4 : Print the final result

## Example01 Walk Through

The example has 3 files:

* `example01.py` which is the main script to execute
* `workflow_factory.py` is where the WorkFlow is put together
* `functions.py` is where all our Function implementations are done

### Step 1 - Implement Functions

In `functions.py` there are 4 function:
 
* `GenerateRandomNumberAndAddToList` which generates a list of 10 random numbers
* `DumpResultObj` which we use as a debug or dumping function
* `CalcSumOfListOfNumbers` which calculates the sum total of a list of integers
* `ErrorMessageFunction` which is our generic error handler function

Each of these classes implements `Function` and more specifically has to override the method `execute`. The method takes two optional parameters:

1. `input_result` which is of type `Result` and serves as a object containing all input parameters (mutable)
2. `globals_dict` which is a general `dict` which contains named objects which can be exposed to the executing function (immutable)

When passing input parameters to a function, create a `Result` object and set the parameter `result_obj` with the input parameters (I prefer to keep this a `dict`, but anything will do, as long as your functions can handle it)

#### The `GenerateRandomNumberAndAddToList` Function

Yes, the name is long, but wanted to make it as clear as possible :-)

Now, with that out of the way, this is a rather interesting implementation of Function. as it will loop by adding a copy of the original task as the next task until 10 random numbers are generated.

Here is the function with all the unnecessary lines omitted:

    1:  class GenerateRandomNumberAndAddToList(Function):
    2:      def __init__(self):
    3:          super(GenerateRandomNumberAndAddToList, self).__init__()
    4:      def execute(self, input_result=Result(result_obj={}), globals_dict={}):
    5:          numbers = []
    6:          success_task = None
    7:          if 'Numbers' in input_result.result_obj:
    8:              numbers = input_result.result_obj['Numbers']
    9:          if len(numbers) < 10:
    10:             numbers.append(random.randrange(100))
    11:             if 'GenerateRandomNumberAndAddToListTask' in globals_dict:
    12:                 success_task = globals_dict['GenerateRandomNumberAndAddToListTask']
    13:         self.result = Result(result_obj={'Numbers': numbers}, override_success_task=success_task)

You will notice in <b><i>line 4</i></b> that one of the input parameters is `global_dicts`. When this function get's called, the value of that parameter is set to a copy of the same Task (see `workflow_factory.py` line 19): `globals_dict={'GenerateRandomNumberAndAddToListTask': t1}` 

In <b><i>line 6</i></b> from the above snippet, the `success_task` is set to `None`, meaning that the normal success Task as defined in the `workflow_factory.py` file (line 19 again) will be executed. However, when the list count is below 10 (see <b><i>line 9</i></b> from the above snippet), the `global_dicts` is searched for the key `'GenerateRandomNumberAndAddToListTask'` and if found, the Task defined by it will be set as the next Task to execute through the `override_success_task` parameter when setting the function's `Result`.

Since `'GenerateRandomNumberAndAddToListTask'` points to essentially the same Task, we are now in a loop.

From <b><i>lines 7 to 8</i></b> a new random number is generated and appended to the list, which is set in the `Result` on <b><i>line 13</i></b>. The result will be the input for whatever next `Task` executes.

#### The `DumpResultObj` Function

This function mainly just dumps the content of the `Result` object's `result_obj` (assuming's it's a dict) to STDOUT.

It will also look for the `'Stop'` key, expecting it to be a boolean. Using this trick, the `Task` that get's this function assigned can be called multiple times by other tasks, and only if this one key is set to `True` will the function force a stop.

#### Other Functions

The other functions are relatively straight forward. They take a `Result` as input (via the `input_result` parameter) as well as the optional `golbals_dict` which should not be set in this example for the remainder of the functions.

### Step 2 - Create a Work Flow

This example doesn't show a very complex factory implementation, but rather just two python functions:

* `get_error_task` which is used to create a error handling `Task`; and
* `get_workflow` which returns a `WorkFlow` instance containing the first `Task` to execute.

### Step 3 - Execute the Work Flow

The main script is very simple:

    1: if __name__ == '__main__':
    2:     workflow = get_workflow()
    3:     result = workflow.run_workflow()
    4:     for k, v in result.result_obj.items():
    5:         print('RESULT: {}={}'.format(k, v))

In <b><i>line 2</i></b> an instance of a `WorkFlow` is obtained from the factory (see the previous step). Then, in <b><i>line 3</i></b> the work flow is executed and the final `Result` stored in `result`.

<b><i>lines 4 and 5</i></b> simply loops through the `result_obj` which is assumed to be a `dict` and the key value pairs are printed to STDOUT.


# Credits

* [github-markdown-toc](https://github.com/ekalinin/github-markdown-toc) by Eugene Kalinin used to create the markdown TOC