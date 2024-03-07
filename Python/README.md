# Setup guide
To get set up, watch this [video](https://www.youtube.com/watch?v=YUytEtaVrrc). Just in case the video is somehow unreachable, here are the required steps:
* Check the latest release of [fake-bpy-module](https://github.com/nutti/fake-bpy-module) and get that version of blender
* Go to the scripting tab of that version of blender and note the version of python
* Install that version of python, create a venv if you want
* Use `pip install fake-bpy-module==<release-version-here>` to get the correct version of the module
* Download [visual studio code](https://code.visualstudio.com/Download ) if you don't have it.
* Download *python* extension for vscode by microsoft.
* Download *Blender development* extension for vs code by Jacques Lucke
* We need to give write permissions to the python folder where we are installing some extra modules. Navigate to your blender install, probably `C:\Program Files\Blender Foundation\Blender 4.0\4.0\`, right click on python folder and select properties, under the security tab, under `Groups or user names:` on the top half of the window, scroll down until you see Users likely 2nd to last in between Administrators and TrustedInstaller. Select it and click edit. Click on users again and in the bottom half of the screen you can tick the `write` checkbox to allow rights. Save/apply everything and close out
* In vs code use `ctrl+shift+p` to open the command panel and search for `Blender: Start` to open the blender program. If it asks you for the binary location, it's probably installed in `C:\Program Files\Blender Foundation\Blender 4.0\blender.exe`. If it works blender will start and in vs code you should see 'Debug client attached'.
* To run your script hit `ctrl+shift+p` and select `Blender: Run Script`.

Good luck :)