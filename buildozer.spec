[app]

# (string) Title of your application
title = forplay

# (string) Package name
package.name = forplay

# (string) Package domain (needed for android packaging)
package.domain = org.kora

# (directory) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,html,css,js,txt

# (string) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.3.0,pyjnius,pillow

# 🌟 9:16 रेश्यो लॉक (ऐप खुलते ही वर्टिकल रहेगा)
orientation = portrait

# 🌟 ज़रूरी अनुमतियाँ (लोकल सर्वर और गैलरी के लिए)
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_AUDIO

# (int) Android API to target
android.api = 33
android.minapi = 21

# (bool) Indicate whether the screen should stay on
android.wakelock = False

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
