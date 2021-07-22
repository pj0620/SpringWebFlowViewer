# SpringWebFlowViewer
Tool written in python used to view flows defined in Spring Webflow files as a Directed Graph. 

## Installing Requirements
```
pip install -r requirements.txt
```

## Testing
```
flow_viewer.py samples\booking-flow.xml
```

Should result in the following.

![Screenshot](Figure_1.png)

## Usage
```
flow-viewer.py <FLOW FILE> 
   -h, --help : display help
   -s, --start_state <START-STATE> : add start state for BFS based search
   -m, --method_vals <METHOD_VALUES> : comma separated list of predefined outputs of methods
   -i, --initialize <VARIABLE VALUES> : comma seperated list of initial variable values. Useful when value of variable cannot be infered from flow file
   -e, --external <EXTERNAL NODES> : comma separated list of external nodes
   -g, --goal_state <GOAL_STATE> : only shows paths which include this state

```
