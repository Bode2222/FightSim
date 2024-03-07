# One click build
Create a dependency graph for all the files i have, then create a task that does the following:
* When I run the task on a specific file, find the file in the dependency graph
* Do bread first search starting from leafs, running each script, only continue if server returns 200
* When I run final script without issue, return 200.
## Instructions
* Create a dependency graph in dot language using command `pydeps . --include-missing` in Python directory
* Run build.py to get the order the files should be built in. Requires `Python.svg` to be in the same directory (i.e. the Python director)
* Run vscode extension with file order to run your program.