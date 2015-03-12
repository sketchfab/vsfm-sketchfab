# vsfm-skfb
Publish a VisualSFM model on Sketchfab

Put the ```vsfm-skfb-master``` package in VisualSFM's ```bin``` directory. For example, if you used https://github.com/luckybulldozer/VisualSFM_OS_X_Installer, it could be ```/Applications/VisualSFM_OS_X_Mavericks_Installer-master/vsfm/bin/vsfm-skfb-master```. On Windows, you can put it in the same directory as VisualSFM.exe.

It includes the python ```requests``` module.

Edit the external tool section of your ```nv.ini``` file. You can add/change arguments when you run the tool, but it's convenient to store the basic command, your API token, and default path to the PLY file, for example:

```
#Some external applications to run from VisualSFM.
#%s will be replaced by the nvm or ply file title.
param_external_tool1 python vsfm-skfb-master -t API_TOKEN "%s.ply"
```

You can get your Sketchfab API token here: https://sketchfab.com/settings/password

For details: http://ccwu.me/vsfm/index.html
