# -*- coding: utf-8 -*-
"""
KORA AI ENGINE - LIVE IN-BROWSER COLOR ADJUSTMENT & TUNING SUITE
UPDATED: ISOLATED CARD-SPECIFIC CHAPTERS (1-20), WEB READER ZOOMING CONTROLS,
2 AVATAR CARDS, 3 SCENE/BG CARDS, AND UNFLATTENED UI
"""

import os
import sys
import io
import time
import json
import shutil
import base64
import random
import threading
import traceback
import urllib.request
import urllib.error
import urllib.parse
import ssl
import re
import webbrowser
import http.server
import socketserver

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty
from kivy.core.audio import SoundLoader

Window.clearcolor = (0.015, 0.02, 0.027, 1)
Window.softinput_mode = 'below_target'

# ================================================================
# ANDROID 9:16 PORTRAIT ORIENTATION FIX
# ================================================================
if platform == 'android':
    try:
        from jnius import autoclass
        ActivityInfo = autoclass('android.content.pm.ActivityInfo')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        PythonActivity.mActivity.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT)
    except Exception as e:
        print(f"Orientation fix error: {e}")

# ==============================================================================
# CLASS LOADER FIX (SDL THREAD CRASH FIX FOR ANDROID)
# ==============================================================================
if platform == 'android':
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Thread = autoclass('java.lang.Thread')
        Thread.currentThread().setContextClassLoader(PythonActivity.mActivity.getClassLoader())
    except Exception as e:
        print(f"Thread fix error: {e}")

KV = '''
<GalleryImageButton@ButtonBehavior+FloatLayout>:
    on_release: app.open_media_selector('character_image', is_video=False)

<GalleryImageBButton@ButtonBehavior+FloatLayout>:
    on_release: app.open_media_selector('character_image_b', is_video=False)

<SceneImage1Button@ButtonBehavior+FloatLayout>:
    on_release: app.open_media_selector('scene_image_1', is_video=False)

<SceneImage2Button@ButtonBehavior+FloatLayout>:
    on_release: app.open_media_selector('scene_image_2', is_video=False)

<BgImageButton@ButtonBehavior+FloatLayout>:
    on_release: app.open_media_selector('scene_bg_image', is_video=False)

<CharacterCardWidget@BoxLayout>:
    orientation: 'vertical'
    size_hint: (None, None)
    width: dp(310)   
    height: dp(585)  
    spacing: dp(10)
    pos_hint: {'center_x': 0.5}

    BoxLayout:
        orientation: 'vertical'
        size_hint: (None, None)
        width: dp(310)
        height: dp(530)
        padding: dp(12)
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: (0.04, 0.05, 0.07, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(12)]
            Color:
                rgba: (0.0, 0.88, 1.0, 0.8)
            Line:
                rounded_rectangle: (self.x, self.y, self.width, self.height, dp(12))
                width: dp(1.5)

        Label:
            text: "[b][color=00e5ff]CHARACTER " + root.card_id_str + "[/color][/b]"
            markup: True
            font_size: '15sp'
            size_hint_y: None
            height: dp(25)
            halign: 'center'

        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'center'
            size_hint: (1, 1)

            StencilView:
                size_hint: (1, 1)
                canvas.before:
                    Color:
                        rgba: (0.1, 0.12, 0.16, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(8)]
                    Color:
                        rgba: (0.0, 0.88, 1.0, 0.6)
                    Line:
                        rounded_rectangle: (self.x, self.y, self.width, self.height, dp(8))
                        width: dp(1.2)

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: (1, 1)
                    pos: self.parent.pos
                    size: self.parent.size
                    spacing: dp(2)

                    AsyncImage:
                        source: root.img_path
                        opacity: 1 if root.img_path else 0
                        allow_stretch: True
                        keep_ratio: False
                        mipmap: True

                    AsyncImage:
                        source: root.img_path_b
                        opacity: 1 if root.img_path_b else 0
                        size_hint_x: 1 if root.img_path_b else 0
                        allow_stretch: True
                        keep_ratio: False
                        mipmap: True

                Label:
                    text: "No Image Selected" if not root.img_path and not root.img_path_b else ""
                    font_size: '11sp'
                    color: (0.5, 0.55, 0.65, 1)
                    halign: 'center'
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}

        BoxLayout:
            orientation: 'horizontal'
            size_hint: (1, None)
            height: dp(40)
            spacing: dp(8)

            BoxLayout:
                orientation: 'vertical'
                size_hint: (1, 1)
                padding: dp(4)
                canvas.before:
                    Color:
                        rgba: (0.08, 0.10, 0.14, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(6)]
                Label:
                    text: "[color=88a0b0]Name:[/color] " + (root.char_name if root.char_name else "---")
                    markup: True
                    font_size: '10sp'
                    halign: 'center'
                    text_size: self.size

            BoxLayout:
                orientation: 'vertical'
                size_hint: (1, 1)
                padding: dp(4)
                canvas.before:
                    Color:
                        rgba: (0.08, 0.10, 0.14, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(6)]
                Label:
                    text: "[color=88a0b0]Role:[/color] " + (root.char_roll if root.char_roll else "---")
                    markup: True
                    font_size: '10sp'
                    halign: 'center'
                    text_size: self.size

    BoxLayout:
        orientation: 'horizontal'
        size_hint: (1, None)
        height: dp(45)
        spacing: dp(10)

        Button:
            text: "EDIT"
            bold: True
            font_size: '14sp'
            background_normal: ''
            background_color: (0.12, 0.48, 0.88, 1)
            color: (1, 1, 1, 1)
            on_release: app.switch_to_edit_screen_for(root.card_index)

        Button:
            text: "PLAY"
            bold: True
            font_size: '14sp'
            background_normal: ''
            background_color: (0.0, 0.85, 0.45, 1)
            color: (1, 1, 1, 1)
            on_release: app.switch_to_chat_screen(card_index=root.card_index)

ScreenManager:
    id: sm

    # 1. मेन होम स्क्रीन
    Screen:
        name: 'home_screen'
        FloatLayout:
            padding: dp(15)

            BoxLayout:
                orientation: 'vertical'
                size_hint: (1, 1)
                padding: [dp(15), dp(55), dp(15), dp(15)]
                spacing: dp(15)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                BoxLayout:
                    orientation: 'vertical'
                    size_hint: (1, 1)
                    padding: dp(12)
                    canvas.before:
                        Color:
                            rgba: (0.04, 0.05, 0.07, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12)]
                        Color:
                            rgba: (0.0, 0.88, 1.0, 0.8)
                        Line:
                            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(12))
                            width: dp(1.5)

                    FloatLayout:
                        Label:
                            text: "[b][color=ffffff]Comic[/color] [color=00e5ff]Ground[/color][/b]"
                            markup: True
                            font_size: '22sp'
                            halign: 'center'
                            valign: 'middle'
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                Button:
                    text: "CHOOSE CHARACTER"
                    size_hint: (1, None)
                    height: dp(50)
                    bold: True
                    font_size: '15sp'
                    background_normal: ''
                    background_color: (0.0, 0.9, 0.46, 1)
                    color: (0, 0, 0, 1)
                    on_release: app.switch_to_character_screen()

            Button:
                text: "⚙ Setting"
                size_hint: (None, None)
                width: dp(85)
                height: dp(35)
                font_size: '12sp'
                bold: True
                background_normal: ''
                background_color: (0.12, 0.48, 0.88, 1)
                color: (1, 1, 1, 1)
                pos_hint: {'right': 0.98, 'top': 0.98}
                on_release: app.open_setting_popup()

    # 2. करैक्टर स्क्रीन (40 कार्ड्स)
    Screen:
        name: 'character_screen'
        FloatLayout:
            ScrollView:
                id: character_scroll_view
                size_hint: (1, 1)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                do_scroll_x: False

                GridLayout:
                    id: character_cards_grid
                    cols: 1
                    spacing: dp(20)
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(10), dp(60), dp(10), dp(40)]

                    CharacterCardWidget:
                        card_index: 1
                        card_id_str: "1"
                        char_name: app.card_names[1]
                        char_roll: app.card_rolls[1]
                        img_path: app.card_imgs[1]
                        img_path_b: app.card_imgs_b[1]
                    CharacterCardWidget:
                        card_index: 2
                        card_id_str: "2"
                        char_name: app.card_names[2]
                        char_roll: app.card_rolls[2]
                        img_path: app.card_imgs[2]
                        img_path_b: app.card_imgs_b[2]
                    CharacterCardWidget:
                        card_index: 3
                        card_id_str: "3"
                        char_name: app.card_names[3]
                        char_roll: app.card_rolls[3]
                        img_path: app.card_imgs[3]
                        img_path_b: app.card_imgs_b[3]
                    CharacterCardWidget:
                        card_index: 4
                        card_id_str: "4"
                        char_name: app.card_names[4]
                        char_roll: app.card_rolls[4]
                        img_path: app.card_imgs[4]
                        img_path_b: app.card_imgs_b[4]
                    CharacterCardWidget:
                        card_index: 5
                        card_id_str: "5"
                        char_name: app.card_names[5]
                        char_roll: app.card_rolls[5]
                        img_path: app.card_imgs[5]
                        img_path_b: app.card_imgs_b[5]
                    CharacterCardWidget:
                        card_index: 6
                        card_id_str: "6"
                        char_name: app.card_names[6]
                        char_roll: app.card_rolls[6]
                        img_path: app.card_imgs[6]
                        img_path_b: app.card_imgs_b[6]
                    CharacterCardWidget:
                        card_index: 7
                        card_id_str: "7"
                        char_name: app.card_names[7]
                        char_roll: app.card_rolls[7]
                        img_path: app.card_imgs[7]
                        img_path_b: app.card_imgs_b[7]
                    CharacterCardWidget:
                        card_index: 8
                        card_id_str: "8"
                        char_name: app.card_names[8]
                        char_roll: app.card_rolls[8]
                        img_path: app.card_imgs[8]
                        img_path_b: app.card_imgs_b[8]
                    CharacterCardWidget:
                        card_index: 9
                        card_id_str: "9"
                        char_name: app.card_names[9]
                        char_roll: app.card_rolls[9]
                        img_path: app.card_imgs[9]
                        img_path_b: app.card_imgs_b[9]
                    CharacterCardWidget:
                        card_index: 10
                        card_id_str: "10"
                        char_name: app.card_names[10]
                        char_roll: app.card_rolls[10]
                        img_path: app.card_imgs[10]
                        img_path_b: app.card_imgs_b[10]
                    CharacterCardWidget:
                        card_index: 11
                        card_id_str: "11"
                        char_name: app.card_names[11]
                        char_roll: app.card_rolls[11]
                        img_path: app.card_imgs[11]
                        img_path_b: app.card_imgs_b[11]
                    CharacterCardWidget:
                        card_index: 12
                        card_id_str: "12"
                        char_name: app.card_names[12]
                        char_roll: app.card_rolls[12]
                        img_path: app.card_imgs[12]
                        img_path_b: app.card_imgs_b[12]
                    CharacterCardWidget:
                        card_index: 13
                        card_id_str: "13"
                        char_name: app.card_names[13]
                        char_roll: app.card_rolls[13]
                        img_path: app.card_imgs[13]
                        img_path_b: app.card_imgs_b[13]
                    CharacterCardWidget:
                        card_index: 14
                        card_id_str: "14"
                        char_name: app.card_names[14]
                        char_roll: app.card_rolls[14]
                        img_path: app.card_imgs[14]
                        img_path_b: app.card_imgs_b[14]
                    CharacterCardWidget:
                        card_index: 15
                        card_id_str: "15"
                        char_name: app.card_names[15]
                        char_roll: app.card_rolls[15]
                        img_path: app.card_imgs[15]
                        img_path_b: app.card_imgs_b[15]
                    CharacterCardWidget:
                        card_index: 16
                        card_id_str: "16"
                        char_name: app.card_names[16]
                        char_roll: app.card_rolls[16]
                        img_path: app.card_imgs[16]
                        img_path_b: app.card_imgs_b[16]
                    CharacterCardWidget:
                        card_index: 17
                        card_id_str: "17"
                        char_name: app.card_names[17]
                        char_roll: app.card_rolls[17]
                        img_path: app.card_imgs[17]
                        img_path_b: app.card_imgs_b[17]
                    CharacterCardWidget:
                        card_index: 18
                        card_id_str: "18"
                        char_name: app.card_names[18]
                        char_roll: app.card_rolls[18]
                        img_path: app.card_imgs[18]
                        img_path_b: app.card_imgs_b[18]
                    CharacterCardWidget:
                        card_index: 19
                        card_id_str: "19"
                        char_name: app.card_names[19]
                        char_roll: app.card_rolls[19]
                        img_path: app.card_imgs[19]
                        img_path_b: app.card_imgs_b[19]
                    CharacterCardWidget:
                        card_index: 20
                        card_id_str: "20"
                        char_name: app.card_names[20]
                        char_roll: app.card_rolls[20]
                        img_path: app.card_imgs[20]
                        img_path_b: app.card_imgs_b[20]
                    CharacterCardWidget:
                        card_index: 21
                        card_id_str: "21"
                        char_name: app.card_names[21]
                        char_roll: app.card_rolls[21]
                        img_path: app.card_imgs[21]
                        img_path_b: app.card_imgs_b[21]
                    CharacterCardWidget:
                        card_index: 22
                        card_id_str: "22"
                        char_name: app.card_names[22]
                        char_roll: app.card_rolls[22]
                        img_path: app.card_imgs[22]
                        img_path_b: app.card_imgs_b[22]
                    CharacterCardWidget:
                        card_index: 23
                        card_id_str: "23"
                        char_name: app.card_names[23]
                        char_roll: app.card_rolls[23]
                        img_path: app.card_imgs[23]
                        img_path_b: app.card_imgs_b[23]
                    CharacterCardWidget:
                        card_index: 24
                        card_id_str: "24"
                        char_name: app.card_names[24]
                        char_roll: app.card_rolls[24]
                        img_path: app.card_imgs[24]
                        img_path_b: app.card_imgs_b[24]
                    CharacterCardWidget:
                        card_index: 25
                        card_id_str: "25"
                        char_name: app.card_names[25]
                        char_roll: app.card_rolls[25]
                        img_path: app.card_imgs[25]
                        img_path_b: app.card_imgs_b[25]
                    CharacterCardWidget:
                        card_index: 26
                        card_id_str: "26"
                        char_name: app.card_names[26]
                        char_roll: app.card_rolls[26]
                        img_path: app.card_imgs[26]
                        img_path_b: app.card_imgs_b[26]
                    CharacterCardWidget:
                        card_index: 27
                        card_id_str: "27"
                        char_name: app.card_names[27]
                        char_roll: app.card_rolls[27]
                        img_path: app.card_imgs[27]
                        img_path_b: app.card_imgs_b[27]
                    CharacterCardWidget:
                        card_index: 28
                        card_id_str: "28"
                        char_name: app.card_names[28]
                        char_roll: app.card_rolls[28]
                        img_path: app.card_imgs[28]
                        img_path_b: app.card_imgs_b[28]
                    CharacterCardWidget:
                        card_index: 29
                        card_id_str: "29"
                        char_name: app.card_names[29]
                        char_roll: app.card_rolls[29]
                        img_path: app.card_imgs[29]
                        img_path_b: app.card_imgs_b[29]
                    CharacterCardWidget:
                        card_index: 30
                        card_id_str: "30"
                        char_name: app.card_names[30]
                        char_roll: app.card_rolls[30]
                        img_path: app.card_imgs[30]
                        img_path_b: app.card_imgs_b[30]
                    CharacterCardWidget:
                        card_index: 31
                        card_id_str: "31"
                        char_name: app.card_names[31]
                        char_roll: app.card_rolls[31]
                        img_path: app.card_imgs[31]
                        img_path_b: app.card_imgs_b[31]
                    CharacterCardWidget:
                        card_index: 32
                        card_id_str: "32"
                        char_name: app.card_names[32]
                        char_roll: app.card_rolls[32]
                        img_path: app.card_imgs[32]
                        img_path_b: app.card_imgs_b[32]
                    CharacterCardWidget:
                        card_index: 33
                        card_id_str: "33"
                        char_name: app.card_names[33]
                        char_roll: app.card_rolls[33]
                        img_path: app.card_imgs[33]
                        img_path_b: app.card_imgs_b[33]
                    CharacterCardWidget:
                        card_index: 34
                        card_id_str: "34"
                        char_name: app.card_names[34]
                        char_roll: app.card_rolls[34]
                        img_path: app.card_imgs[34]
                        img_path_b: app.card_imgs_b[34]
                    CharacterCardWidget:
                        card_index: 35
                        card_id_str: "35"
                        char_name: app.card_names[35]
                        char_roll: app.card_rolls[35]
                        img_path: app.card_imgs[35]
                        img_path_b: app.card_imgs_b[35]
                    CharacterCardWidget:
                        card_index: 36
                        card_id_str: "36"
                        char_name: app.card_names[36]
                        char_roll: app.card_rolls[36]
                        img_path: app.card_imgs[36]
                        img_path_b: app.card_imgs_b[36]
                    CharacterCardWidget:
                        card_index: 37
                        card_id_str: "37"
                        char_name: app.card_names[37]
                        char_roll: app.card_rolls[37]
                        img_path: app.card_imgs[37]
                        img_path_b: app.card_imgs_b[37]
                    CharacterCardWidget:
                        card_index: 38
                        card_id_str: "38"
                        char_name: app.card_names[38]
                        char_roll: app.card_rolls[38]
                        img_path: app.card_imgs[38]
                        img_path_b: app.card_imgs_b[38]
                    CharacterCardWidget:
                        card_index: 39
                        card_id_str: "39"
                        char_name: app.card_names[39]
                        char_roll: app.card_rolls[39]
                        img_path: app.card_imgs[39]
                        img_path_b: app.card_imgs_b[39]
                    CharacterCardWidget:
                        card_index: 40
                        card_id_str: "40"
                        char_name: app.card_names[40]
                        char_roll: app.card_rolls[40]
                        img_path: app.card_imgs[40]
                        img_path_b: app.card_imgs_b[40]

            Button:
                text: "< Back"
                size_hint: (None, None)
                width: dp(65)
                height: dp(30)
                font_size: '12sp'
                bold: True
                background_normal: ''
                background_color: (0.0, 0.88, 1.0, 0.2)
                color: (0.0, 0.88, 1.0, 1)
                pos_hint: {'x': 0.02, 'top': 0.98}
                on_release: app.switch_to_home_screen()

    # 3. एडिट पैनल स्क्रीन
    Screen:
        name: 'edit_screen'
        FloatLayout:
            padding: dp(8)
            
            BoxLayout:
                orientation: 'vertical'
                size_hint: (1, 1)
                padding: [dp(10), dp(54), dp(10), dp(10)]
                spacing: dp(10)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                canvas.before:
                    Color:
                        rgba: (0.04, 0.05, 0.07, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(12)]
                    Color:
                        rgba: (0.0, 0.88, 1.0, 0.8)
                    Line:
                        rounded_rectangle: (self.x, self.y, self.width, self.height, dp(12))
                        width: dp(1.5)

                Label:
                    text: "[b][color=00e5ff]EDIT COMIC PANEL (" + app.current_active_card_str + ")[/color][/b] - [color=ffea00]" + app.current_selected_chapter + "[/color]"
                    markup: True
                    font_size: '14sp'
                    size_hint_y: None
                    height: dp(26)
                    halign: 'center'

                ScrollView:
                    size_hint: (1, 1)
                    do_scroll_x: False

                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(12)
                        padding: [dp(2), dp(6), dp(2), dp(16)]

                        # 🌟 ऊपर केवल 2 कार्ड्स (CHARACTER A और CHARACTER B)
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: (1, None)
                            height: dp(145)
                            spacing: dp(10)

                            # Box A
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint: (1, 1)
                                spacing: dp(4)

                                Label:
                                    text: "[b][color=ffea00]CHARACTER A[/color][/b]"
                                    markup: True
                                    font_size: '12sp'
                                    size_hint_y: None
                                    height: dp(16)
                                    halign: 'center'

                                GalleryImageButton:
                                    size_hint: (1, 1)
                                    canvas.before:
                                        Color:
                                            rgba: (0.08, 0.11, 0.16, 1)
                                        RoundedRectangle:
                                            pos: self.pos
                                            size: self.size
                                            radius: [dp(8)]
                                        Color:
                                            rgba: (0.0, 0.88, 1.0, 0.8)
                                        Line:
                                            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(8))
                                            width: dp(1.2)
                                    AsyncImage:
                                        source: app.character_img_path
                                        opacity: 1 if app.character_img_path else 0
                                        allow_stretch: True
                                        keep_ratio: True
                                        mipmap: True
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                        size_hint: (1, 1)
                                    Label:
                                        text: "Tap Avatar A" if not app.character_img_path else ""
                                        font_size: '10sp'
                                        color: (0.6, 0.65, 0.75, 1)
                                        halign: 'center'
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                            # Box B
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint: (1, 1)
                                spacing: dp(4)

                                Label:
                                    text: "[b][color=ffea00]CHARACTER B[/color][/b]"
                                    markup: True
                                    font_size: '12sp'
                                    size_hint_y: None
                                    height: dp(16)
                                    halign: 'center'

                                GalleryImageBButton:
                                    size_hint: (1, 1)
                                    canvas.before:
                                        Color:
                                            rgba: (0.08, 0.11, 0.16, 1)
                                        RoundedRectangle:
                                            pos: self.pos
                                            size: self.size
                                            radius: [dp(8)]
                                        Color:
                                            rgba: (0.0, 0.88, 1.0, 0.8)
                                        Line:
                                            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(8))
                                            width: dp(1.2)
                                    AsyncImage:
                                        source: app.character_img_b_path
                                        opacity: 1 if app.character_img_b_path else 0
                                        allow_stretch: True
                                        keep_ratio: True
                                        mipmap: True
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                        size_hint: (1, 1)
                                    Label:
                                        text: "Tap Avatar B" if not app.character_img_b_path else ""
                                        font_size: '10sp'
                                        color: (0.6, 0.65, 0.75, 1)
                                        halign: 'center'
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                        # 🌟 इनपुट्स
                        # 1. NAME
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: (1, None)
                            height: dp(42)
                            spacing: dp(8)

                            Label:
                                text: "NAME"
                                font_size: '12sp'
                                bold: True
                                size_hint_x: None
                                width: dp(75)
                                color: (0.0, 0.88, 1.0, 1)

                            TextInput:
                                id: name_edit_input
                                text: app.character_name
                                hint_text: "Comic / Episode Title..."
                                size_hint: (1, 1)
                                multiline: False
                                background_color: (0.08, 0.10, 0.15, 1)
                                foreground_color: (1, 1, 1, 1)
                                cursor_color: (0, 0.88, 1, 1)
                                padding: [dp(10), dp(11)]
                                on_text: app.character_name = self.text

                        # 2. ROLE
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: (1, None)
                            height: dp(42)
                            spacing: dp(8)

                            Label:
                                text: "ROLE"
                                font_size: '12sp'
                                bold: True
                                size_hint_x: None
                                width: dp(75)
                                color: (0.0, 0.88, 1.0, 1)

                            TextInput:
                                id: rollplay_edit_input
                                text: app.character_rollplay
                                hint_text: "Role / Description..."
                                size_hint: (1, 1)
                                multiline: False
                                background_color: (0.08, 0.10, 0.15, 1)
                                foreground_color: (1, 1, 1, 1)
                                cursor_color: (0, 0.88, 1, 1)
                                padding: [dp(10), dp(11)]
                                on_text: app.character_rollplay = self.text

                        # 3. AUDIO
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: (1, None)
                            height: dp(42)
                            spacing: dp(8)

                            Label:
                                text: "AUDIO"
                                font_size: '12sp'
                                bold: True
                                size_hint_x: None
                                width: dp(75)
                                color: (0.0, 0.88, 1.0, 1)

                            TextInput:
                                id: audio_input_field
                                text: app.audio_file_path
                                hint_text: "Tap Browse ->"
                                size_hint: (1, 1)
                                multiline: False
                                readonly: True
                                background_color: (0.08, 0.10, 0.15, 1)
                                foreground_color: (1, 1, 1, 1)
                                cursor_color: (0, 0.88, 1, 1)
                                padding: [dp(10), dp(11)]

                            Button:
                                text: "Browse"
                                size_hint: (None, 1)
                                width: dp(65)
                                font_size: '11sp'
                                bold: True
                                background_normal: ''
                                background_color: (0.12, 0.48, 0.88, 1)
                                color: (1, 1, 1, 1)
                                on_release: app.open_media_selector('audio_upload', is_video=False)

                            Button:
                                text: "Del"
                                size_hint: (None, 1)
                                width: dp(42)
                                font_size: '11sp'
                                bold: True
                                background_normal: ''
                                background_color: (0.88, 0.2, 0.2, 1)
                                color: (1, 1, 1, 1)
                                on_release: app.delete_audio_file()

                        # 4. TEXT A
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: (1, None)
                            height: dp(42)
                            spacing: dp(8)

                            Label:
                                text: "TEXT A"
                                font_size: '12sp'
                                bold: True
                                size_hint_x: None
                                width: dp(75)
                                color: (1, 0.9, 0.2, 1)

                            TextInput:
                                id: text_a_input
                                text: app.text_command_a
                                hint_text: "Character A dialogue / Notes..."
                                size_hint: (1, 1)
                                multiline: False
                                background_color: (0.08, 0.10, 0.15, 1)
                                foreground_color: (1, 1, 1, 1)
                                cursor_color: (0, 0.88, 1, 1)
                                padding: [dp(10), dp(11)]
                                on_text: app.text_command_a = self.text

                        # 5. TEXT B
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: (1, None)
                            height: dp(42)
                            spacing: dp(8)

                            Label:
                                text: "TEXT B"
                                font_size: '12sp'
                                bold: True
                                size_hint_x: None
                                width: dp(75)
                                color: (1, 0.9, 0.2, 1)

                            TextInput:
                                id: text_b_input
                                text: app.text_command_b
                                hint_text: "Character B dialogue / Notes..."
                                size_hint: (1, 1)
                                multiline: False
                                background_color: (0.08, 0.10, 0.15, 1)
                                foreground_color: (1, 1, 1, 1)
                                cursor_color: (0, 0.88, 1, 1)
                                padding: [dp(10), dp(11)]
                                on_text: app.text_command_b = self.text

                        # 🌟 6. नीचे तीनों स्क्रीन एक साथ (Scene 1, Scene 2, BG)
                        Label:
                            text: "[b][color=00e5ff]SCENE 1, SCENE 2 & BACKGROUND (BG) SCREENS[/color][/b]"
                            markup: True
                            font_size: '12sp'
                            size_hint_y: None
                            height: dp(22)
                            halign: 'left'

                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: (1, None)
                            height: dp(190)
                            spacing: dp(8)

                            # 1. Scene Image 1 (लेडी वाली मुख्य स्क्रीन)
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint: (1, 1)
                                spacing: dp(4)
                                SceneImage1Button:
                                    size_hint: (1, 1)
                                    canvas.before:
                                        Color:
                                            rgba: (0.06, 0.09, 0.14, 1)
                                        RoundedRectangle:
                                            pos: self.pos
                                            size: self.size
                                            radius: [dp(6)]
                                        Color:
                                            rgba: (0.0, 0.88, 1.0, 0.9)
                                        Line:
                                            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(6))
                                            width: dp(1.2)
                                    AsyncImage:
                                        source: app.scene_image_1_path
                                        opacity: 1 if app.scene_image_1_path else 0
                                        allow_stretch: True
                                        keep_ratio: True
                                        mipmap: True
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                    Label:
                                        text: "Scene Img 1" if not app.scene_image_1_path else ""
                                        font_size: '10sp'
                                        color: (0.0, 0.88, 1.0, 1)
                                        halign: 'center'
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                Button:
                                    text: "Del 1"
                                    size_hint: (1, None)
                                    height: dp(30)
                                    font_size: '10.5sp'
                                    bold: True
                                    background_normal: ''
                                    background_color: (0.88, 0.2, 0.2, 1)
                                    color: (1, 1, 1, 1)
                                    on_release: app.delete_scene_1_file()

                            # 2. Scene Image 2 (दूसरी नई सीन स्क्रीन)
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint: (1, 1)
                                spacing: dp(4)
                                SceneImage2Button:
                                    size_hint: (1, 1)
                                    canvas.before:
                                        Color:
                                            rgba: (0.06, 0.09, 0.14, 1)
                                        RoundedRectangle:
                                            pos: self.pos
                                            size: self.size
                                            radius: [dp(6)]
                                        Color:
                                            rgba: (0.0, 0.88, 1.0, 0.9)
                                        Line:
                                            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(6))
                                            width: dp(1.2)
                                    AsyncImage:
                                        source: app.scene_image_2_path
                                        opacity: 1 if app.scene_image_2_path else 0
                                        allow_stretch: True
                                        keep_ratio: True
                                        mipmap: True
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                    Label:
                                        text: "Scene Img 2" if not app.scene_image_2_path else ""
                                        font_size: '10sp'
                                        color: (0.0, 0.88, 1.0, 1)
                                        halign: 'center'
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                Button:
                                    text: "Del 2"
                                    size_hint: (1, None)
                                    height: dp(30)
                                    font_size: '10.5sp'
                                    bold: True
                                    background_normal: ''
                                    background_color: (0.88, 0.2, 0.2, 1)
                                    color: (1, 1, 1, 1)
                                    on_release: app.delete_scene_2_file()

                            # 3. BG Image (सिर्फ बैकग्राउंड के लिए)
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint: (1, 1)
                                spacing: dp(4)
                                BgImageButton:
                                    size_hint: (1, 1)
                                    canvas.before:
                                        Color:
                                            rgba: (0.06, 0.09, 0.14, 1)
                                        RoundedRectangle:
                                            pos: self.pos
                                            size: self.size
                                            radius: [dp(6)]
                                        Color:
                                            rgba: (0.0, 0.88, 1.0, 0.9)
                                        Line:
                                            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(6))
                                            width: dp(1.2)
                                    AsyncImage:
                                        source: app.scene_bg_image_path
                                        opacity: 1 if app.scene_bg_image_path else 0
                                        allow_stretch: True
                                        keep_ratio: True
                                        mipmap: True
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                    Label:
                                        text: "BG Screen" if not app.scene_bg_image_path else ""
                                        font_size: '10sp'
                                        color: (0.0, 0.88, 1.0, 1)
                                        halign: 'center'
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                Button:
                                    text: "Del BG"
                                    size_hint: (1, None)
                                    height: dp(30)
                                    font_size: '10.5sp'
                                    bold: True
                                    background_normal: ''
                                    background_color: (0.88, 0.2, 0.2, 1)
                                    color: (1, 1, 1, 1)
                                    on_release: app.delete_bg_image_file()

                        AnchorLayout:
                            anchor_x: 'center'
                            anchor_y: 'center'
                            size_hint: (1, None)
                            height: dp(60)

                            Button:
                                text: "SAVE COMIC PAGE"
                                size_hint: (None, None)
                                width: dp(240)
                                height: dp(46)
                                bold: True
                                font_size: '14sp'
                                background_normal: ''
                                background_color: (0.0, 0.85, 0.45, 1)
                                color: (0, 0, 0, 1)
                                on_release: app.save_edit_screen()

            # एडिट स्क्रीन के शीर्ष बटन (< Back, CHAPTER, Data)
            Button:
                text: "< Back"
                size_hint: (None, None)
                width: dp(65)
                height: dp(34)
                font_size: '12sp'
                bold: True
                background_normal: ''
                background_color: (0.0, 0.88, 1.0, 0.2)
                color: (0.0, 0.88, 1.0, 1)
                pos_hint: {'x': 0.02, 'top': 0.98}
                on_release: app.switch_to_home_screen()

            BoxLayout:
                orientation: 'horizontal'
                size_hint: (None, None)
                width: dp(175)
                height: dp(34)
                spacing: dp(8)
                pos_hint: {'right': 0.98, 'top': 0.98}

                Button:
                    text: "📖 Chapter"
                    bold: True
                    font_size: '11sp'
                    background_normal: ''
                    background_color: (0.9, 0.55, 0.0, 1)
                    color: (1, 1, 1, 1)
                    on_release: app.open_chapter_popup()

                Button:
                    text: "Data"
                    bold: True
                    font_size: '11sp'
                    background_normal: ''
                    background_color: (0.12, 0.48, 0.88, 1)
                    color: (1, 1, 1, 1)
                    on_release: app.open_card_data_popup()
'''

class CharacterCardWidget(BoxLayout):
    card_index = NumericProperty(0)
    card_id_str = StringProperty("1")
    char_name = StringProperty("")
    char_roll = StringProperty("")
    img_path = StringProperty("")
    img_path_b = StringProperty("")

class BlankKoraApp(App):
    character_img_path = StringProperty("")
    character_img_b_path = StringProperty("")
    audio_file_path = StringProperty("")
    scene_image_1_path = StringProperty("")
    scene_image_2_path = StringProperty("")
    scene_bg_image_path = StringProperty("")
    
    character_name = StringProperty("")
    character_rollplay = StringProperty("")
    text_command_a = StringProperty("")
    text_command_b = StringProperty("")
    
    current_selected_chapter = StringProperty("Chapter 1")
    active_edit_card_index = NumericProperty(1)
    current_active_card_str = StringProperty("1")
    
    card_names = DictProperty({})
    card_rolls = DictProperty({})
    card_imgs = DictProperty({})
    card_imgs_b = DictProperty({})
    card_scene_imgs = DictProperty({})
    card_scene_imgs_2 = DictProperty({})
    card_bgs = DictProperty({})
    card_chapters = DictProperty({})

    def build(self):
        try:
            os.makedirs("playground", exist_ok=True)
            for i in range(1, 41):
                self.card_names[i] = ""
                self.card_rolls[i] = ""
                self.card_imgs[i] = ""
                self.card_imgs_b[i] = ""
                self.card_scene_imgs[i] = ""
                self.card_scene_imgs_2[i] = ""
                self.card_bgs[i] = ""
                self.card_chapters[i] = "Chapter 1"
            
            self.load_commands_from_json()
            self.start_local_http_server()
        except Exception as e:
            self.toast(f"Build Error: {str(e)[:30]}")
        return Builder.load_string(KV)

    # =========================================================================
    # 🌟 हर कार्ड के लिए अलग चैप्टर पॉपअप (CHAPTER 1 TO 20)
    # =========================================================================
    def open_chapter_popup(self):
        try:
            card_num = self.active_edit_card_index
            main_box = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
            
            lbl_title = Label(
                text=f"[b][color=00e5ff]CARD {card_num} CHAPTERS (1 - 20)[/color][/b]",
                markup=True, size_hint_y=None, height=dp(30), font_size='13sp'
            )
            main_box.add_widget(lbl_title)

            scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
            grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, padding=[dp(4), dp(4)])
            grid.bind(minimum_height=grid.setter('height'))

            current_ch = self.card_chapters.get(card_num, "Chapter 1")

            for i in range(1, 21):
                ch_name = f"Chapter {i}"
                is_curr = (ch_name == current_ch)
                btn = Button(
                    text=f"📖 {ch_name}",
                    size_hint_y=None, height=dp(44),
                    font_size='12sp', bold=True,
                    background_normal='',
                    background_color=(0.0, 0.88, 0.45, 1) if is_curr else (0.1, 0.16, 0.24, 1),
                    color=(0, 0, 0, 1) if is_curr else (1, 1, 1, 1)
                )
                btn.bind(on_release=lambda instance, c=ch_name: self.select_chapter_action(c))
                grid.add_widget(btn)

            scroll.add_widget(grid)
            main_box.add_widget(scroll)

            btn_play = Button(
                text=f"▶ PLAY CARD {card_num} ({current_ch})",
                size_hint=(1, None), height=dp(46),
                bold=True, font_size='13sp',
                background_normal='',
                background_color=(0.95, 0.55, 0.0, 1), color=(1, 1, 1, 1)
            )
            btn_play.bind(on_release=lambda x: self.switch_to_chat_screen(card_index=card_num))
            main_box.add_widget(btn_play)

            self.ch_popup = Popup(
                title=f"Card {card_num} Chapters",
                content=main_box,
                size_hint=(0.88, 0.75),
                auto_dismiss=True
            )
            self.ch_popup.open()
        except Exception as e:
            self.toast(f"Chapter Popup Error: {str(e)[:30]}")

    def select_chapter_action(self, ch_name):
        card_num = self.active_edit_card_index
        self.card_chapters[card_num] = ch_name
        self.current_selected_chapter = ch_name
        if hasattr(self, 'ch_popup'):
            self.ch_popup.dismiss()
        self.toast(f"Card {card_num}: {ch_name} Selected!")

    def start_local_http_server(self):
        app_instance = self

        class ComicHandler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                super().end_headers()

            def do_GET(self):
                if self.path.startswith('/delete_page'):
                    try:
                        query = urllib.parse.urlparse(self.path).query
                        params = urllib.parse.parse_qs(query)
                        target_id = params.get('id', [''])[0]

                        if hasattr(app_instance, 'user_data_dir') and platform == 'android':
                            pg_dir = os.path.join(app_instance.user_data_dir, "playground")
                        else:
                            pg_dir = os.path.abspath("playground")

                        json_path = os.path.join(pg_dir, "commands.json")
                        if os.path.exists(json_path):
                            with open(json_path, "r", encoding="utf-8") as f:
                                data = json.load(f)

                            if "comic_pages" in data:
                                data["comic_pages"] = [p for p in data["comic_pages"] if str(p.get("id", "")) != str(target_id)]

                            with open(json_path, "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=4, ensure_ascii=False)

                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(b'{"success": true}')
                        return
                    except Exception as e:
                        print(f"Delete API Error: {e}")
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(b'{"success": false}')
                        return

                return super().do_GET()

        def run_server():
            try:
                PORT = 8000
                if hasattr(self, 'user_data_dir') and platform == 'android':
                    playground_dir = os.path.join(self.user_data_dir, "playground")
                else:
                    playground_dir = os.path.abspath("playground")
                
                os.makedirs(playground_dir, exist_ok=True)
                os.chdir(playground_dir)
                
                index_path = os.path.join(playground_dir, "index.html")
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write("""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <!-- 🌟 पिंच-टू-ज़ूम सक्षम (user-scalable=yes) -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, minimum-scale=0.5, user-scalable=yes">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <title>Kora Comic Reader & Live Color Studio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: #030508;
            color: #fff;
            font-family: 'Impact', 'Arial Black', sans-serif;
            overflow-x: auto;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }

        .top-fixed-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 52px;
            background: rgba(4, 7, 12, 0.95);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 8px;
            z-index: 9999;
            border-bottom: 2px solid #00e5ff;
            box-shadow: 0 4px 20px rgba(0, 229, 255, 0.25);
        }

        .card-badge-info {
            background: #00e5ff;
            color: #000;
            font-size: 11px;
            font-weight: 900;
            padding: 3px 6px;
            border-radius: 4px;
            border: 1.5px solid #000;
        }

        .chapter-badge-select {
            background: #ffea00;
            color: #000;
            font-size: 11px;
            font-weight: 900;
            border: 2px solid #000;
            padding: 4px 6px;
            border-radius: 6px;
            cursor: pointer;
            max-width: 105px;
        }

        /* 🌟 ज़ूम इन, ज़ूम आउट और रीसेट कंट्रोल्स */
        .zoom-toolbar {
            display: flex;
            align-items: center;
            gap: 3px;
            background: #0d1522;
            padding: 3px 6px;
            border-radius: 6px;
            border: 1.5px solid #00e5ff;
        }
        .btn-zoom {
            background: #1a273a;
            color: #00e5ff;
            border: 1px solid #00e5ff;
            font-size: 13px;
            font-weight: 900;
            width: 26px;
            height: 26px;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .btn-zoom:active { background: #00e5ff; color: #000; }
        .zoom-level-label {
            font-size: 10px;
            color: #ffea00;
            font-weight: bold;
            min-width: 34px;
            text-align: center;
            cursor: pointer;
        }

        .bar-btn-settings {
            background: linear-gradient(135deg, #00e5ff, #0088ff);
            color: #000;
            border: 2px solid #fff;
            padding: 5px 8px;
            font-size: 10px;
            font-weight: 900;
            border-radius: 6px;
            cursor: pointer;
            box-shadow: 2px 2px 0px #000;
        }

        .comic-feed-wrapper {
            width: 100%;
            overflow: visible;
            display: flex;
            justify-content: center;
        }

        .comic-feed {
            width: 100vw;
            max-width: 480px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 26px;
            padding: 68px 8px 60px;
            transition: transform 0.2s cubic-bezier(0.2, 0, 0, 1);
            transform-origin: top center;
        }

        .comic-page {
            width: 100%;
            background: #000;
            border: 4px solid #000;
            box-shadow: 0 12px 35px rgba(0,0,0,0.95);
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .page-control-bar {
            width: 100%;
            background: #080d16;
            border-bottom: 2px solid #000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 12px;
        }
        .comic-page-title {
            color: #00e5ff;
            font-size: 13px;
            font-weight: 900;
            letter-spacing: 0.8px;
        }
        .comic-del-page-btn {
            background: #e61919;
            color: #ffffff;
            font-family: inherit;
            font-size: 11px;
            letter-spacing: 0.5px;
            border: 2px solid #000;
            padding: 4px 10px;
            border-radius: 6px;
            cursor: pointer;
            box-shadow: 2px 2px 0px #000;
        }

        .top-split-panel-2 {
            width: 100%;
            height: 220px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4px;
            background: #000;
            border-bottom: 4px solid #000;
        }

        .avatar-box {
            position: relative;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #111;
        }

        .avatar-box img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        .comic-badge {
            position: absolute;
            top: 6px;
            width: 36px;
            height: 36px;
            background: #ffea00;
            color: #000;
            font-size: 20px;
            font-weight: 900;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2.5px solid #000;
            box-shadow: 2px 2px 0px #000;
            z-index: 10;
        }
        .badge-a { left: 6px; }
        .badge-b { right: 6px; }

        .comic-bubble {
            position: absolute;
            bottom: 6px;
            background: #fff;
            color: #000;
            border: 2px solid #000;
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 10.5px;
            font-weight: 900;
            text-transform: uppercase;
            box-shadow: 2px 2px 0px #000;
            max-width: 90%;
            word-break: break-word;
            z-index: 10;
            text-align: center;
        }
        .bubble-left { left: 6px; }
        .bubble-right { right: 6px; }

        /* 🌟 दोनों सीन इमेज एक साथ दिखने वाला लेआउट + BG बैकग्राउंड */
        .main-scene-panel {
            width: 100%;
            position: relative;
            background: #000;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-height: 360px;
        }

        .scene-bg-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 1;
            opacity: 0.95;
        }

        .scene-content-layer {
            position: relative;
            width: 100%;
            z-index: 2;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .dual-scene-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            width: 100%;
            padding: 4px;
        }

        .scene-half {
            position: relative;
            width: 100%;
            min-height: 350px;
            max-height: 560px;
            overflow: hidden;
            background: rgba(10, 14, 23, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(0, 229, 255, 0.4);
            border-radius: 6px;
        }

        .scene-half img, .single-scene-img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            display: block;
        }

        .single-scene-img {
            max-height: 600px;
            object-fit: contain;
        }

        .sound-btn {
            position: absolute;
            bottom: 12px;
            right: 12px;
            background: #ffea00;
            color: #000;
            border: 2.5px solid #000;
            padding: 5px 12px;
            border-radius: 8px;
            font-weight: 900;
            font-size: 13px;
            box-shadow: 2px 2px 0px #000;
            cursor: pointer;
            z-index: 25;
        }

        .settings-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            z-index: 100000;
            justify-content: center;
            align-items: center;
            padding: 12px;
        }

        .settings-box {
            width: 100%;
            max-width: 440px;
            max-height: 90vh;
            background: #070c14;
            border: 2px solid #00e5ff;
            border-radius: 14px;
            box-shadow: 0 10px 40px rgba(0, 229, 255, 0.4);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .settings-header {
            background: #0e1624;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #00e5ff;
        }
        .settings-header h3 {
            color: #00e5ff;
            font-size: 15px;
            letter-spacing: 0.8px;
        }
        .btn-close-modal {
            background: #e61919;
            color: #fff;
            border: 1px solid #000;
            border-radius: 6px;
            width: 28px;
            height: 28px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
        }

        .settings-body {
            padding: 14px 16px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .control-row {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .control-label-box {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11.5px;
            color: #d0e0f0;
        }
        .control-val-badge {
            color: #00e5ff;
            font-weight: bold;
            font-size: 12px;
        }

        .control-slider {
            -webkit-appearance: none;
            width: 100%;
            height: 8px;
            border-radius: 4px;
            background: #182436;
            outline: none;
        }
        .control-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #00e5ff;
            cursor: pointer;
            box-shadow: 0 0 8px #00e5ff;
        }

        .settings-footer {
            background: #0e1624;
            padding: 10px 14px;
            display: flex;
            gap: 8px;
            border-top: 1px solid #1a293e;
        }

        .btn-act {
            flex: 1;
            padding: 9px;
            font-size: 12px;
            font-weight: 900;
            border-radius: 6px;
            cursor: pointer;
            font-family: inherit;
        }
        .btn-reset { background: #444; color: #fff; border: 1px solid #777; }
        .btn-preview { background: #ffaa00; color: #000; border: 1px solid #000; }
        .btn-save { background: #00e5ff; color: #000; border: 1px solid #fff; }

        .empty-placeholder {
            margin: 50px auto;
            text-align: center;
            padding: 30px;
            border: 3px dashed #00e5ff;
            border-radius: 12px;
            max-width: 380px;
            color: #00e5ff;
            font-size: 16px;
        }
    </style>
</head>
<body>

    <div class="top-fixed-bar">
        <span class="card-badge-info" id="cardBadgeDisplay">CARD 1</span>
        
        <select class="chapter-badge-select" id="chapterSelector" onchange="switchChapter(this.value)">
            <!-- Chapters 1 to 20 -->
        </select>

        <!-- 🌟 ज़ूमिंग कंट्रोल्स -->
        <div class="zoom-toolbar">
            <button class="btn-zoom" onclick="zoomOut()" title="Zoom Out">−</button>
            <span class="zoom-level-label" id="zoomVal" onclick="resetZoom()" title="Click to Reset">100%</span>
            <button class="btn-zoom" onclick="zoomIn()" title="Zoom In">+</button>
        </div>

        <button class="bar-btn-settings" onclick="toggleSettingsModal()">⚙️ COLOR</button>
    </div>

    <svg style="position: absolute; width: 0; height: 0; overflow: hidden;" aria-hidden="true">
        <defs>
            <filter id="koraLiveFilter" color-interpolation-filters="sRGB">
                <feColorMatrix id="koraColorMatrix" type="matrix"
                    values="1 0 0 0 0
                            0 1 0 0 0
                            0 0 1 0 0
                            0 0 0 1 0" />
                <feConvolveMatrix id="koraSharpnessMatrix" order="3" preserveAlpha="true"
                    kernelMatrix="0 0 0
                                  0 1 0
                                  0 0 0" />
            </filter>
        </defs>
    </svg>

    <!-- कलर मॉडल -->
    <div id="settingsOverlay" class="settings-overlay">
        <div class="settings-box">
            <div class="settings-header">
                <h3>🎨 LIVE COLOR STUDIO</h3>
                <button class="btn-close-modal" onclick="toggleSettingsModal()">✕</button>
            </div>
            <div class="settings-body" id="settingsBody">
                <div class="control-row">
                    <div class="control-label-box">
                        <span>कलर / वाइब्रेंस (Color Boost)</span>
                        <span id="lblColor" class="control-val-badge">110%</span>
                    </div>
                    <input type="range" min="50" max="200" value="110" class="control-slider" id="rngColor" oninput="applyLiveTuning()">
                </div>
                <div class="control-row">
                    <div class="control-label-box">
                        <span>कंट्रास्ट (Contrast)</span>
                        <span id="lblContrast" class="control-val-badge">100%</span>
                    </div>
                    <input type="range" min="50" max="180" value="100" class="control-slider" id="rngContrast" oninput="applyLiveTuning()">
                </div>
                <div class="control-row">
                    <div class="control-label-box">
                        <span>ब्राइटनेस (Brightness)</span>
                        <span id="lblBrightness" class="control-val-badge">100%</span>
                    </div>
                    <input type="range" min="50" max="170" value="100" class="control-slider" id="rngBrightness" oninput="applyLiveTuning()">
                </div>
                <div class="control-row">
                    <div class="control-label-box">
                        <span>शैडो (Shadows)</span>
                        <span id="lblShadows" class="control-val-badge">0</span>
                    </div>
                    <input type="range" min="-50" max="50" value="0" class="control-slider" id="rngShadows" oninput="applyLiveTuning()">
                </div>
                <div class="control-row">
                    <div class="control-label-box">
                        <span>कलर टेम्परेचर (Cool ❄️ / Warm ☀️)</span>
                        <span id="lblTemp" class="control-val-badge">0</span>
                    </div>
                    <input type="range" min="-50" max="50" value="0" class="control-slider" id="rngTemp" oninput="applyLiveTuning()">
                </div>
                <div class="control-row">
                    <div class="control-label-box">
                        <span>पिंक इफ़ेक्ट (Pink Tone 🌸)</span>
                        <span id="lblPink" class="control-val-badge">0</span>
                    </div>
                    <input type="range" min="0" max="50" value="0" class="control-slider" id="rngPink" oninput="applyLiveTuning()">
                </div>
                <div class="control-row">
                    <div class="control-label-box">
                        <span>डिहेज़ (Dehaze 🌫️)</span>
                        <span id="lblDehaze" class="control-val-badge">0</span>
                    </div>
                    <input type="range" min="0" max="50" value="0" class="control-slider" id="rngDehaze" oninput="applyLiveTuning()">
                </div>
                <div class="control-row">
                    <div class="control-label-box">
                        <span>शार्पनेस (Sharpness 🗡️)</span>
                        <span id="lblSharpness" class="control-val-badge">0</span>
                    </div>
                    <input type="range" min="0" max="50" value="0" class="control-slider" id="rngSharpness" oninput="applyLiveTuning()">
                </div>
                <div class="control-row">
                    <div class="control-label-box">
                        <span>ह्यू रोटेशन (Hue 🌈)</span>
                        <span id="lblHue" class="control-val-badge">0°</span>
                    </div>
                    <input type="range" min="-180" max="180" value="0" class="control-slider" id="rngHue" oninput="applyLiveTuning()">
                </div>
            </div>
            <div class="settings-footer">
                <button class="btn-act btn-reset" onclick="resetToDefaults()">🔄 RESET</button>
                <button class="btn-act btn-preview" onclick="toggleOverlayVisibility()">👁️ HIDE UI</button>
                <button class="btn-act btn-save" onclick="saveSettings()">💾 SAVE</button>
            </div>
        </div>
    </div>

    <!-- कॉमिक फ़ीड -->
    <div class="comic-feed-wrapper">
        <div class="comic-feed" id="comicFeed">
            <div class="empty-placeholder">⚡ Loading Comic Strip...</div>
        </div>
    </div>

    <audio id="audioPlayer"></audio>

    <script>
        let allPages = [];
        let activeCard = "1";
        let activeChapter = "Chapter 1";
        let currentZoom = 1.0;

        function playAudio(src) {
            let player = document.getElementById('audioPlayer');
            player.src = src;
            player.play().catch(e => console.log(e));
        }

        // ========================================================
        // 🌟 ज़ूमिंग सिस्टम फंक्शंस
        // ========================================================
        function zoomIn() {
            if (currentZoom < 3.0) {
                currentZoom = Math.round((currentZoom + 0.15) * 100) / 100;
                applyZoom();
            }
        }

        function zoomOut() {
            if (currentZoom > 0.6) {
                currentZoom = Math.round((currentZoom - 0.15) * 100) / 100;
                applyZoom();
            }
        }

        function resetZoom() {
            currentZoom = 1.0;
            applyZoom();
        }

        function applyZoom() {
            let feed = document.getElementById('comicFeed');
            feed.style.transform = `scale(${currentZoom})`;
            document.getElementById('zoomVal').innerText = Math.round(currentZoom * 100) + '%';
        }

        async function deleteSinglePage(pageId) {
            if (!confirm("क्या आप सच में इस पेज को डिलीट करना चाहते हैं?")) return;
            try {
                let res = await fetch('/delete_page?id=' + pageId);
                let result = await res.json();
                if (result.success) {
                    let pageElem = document.getElementById('page_' + pageId);
                    if (pageElem) {
                        pageElem.style.transition = 'all 0.3s ease';
                        pageElem.style.opacity = '0';
                        pageElem.style.transform = 'scale(0.92)';
                        setTimeout(() => {
                            pageElem.remove();
                            if (document.querySelectorAll('.comic-page').length === 0) {
                                renderComicPages();
                            }
                        }, 300);
                    }
                }
            } catch(e) {
                alert("पेज डिलीट करने में समस्या: " + e);
            }
        }

        const DEFAULTS = { color: 110, contrast: 100, brightness: 100, shadows: 0, temp: 0, pink: 0, dehaze: 0, sharpness: 0, hue: 0 };

        function toggleSettingsModal() {
            let overlay = document.getElementById('settingsOverlay');
            overlay.style.display = (overlay.style.display === 'flex') ? 'none' : 'flex';
        }

        function toggleOverlayVisibility() {
            let box = document.getElementById('settingsBody');
            box.style.display = (box.style.display === 'none') ? 'flex' : 'none';
        }

        function applyLiveTuning() {
            let color = document.getElementById('rngColor').value;
            let contrast = document.getElementById('rngContrast').value;
            let brightness = document.getElementById('rngBrightness').value;
            let shadows = parseFloat(document.getElementById('rngShadows').value);
            let temp = parseFloat(document.getElementById('rngTemp').value);
            let pink = parseFloat(document.getElementById('rngPink').value);
            let dehaze = parseFloat(document.getElementById('rngDehaze').value);
            let sharpness = parseFloat(document.getElementById('rngSharpness').value);
            let hue = document.getElementById('rngHue').value;

            document.getElementById('lblColor').innerText = color + '%';
            document.getElementById('lblContrast').innerText = contrast + '%';
            document.getElementById('lblBrightness').innerText = brightness + '%';
            document.getElementById('lblShadows').innerText = (shadows > 0 ? '+' : '') + shadows;
            document.getElementById('lblTemp').innerText = (temp > 0 ? '+' : '') + temp;
            document.getElementById('lblPink').innerText = pink;
            document.getElementById('lblDehaze').innerText = dehaze;
            document.getElementById('lblSharpness').innerText = sharpness;
            document.getElementById('lblHue').innerText = hue + '°';

            let t = temp / 100, p = pink / 100, dh = dehaze / 100, sh = shadows / 100;
            let rMult = (1 + t * 0.22) * (1 + p * 0.18) * (1 + dh * 0.12);
            let gMult = (1 - p * 0.10) * (1 + dh * 0.12);
            let bMult = (1 - t * 0.22) * (1 + p * 0.25) * (1 + dh * 0.12);

            let offset = (sh * 0.05) - (dh * 0.04);
            let rOff = offset + (p * 0.025);
            let gOff = offset - (p * 0.015);
            let bOff = offset + (p * 0.035);

            let matrixValues = `
                ${rMult.toFixed(3)} 0 0 0 ${rOff.toFixed(3)}
                0 ${gMult.toFixed(3)} 0 0 ${gOff.toFixed(3)}
                0 0 ${bMult.toFixed(3)} 0 ${bOff.toFixed(3)}
                0 0 0 1 0
            `.trim();
            document.getElementById('koraColorMatrix').setAttribute('values', matrixValues);

            let sKernel = sharpness > 0 ? (sharpness / 100) * 0.8 : 0;
            let cVal = (1 + 4 * sKernel).toFixed(2);
            let nVal = (-sKernel).toFixed(2);
            let kernelStr = `0 ${nVal} 0  ${nVal} ${cVal} ${nVal}  0 ${nVal} 0`;
            document.getElementById('koraSharpnessMatrix').setAttribute('kernelMatrix', kernelStr);

            let cssFilter = `brightness(${brightness}%) contrast(${contrast}%) saturate(${color}%) hue-rotate(${hue}deg) url(#koraLiveFilter)`;
            
            let targets = document.querySelectorAll('.scene-half img, .single-scene-img, .avatar-box img');
            targets.forEach(img => {
                img.style.filter = cssFilter;
                img.style.webkitFilter = cssFilter;
            });
        }

        function resetToDefaults() {
            setSliderValues(DEFAULTS);
            applyLiveTuning();
            localStorage.removeItem('kora_user_tunings');
        }

        function saveSettings() {
            let current = {
                color: document.getElementById('rngColor').value,
                contrast: document.getElementById('rngContrast').value,
                brightness: document.getElementById('rngBrightness').value,
                shadows: document.getElementById('rngShadows').value,
                temp: document.getElementById('rngTemp').value,
                pink: document.getElementById('rngPink').value,
                dehaze: document.getElementById('rngDehaze').value,
                sharpness: document.getElementById('rngSharpness').value,
                hue: document.getElementById('rngHue').value
            };
            localStorage.setItem('kora_user_tunings', JSON.stringify(current));
            alert("✅ Color Tuning Settings Saved!");
            toggleSettingsModal();
        }

        function setSliderValues(cfg) {
            document.getElementById('rngColor').value = cfg.color;
            document.getElementById('rngContrast').value = cfg.contrast;
            document.getElementById('rngBrightness').value = cfg.brightness;
            document.getElementById('rngShadows').value = cfg.shadows;
            document.getElementById('rngTemp').value = cfg.temp;
            document.getElementById('rngPink').value = cfg.pink;
            document.getElementById('rngDehaze').value = cfg.dehaze;
            document.getElementById('rngSharpness').value = cfg.sharpness;
            document.getElementById('rngHue').value = cfg.hue;
        }

        function loadSavedSettings() {
            let saved = localStorage.getItem('kora_user_tunings');
            if (saved) {
                try {
                    let cfg = JSON.parse(saved);
                    setSliderValues(cfg);
                } catch(e) {}
            } else {
                setSliderValues(DEFAULTS);
            }
            applyLiveTuning();
        }

        function initChapterDropdown() {
            let sel = document.getElementById('chapterSelector');
            sel.innerHTML = '';
            for(let i=1; i<=20; i++) {
                let opt = document.createElement('option');
                opt.value = `Chapter ${i}`;
                opt.innerText = `📖 Chapter ${i}`;
                if(`Chapter ${i}` === activeChapter) opt.selected = true;
                sel.appendChild(opt);
            }
        }

        function switchChapter(ch) {
            activeChapter = ch;
            renderComicPages();
        }

        // ========================================================
        // 🌟 कार्ड और चैप्टर के अनुसार अलग-अलग पेज रेंडर करना
        // ========================================================
        function renderComicPages() {
            let container = document.getElementById('comicFeed');
            document.getElementById('cardBadgeDisplay').innerText = `CARD ${activeCard}`;

            // कार्ड और चैप्टर दोनों का मेल होना ज़रूरी है (कोई डेटा मिक्स नहीं होगा)
            let pages = allPages.filter(p => {
                let pCard = String(p.card_index || '1');
                let pChap = p.chapter || 'Chapter 1';
                return (pCard === String(activeCard)) && (pChap === activeChapter);
            });

            if(pages.length === 0) {
                container.innerHTML = `
                    <div class="empty-placeholder">
                        📖 NO PAGES IN CARD ${activeCard} - ${activeChapter} YET!<br><br>
                        Go to Edit panel for Card ${activeCard}, add images, and tap <b>SAVE COMIC PAGE</b>!
                    </div>
                `;
                return;
            }

            let html = '';
            pages.forEach((p, idx) => {
                let avA = p.avatar_a ? `<img src="${p.avatar_a}?t=${p.timestamp}">` : `<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#444;font-size:11px;">AVATAR A</div>`;
                let avB = p.avatar_b ? `<img src="${p.avatar_b}?t=${p.timestamp}">` : `<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#444;font-size:11px;">AVATAR B</div>`;
                
                let txtA = p.text_a || "";
                let txtB = p.text_b || "";

                let topAvatarsHtml = `
                    <div class="top-split-panel-2">
                        <div class="avatar-box">
                            <div class="comic-badge badge-a">A</div>
                            ${avA}
                            ${txtA ? `<div class="comic-bubble bubble-left">${txtA}</div>` : ''}
                        </div>
                        <div class="avatar-box">
                            <div class="comic-badge badge-b">B</div>
                            ${avB}
                            ${txtB ? `<div class="comic-bubble bubble-right">${txtB}</div>` : ''}
                        </div>
                    </div>
                `;

                // 🌟 दोनों सीन इमेज एक साथ दिखने वाला लेआउट + BG बैकग्राउंड
                let sc1 = p.scene_image_1 || '';
                let sc2 = p.scene_image_2 || '';
                let bg = p.scene_bg || '';

                let innerSceneHtml = '';
                if (sc1 && sc2) {
                    innerSceneHtml = `
                        <div class="dual-scene-grid">
                            <div class="scene-half"><img src="${sc1}?t=${p.timestamp}" class="glamour-8k-layer"></div>
                            <div class="scene-half"><img src="${sc2}?t=${p.timestamp}" class="glamour-8k-layer"></div>
                        </div>
                    `;
                } else if (sc1) {
                    innerSceneHtml = `<img src="${sc1}?t=${p.timestamp}" class="single-scene-img glamour-8k-layer">`;
                } else if (sc2) {
                    innerSceneHtml = `<img src="${sc2}?t=${p.timestamp}" class="single-scene-img glamour-8k-layer">`;
                } else {
                    innerSceneHtml = `<div style="height:260px;display:flex;align-items:center;justify-content:center;color:#666;">No Scene Images</div>`;
                }

                html += `
                    <div class="comic-page" id="page_${p.id}">
                        <div class="page-control-bar">
                            <span class="comic-page-title">CARD ${activeCard} • ${activeChapter} • P#${idx + 1}</span>
                            <button class="comic-del-page-btn" onclick="deleteSinglePage('${p.id}')">🗑 DELETE</button>
                        </div>

                        ${topAvatarsHtml}

                        <div class="main-scene-panel">
                            ${bg ? `<img src="${bg}?t=${p.timestamp}" class="scene-bg-layer">` : ''}
                            <div class="scene-content-layer">
                                ${innerSceneHtml}
                            </div>
                            ${p.audio ? `<button class="sound-btn" onclick="playAudio('${p.audio}')">🔊 SOUND</button>` : ''}
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
            applyLiveTuning();
        }

        window.addEventListener('DOMContentLoaded', async () => {
            const urlParams = new URLSearchParams(window.location.search);
            const cardParam = urlParams.get('card');
            const chParam = urlParams.get('chapter');
            
            if(cardParam) activeCard = cardParam;
            if(chParam) activeChapter = chParam;

            initChapterDropdown();

            try {
                let res = await fetch('commands.json?t=' + Date.now(), { cache: 'no-store' });
                let data = await res.json();
                allPages = data.comic_pages || [];
                renderComicPages();
                loadSavedSettings();
            } catch(e) {
                document.getElementById('comicFeed').innerHTML = `<div class="empty-placeholder" style="color:red;">Error loading comic data!</div>`;
            }
        });
    </script>
</body>
</html>""")

                Handler = ComicHandler
                with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
                    print(f"Server serving from: {playground_dir}")
                    httpd.serve_forever()
            except Exception as e:
                print(f"HTTP Server Error: {e}")

        threading.Thread(target=run_server, daemon=True).start()

    def on_start(self):
        try:
            os.makedirs("playground", exist_ok=True)
            self.load_commands_from_json()
            self.request_android_permissions()
        except Exception as e:
            self.toast(f"OnStart Error: {str(e)[:30]}")

    def request_android_permissions(self, callback=None):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                perms = [
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    "android.permission.READ_MEDIA_IMAGES",
                    "android.permission.READ_MEDIA_AUDIO"
                ]
                request_permissions(perms, callback=callback if callback else lambda p, g: None)
            except Exception as e:
                print(f"Permission error: {e}")

    def delete_audio_file(self):
        self.audio_file_path = ""
        self.toast("Audio Deleted!")

    def delete_scene_1_file(self):
        self.scene_image_1_path = ""
        self.toast("Scene 1 Image Deleted!")

    def delete_scene_2_file(self):
        self.scene_image_2_path = ""
        self.toast("Scene 2 Image Deleted!")

    def delete_bg_image_file(self):
        self.scene_bg_image_path = ""
        self.toast("BG Image Deleted!")

    def open_setting_popup(self):
        try:
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
            
            btn_folder = Button(
                text="📁 Open Data Folder",
                size_hint=(1, None), height=dp(45),
                bold=True, background_normal='',
                background_color=(0.12, 0.48, 0.88, 1), color=(1, 1, 1, 1)
            )
            
            btn_delete = Button(
                text="🗑 Delete All Comics Pages",
                size_hint=(1, None), height=dp(45),
                bold=True, background_normal='',
                background_color=(0.88, 0.2, 0.2, 1), color=(1, 1, 1, 1)
            )

            content.add_widget(btn_folder)
            content.add_widget(btn_delete)

            self.setting_popup = Popup(
                title="Settings & Data Manager",
                content=content,
                size_hint=(0.85, 0.4),
                auto_dismiss=True
            )

            btn_folder.bind(on_release=lambda x: self.show_data_folder_contents())
            btn_delete.bind(on_release=lambda x: self.confirm_delete_all_data())

            self.setting_popup.open()
        except Exception as e:
            self.toast(f"Setting Error: {str(e)[:30]}")

    def open_card_data_popup(self):
        try:
            card_num = self.active_edit_card_index
            content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15))
            
            btn_data_card = Button(
                text=f"📁 View Data of Card {card_num}",
                size_hint=(1, None), height=dp(45),
                bold=True, background_normal='',
                background_color=(0.12, 0.48, 0.88, 1), color=(1, 1, 1, 1)
            )
            
            btn_delete_card = Button(
                text=f"🗑 Delete Comic Pages for Card {card_num}",
                size_hint=(1, None), height=dp(45),
                bold=True, background_normal='',
                background_color=(0.88, 0.2, 0.2, 1), color=(1, 1, 1, 1)
            )

            content.add_widget(btn_data_card)
            content.add_widget(btn_delete_card)

            self.card_data_popup = Popup(
                title=f"Card {card_num} Data Manager",
                content=content,
                size_hint=(0.85, 0.35),
                auto_dismiss=True
            )

            btn_data_card.bind(on_release=lambda x: self.view_card_data(card_num))
            btn_delete_card.bind(on_release=lambda x: self.confirm_delete_card_data(card_num))

            self.card_data_popup.open()
        except Exception as e:
            self.toast(f"Card Data Popup Err: {str(e)[:30]}")

    def view_card_data(self, card_num):
        try:
            ch = self.card_chapters.get(card_num, "Chapter 1")
            card_info = {
                "card_index": card_num,
                "current_chapter": ch,
                "name": self.character_name,
                "role": self.character_rollplay,
                "avatar_a": self.character_img_path,
                "avatar_b": self.character_img_b_path,
                "audio": self.audio_file_path,
                "scene_image_1": self.scene_image_1_path,
                "scene_image_2": self.scene_image_2_path,
                "scene_bg": self.scene_bg_image_path,
                "text_a": self.text_command_a,
                "text_b": self.text_command_b
            }
            
            pretty_text = json.dumps(card_info, indent=4)

            if hasattr(self, 'card_data_popup'):
                self.card_data_popup.dismiss()

            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
            
            scroll = ScrollView(size_hint=(1, 1))
            lbl = Label(
                text=pretty_text,
                size_hint_y=None,
                font_size='11sp',
                color=(0, 0.88, 1, 1),
                halign='left', valign='top'
            )
            lbl.bind(texture_size=lambda s, w: setattr(s, 'height', w[1]))
            lbl.bind(width=lambda s, w: setattr(s, 'text_size', (w, None)))
            scroll.add_widget(lbl)
            
            btn_close = Button(
                text="Close",
                size_hint=(1, None), height=dp(40),
                bold=True, background_normal='',
                background_color=(0.12, 0.48, 0.88, 1), color=(1, 1, 1, 1)
            )

            content.add_widget(scroll)
            content.add_widget(btn_close)

            self.view_popup = Popup(
                title=f"Data of Card {card_num}",
                content=content,
                size_hint=(0.85, 0.65),
                auto_dismiss=True
            )
            btn_close.bind(on_release=lambda x: self.view_popup.dismiss())
            self.view_popup.open()
        except Exception as e:
            self.toast(f"View Data Err: {str(e)[:30]}")

    def confirm_delete_card_data(self, card_num):
        try:
            self.card_names[card_num] = ""
            self.card_rolls[card_num] = ""
            self.card_imgs[card_num] = ""
            self.card_imgs_b[card_num] = ""
            self.card_scene_imgs[card_num] = ""
            self.card_scene_imgs_2[card_num] = ""
            self.card_bgs[card_num] = ""
            
            if self.active_edit_card_index == card_num:
                self.character_name = ""
                self.character_rollplay = ""
                self.character_img_path = ""
                self.character_img_b_path = ""
                self.audio_file_path = ""
                self.scene_image_1_path = ""
                self.scene_image_2_path = ""
                self.scene_bg_image_path = ""
                self.text_command_a = ""
                self.text_command_b = ""

            if hasattr(self, 'user_data_dir') and platform == 'android':
                pg_dir = os.path.join(self.user_data_dir, "playground")
            else:
                pg_dir = os.path.abspath("playground")
                
            json_path = os.path.join(pg_dir, "commands.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if "character_cards_meta" in data and str(card_num) in data["character_cards_meta"]:
                    del data["character_cards_meta"][str(card_num)]

                if "comic_pages" in data:
                    data["comic_pages"] = [p for p in data["comic_pages"] if p.get("card_index") != int(card_num)]

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

            if hasattr(self, 'card_data_popup'):
                self.card_data_popup.dismiss()

            self.toast(f"Card {card_num} Pages Deleted!")
        except Exception as e:
            self.toast(f"Delete Card Err: {str(e)[:30]}")

    def show_data_folder_contents(self):
        try:
            if hasattr(self, 'user_data_dir') and platform == 'android':
                pg_dir = os.path.join(self.user_data_dir, "playground")
            else:
                pg_dir = os.path.abspath("playground")

            os.makedirs(pg_dir, exist_ok=True)
            files = os.listdir(pg_dir)
            file_list_text = "\n".join(files) if files else "Folder is empty!"

            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
            scroll = ScrollView(size_hint=(1, 1))
            lbl = Label(
                text=file_list_text,
                size_hint_y=None,
                font_size='12sp',
                color=(0, 0.88, 1, 1),
                halign='left', valign='top'
            )
            lbl.bind(texture_size=lambda s, w: setattr(s, 'height', w[1]))
            lbl.bind(width=lambda s, w: setattr(s, 'text_size', (w, None)))
            scroll.add_widget(lbl)
            
            btn_close = Button(
                text="Close",
                size_hint=(1, None), height=dp(40),
                bold=True, background_normal='',
                background_color=(0.12, 0.48, 0.88, 1), color=(1, 1, 1, 1)
            )

            content.add_widget(scroll)
            content.add_widget(btn_close)

            self.data_popup = Popup(
                title="Playground Data Files",
                content=content,
                size_hint=(0.85, 0.6),
                auto_dismiss=True
            )
            btn_close.bind(on_release=lambda x: self.data_popup.dismiss())
            self.data_popup.open()
        except Exception as e:
            self.toast(f"Folder Err: {str(e)[:30]}")

    def confirm_delete_all_data(self):
        try:
            if hasattr(self, 'user_data_dir') and platform == 'android':
                pg_dir = os.path.join(self.user_data_dir, "playground")
            else:
                pg_dir = os.path.abspath("playground")

            if os.path.exists(pg_dir):
                for f in os.listdir(pg_dir):
                    if f.startswith("media_"):
                        try:
                            os.remove(os.path.join(pg_dir, f))
                        except Exception:
                            pass

            json_path = os.path.join(pg_dir, "commands.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump({"comic_pages": [], "character_cards_meta": {}}, f, indent=4, ensure_ascii=False)

            self.character_img_path = ""
            self.character_img_b_path = ""
            self.audio_file_path = ""
            self.scene_image_1_path = ""
            self.scene_image_2_path = ""
            self.scene_bg_image_path = ""
            self.character_name = ""
            self.character_rollplay = ""
            self.text_command_a = ""
            self.text_command_b = ""
            
            for i in range(1, 41):
                self.card_names[i] = ""
                self.card_rolls[i] = ""
                self.card_imgs[i] = ""
                self.card_imgs_b[i] = ""
                self.card_scene_imgs[i] = ""
                self.card_scene_imgs_2[i] = ""
                self.card_bgs[i] = ""
                self.card_chapters[i] = "Chapter 1"

            if hasattr(self, 'setting_popup'):
                self.setting_popup.dismiss()

            self.toast("All Comic Pages Cleared & Reset!")
        except Exception as e:
            self.toast(f"Delete Error: {str(e)[:30]}")

    def open_media_selector(self, key_type, is_video=False):
        self.current_target_key = key_type

        if platform == 'android':
            try:
                from android import activity
                from jnius import autoclass

                Intent = autoclass('android.content.Intent')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                intent = Intent(Intent.ACTION_GET_CONTENT)
                if key_type == 'audio_upload':
                    intent.setType("audio/*")
                else:
                    intent.setType("image/*")

                intent.addCategory(Intent.CATEGORY_OPENABLE)

                try:
                    activity.unbind(on_activity_result=self._on_activity_result)
                except Exception:
                    pass

                activity.bind(on_activity_result=self._on_activity_result)
                PythonActivity.mActivity.startActivityForResult(intent, 5005)
                return
            except Exception as e:
                self.toast(f"Intent Error: {str(e)[:30]}")
                return
        else:
            self.toast("Gallery picker works on Android device!")

    def _on_activity_result(self, request_code, result_code, intent_data):
        if request_code == 5005:
            if result_code == -1 and intent_data is not None:
                try:
                    uri = intent_data.getData()
                    if uri is None:
                        clip = intent_data.getClipData()
                        if clip is not None and clip.getItemCount() > 0:
                            uri = clip.getItemAt(0).getUri()

                    if uri is not None:
                        path = self._copy_uri_to_playground(uri)
                        if path and os.path.exists(path):
                            Clock.schedule_once(lambda dt: self._apply_media_path(path), 0)
                        else:
                            self.toast("Error: File not loaded!")
                    else:
                        self.toast("Error: URI is None!")
                except Exception as e:
                    self.toast(f"Result Error: {str(e)[:30]}")
            else:
                self.toast("Selection cancelled")

    def _copy_uri_to_playground(self, uri):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            cr = PythonActivity.mActivity.getContentResolver()
            in_stream = cr.openInputStream(uri)
            if in_stream is None:
                return None

            is_audio_type = (self.current_target_key == 'audio_upload')
            ext = ".mp3" if is_audio_type else ".jpg"
            
            if hasattr(self, 'user_data_dir') and platform == 'android':
                out_dir = os.path.join(self.user_data_dir, "playground")
            else:
                out_dir = os.path.abspath("playground")
                
            os.makedirs(out_dir, exist_ok=True)
            filename = f"media_{int(time.time())}_{random.randint(1000, 9999)}{ext}"
            out_path = os.path.join(out_dir, filename)

            FileOutputStream = autoclass('java.io.FileOutputStream')
            out_stream = FileOutputStream(out_path)

            copied = False
            try:
                FileUtils = autoclass('android.os.FileUtils')
                FileUtils.copy(in_stream, out_stream)
                copied = True
            except Exception:
                pass

            if not copied:
                try:
                    BufferedInputStream = autoclass('java.io.BufferedInputStream')
                    bis = BufferedInputStream(in_stream)
                    buf = bytearray(32768)
                    while True:
                        length = bis.read(buf)
                        if length <= 0:
                            break
                        out_stream.write(buf, 0, length)
                    bis.close()
                    copied = True
                except Exception:
                    pass

            out_stream.flush()
            out_stream.close()
            in_stream.close()

            if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                return out_path
        except Exception as e:
            self.toast(f"Copy Exc: {str(e)[:30]}")
        return None

    def _apply_media_path(self, path):
        if not path or not os.path.exists(path):
            self.toast("File not found!")
            return

        k = self.current_target_key
        if k == 'character_image':
            self.character_img_path = path
            self.toast("Avatar A Selected!")
        elif k == 'character_image_b':
            self.character_img_b_path = path
            self.toast("Avatar B Selected!")
        elif k == 'scene_image_1':
            self.scene_image_1_path = path
            self.toast("Scene Image 1 Selected!")
        elif k == 'scene_image_2':
            self.scene_image_2_path = path
            self.toast("Scene Image 2 Selected!")
        elif k == 'scene_bg_image':
            self.scene_bg_image_path = path
            self.toast("Background (BG) Selected!")
        elif k == 'audio_upload':
            self.audio_file_path = path
            self.toast("Audio File Selected!")

    def load_commands_from_json(self):
        try:
            if hasattr(self, 'user_data_dir') and platform == 'android':
                pg_dir = os.path.join(self.user_data_dir, "playground")
            else:
                pg_dir = os.path.abspath("playground")
                
            json_path = os.path.join(pg_dir, "commands.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    meta_dict = data.get("character_cards_meta", {})
                    for k, meta in meta_dict.items():
                        idx = int(k)
                        if 1 <= idx <= 40:
                            avatar_file = meta.get("avatar", "")
                            avatar_b_file = meta.get("avatar_b", "")
                            scene_file_1 = meta.get("scene_image_1", meta.get("scene_image", ""))
                            scene_file_2 = meta.get("scene_image_2", "")
                            bg_file = meta.get("scene_bg", "")

                            av_path = os.path.join(pg_dir, avatar_file) if avatar_file and os.path.exists(os.path.join(pg_dir, avatar_file)) else ""
                            av_b_path = os.path.join(pg_dir, avatar_b_file) if avatar_b_file and os.path.exists(os.path.join(pg_dir, avatar_b_file)) else ""
                            sc1_path = os.path.join(pg_dir, scene_file_1) if scene_file_1 and os.path.exists(os.path.join(pg_dir, scene_file_1)) else ""
                            sc2_path = os.path.join(pg_dir, scene_file_2) if scene_file_2 and os.path.exists(os.path.join(pg_dir, scene_file_2)) else ""
                            bg_path = os.path.join(pg_dir, bg_file) if bg_file and os.path.exists(os.path.join(pg_dir, bg_file)) else ""

                            self.card_names[idx] = meta.get("name", "")
                            self.card_rolls[idx] = meta.get("role", "")
                            self.card_imgs[idx] = av_path
                            self.card_imgs_b[idx] = av_b_path
                            self.card_scene_imgs[idx] = sc1_path
                            self.card_scene_imgs_2[idx] = sc2_path
                            self.card_bgs[idx] = bg_path
                            self.card_chapters[idx] = meta.get("current_chapter", "Chapter 1")
        except Exception as e:
            self.toast(f"LoadCmd Error: {str(e)[:30]}")

    def save_edit_screen(self):
        try:
            text_a = self.text_command_a.strip()
            text_b = self.text_command_b.strip()
            sc1 = self.scene_image_1_path.strip()
            sc2 = self.scene_image_2_path.strip()
            bgpath = self.scene_bg_image_path.strip()
            audiopath = self.audio_file_path.strip()
            av_a = self.character_img_path.strip()
            av_b = self.character_img_b_path.strip()

            if not av_a and not av_b and not sc1 and not sc2 and not bgpath and not text_a and not text_b:
                self.toast("Error: Add images or text to save page!")
                return

            if hasattr(self, 'user_data_dir') and platform == 'android':
                pg_dir = os.path.join(self.user_data_dir, "playground")
            else:
                pg_dir = os.path.abspath("playground")
                
            os.makedirs(pg_dir, exist_ok=True)
            json_path = os.path.join(pg_dir, "commands.json")
            data = {}
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {}

            if "comic_pages" not in data or not isinstance(data["comic_pages"], list):
                data["comic_pages"] = []

            card_key = int(self.active_edit_card_index)
            active_ch = self.card_chapters.get(card_key, self.current_selected_chapter)

            new_page = {
                "id": int(time.time() * 1000),
                "chapter": active_ch,
                "card_index": card_key,
                "name": self.character_name,
                "role": self.character_rollplay,
                "avatar_a": os.path.basename(av_a) if av_a else "",
                "avatar_b": os.path.basename(av_b) if av_b else "",
                "text_a": text_a if text_a else "",
                "text_b": text_b if text_b else "",
                "scene_image_1": os.path.basename(sc1) if sc1 else "",
                "scene_image_2": os.path.basename(sc2) if sc2 else "",
                "scene_bg": os.path.basename(bgpath) if bgpath else "",
                "audio": os.path.basename(audiopath) if audiopath else "",
                "timestamp": int(time.time() * 1000)
            }

            data["comic_pages"].append(new_page)

            if "character_cards_meta" not in data:
                data["character_cards_meta"] = {}

            data["character_cards_meta"][str(card_key)] = {
                "name": self.character_name,
                "role": self.character_rollplay,
                "current_chapter": active_ch,
                "text_a": text_a,
                "text_b": text_b,
                "avatar": os.path.basename(av_a) if av_a else "",
                "avatar_b": os.path.basename(av_b) if av_b else "",
                "scene_image_1": os.path.basename(sc1) if sc1 else "",
                "scene_image_2": os.path.basename(sc2) if sc2 else "",
                "scene_bg": os.path.basename(bgpath) if bgpath else ""
            }

            self.card_names[card_key] = self.character_name
            self.card_rolls[card_key] = self.character_rollplay
            self.card_imgs[card_key] = self.character_img_path
            self.card_imgs_b[card_key] = self.character_img_b_path
            self.card_scene_imgs[card_key] = self.scene_image_1_path
            self.card_scene_imgs_2[card_key] = self.scene_image_2_path
            self.card_bgs[card_key] = self.scene_bg_image_path
            self.card_chapters[card_key] = active_ch

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            self.toast(f"Saved: Card {card_key} • {active_ch}!")
            self.switch_to_character_screen()
        except Exception as e:
            self.toast(f"SaveEdit Error: {str(e)[:30]}")

    def switch_to_character_screen(self):
        try:
            self.root.current = 'character_screen'
        except Exception as e:
            self.toast(f"Switch Err: {str(e)[:30]}")

    def switch_to_home_screen(self):
        try:
            self.root.current = 'home_screen'
        except Exception as e:
            self.toast(f"Home Switch Err: {str(e)[:30]}")

    def switch_to_chat_screen(self, card_index=None):
        try:
            c_idx = card_index if card_index is not None else self.active_edit_card_index
            c_chap = self.card_chapters.get(c_idx, "Chapter 1")
            
            ch_query = urllib.parse.quote(c_chap)
            web_url = f"http://127.0.0.1:8000/index.html?card={c_idx}&chapter={ch_query}"
            
            if platform == 'android':
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(web_url))
                intent.setPackage("com.android.chrome")
                PythonActivity.mActivity.startActivity(intent)
                self.toast(f"📖 Opening Card {c_idx} ({c_chap}) in Chrome!")
            else:
                webbrowser.open(web_url)
        except Exception as e:
            err_trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(err_trace)
            self.toast(f"Play Err: {str(e)[:40]}")

    def switch_to_edit_screen_for(self, card_index):
        try:
            self.active_edit_card_index = card_index
            self.current_active_card_str = str(card_index)
            self.current_selected_chapter = self.card_chapters.get(card_index, "Chapter 1")
            
            self.character_name = self.card_names.get(card_index, "")
            self.character_rollplay = self.card_rolls.get(card_index, "")
            self.character_img_path = self.card_imgs.get(card_index, "")
            self.character_img_b_path = self.card_imgs_b.get(card_index, "")
            self.scene_image_1_path = self.card_scene_imgs.get(card_index, "")
            self.scene_image_2_path = self.card_scene_imgs_2.get(card_index, "")
            self.scene_bg_image_path = self.card_bgs.get(card_index, "")
            
            self.audio_file_path = ""
            self.text_command_a = ""
            self.text_command_b = ""

            self.root.current = 'edit_screen'
        except Exception as e:
            self.toast(f"Edit Switch Err: {str(e)[:30]}")

    def toast(self, msg):
        try:
            box = BoxLayout(padding=dp(8))
            box.add_widget(Label(text=f"[b]{msg}[/b]", markup=True, halign='center', font_size='11sp', color=(0.0, 0.88, 1.0, 1)))
            pop = Popup(title="Kora Comic Alert", content=box, size_hint=(0.8, 0.35), auto_dismiss=True)
            pop.open()
        except Exception as ex:
            print(f"Toast failed: {ex}")

if __name__ == '__main__':
    BlankKoraApp().run()
