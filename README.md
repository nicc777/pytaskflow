# pytaskflow

I like to play and experiment a lot and that means re-implementing very similar applications (or exavctly the same application) in multiple frameworks (think Django and Flask for web frameworks).

For this reason I have come up with a simple (IMHO) Python library that allow me to define my application logic as a series of tasks that can be executed with some logic that minimizes the effort when swithching the same application between frameworks.

I hope this might be of some benefot to someone else as well.

Updates to this document and others to follow...

## Basic Operation and Logic

The following diagram explains the basic flow through the Workflow engine, assuming your tasks have all been defined (more about this later):

![Diagram 1](https://github.com/nicc777/pytaskflow/blob/master/docs/diagram_01.png)