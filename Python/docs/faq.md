# FAQs
### ModuleNotFoundError
If you see the error `ModuleNotFoundError: No module named '<insert_module_name>'`. Add the following to the top of the file:
```
import os, sys
dir = os.path.dirname(__file__)
if not dir in sys.path:
    sys.path.append(dir)
```