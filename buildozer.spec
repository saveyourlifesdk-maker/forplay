[app]
title = forplay
package.name = forplay
package.domain = org.kora
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,html,css,js,txt
version = 0.1
requirements = python3,kivy==2.3.0,pyjnius
orientation = portrait
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_AUDIO
android.api = 33
android.minapi = 21
android.wakelock = False
android.archs = arm64-v8a
android.copy_libs = 1
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
