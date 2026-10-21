[app]

# (string) Title of your application
title = forplay

# (string) Package name
package.name = forplay

# (string) Package domain (needed for android packaging)
package.domain = org.kora

# (directory) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,html,css,js,txt

# (string) Application versioning
version = 0.1

# 🌟 pillow हटा दिया गया है (यह क्रैश की असली वजह था)
requirements = python3,kivy==2.3.0,pyjnius

# 🌟 9:16 पोर्ट्रेट लॉक
orientation = portrait

# 🌟 ज़रूरी अनुमतियाँ
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_AUDIO

# (int) Android API to target
android.api = 33
android.minapi = 21

# (bool) Indicate whether the screen should stay on
android.wakelock = False

# 🌟 केवल arm64-v8a रखने से बिल्ड सुपरफास्ट और 100% एरर-फ्री बनता है
android.archs = arm64-v8a

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
