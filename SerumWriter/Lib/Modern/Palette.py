#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""QRainbowStyle default palette."""

# Standard library imports
from collections import OrderedDict

# package imports
from SerumWriter.Lib.Modern.ColorSystem import *


class BasePalette:
    """Base class for palettes."""

    # Color
    COLOR_BACKGROUND_1 = ''
    COLOR_BACKGROUND_2 = ''
    COLOR_BACKGROUND_3 = ''
    COLOR_BACKGROUND_4 = ''
    COLOR_BACKGROUND_5 = ''
    COLOR_BACKGROUND_6 = ''

    COLOR_TEXT_1 = ''
    COLOR_TEXT_2 = ''
    COLOR_TEXT_3 = ''
    COLOR_TEXT_4 = ''

    COLOR_ACCENT_1 = ''
    COLOR_ACCENT_2 = ''
    COLOR_ACCENT_3 = ''
    COLOR_ACCENT_4 = ''
    COLOR_ACCENT_5 = ''

    OPACITY_TOOLTIP = 0

    # Size
    SIZE_BORDER_RADIUS = '4px'

    # Borders
    BORDER_1 = '1px solid $COLOR_BACKGROUND_1'
    BORDER_2 = '1px solid $COLOR_BACKGROUND_4'
    BORDER_3 = '1px solid $COLOR_BACKGROUND_6'

    BORDER_SELECTION_3 = '1px solid $COLOR_ACCENT_3'
    BORDER_SELECTION_2 = '1px solid $COLOR_ACCENT_2'
    BORDER_SELECTION_1 = '1px solid $COLOR_ACCENT_1'

    TITLEBAR_BOTTOM_BORDER = ''
    TITLE_BAR_BACKGROUND_COLOR = COLOR_ACCENT_3
    TITLE_BAR_BUTTONS_HOVER_COLOR = COLOR_ACCENT_4
    TITLE_BAR_BUTTONS_DISABLED_COLOR = COLOR_ACCENT_1
    TITLE_BAR_TEXT_COLOR = COLOR_TEXT_1

    # Paths
    PATH_RESOURCES = "':/qss_icons'"

    @classmethod
    def to_dict(cls, colors_only=False):
        """Convert variables to dictionary."""
        order = [
            'COLOR_BACKGROUND_6',
            'COLOR_BACKGROUND_5',
            'COLOR_BACKGROUND_4',
            'COLOR_BACKGROUND_2',
            'COLOR_BACKGROUND_3',
            'COLOR_BACKGROUND_1',
            'COLOR_TEXT_1',
            'COLOR_TEXT_2',
            'COLOR_TEXT_3',
            'COLOR_TEXT_4',
            'COLOR_ACCENT_1',
            'COLOR_ACCENT_2',
            'COLOR_ACCENT_3',
            'COLOR_ACCENT_4',
            'COLOR_ACCENT_5',
            'OPACITY_TOOLTIP',
            'SIZE_BORDER_RADIUS',
            'BORDER_1',
            'BORDER_2',
            'BORDER_3',
            'BORDER_SELECTION_3',
            'BORDER_SELECTION_2',
            'BORDER_SELECTION_1',
            'TITLEBAR_BOTTOM_BORDER',
            'TITLE_BAR_BACKGROUND_COLOR',
            'TITLE_BAR_BUTTONS_HOVER_COLOR',
            'TITLE_BAR_BUTTONS_DISABLED_COLOR',
            'TITLE_BAR_TEXT_COLOR',
            'PATH_RESOURCES',
        ]
        dic = OrderedDict()
        for var in order:
            value = getattr(cls, var)

            if colors_only:
                if not var.startswith('COLOR'):
                    value = None

            if value:
                dic[var] = value

        return dic

    @classmethod
    def color_palette(cls):
        """Return the ordered colored palette dictionary."""
        return cls.to_dict(colors_only=True)


class Dark(BasePalette):
    
    COLOR_BACKGROUND_1 = "#1a1a1a"
    COLOR_BACKGROUND_2 = "#181818"
    COLOR_BACKGROUND_3 = "#282828"
    COLOR_BACKGROUND_4 = "#393939" 
    COLOR_BACKGROUND_5 = "#3E3E3E" 
    COLOR_BACKGROUND_6 = "#535353"

    COLOR_TEXT_1 = Gray.B120
    COLOR_TEXT_2 = Gray.B130
    COLOR_TEXT_3 = Gray.B140
    COLOR_TEXT_4 = Gray.B150
    
    COLOR_ACCENT_1 = "#ce4b01"
    COLOR_ACCENT_2 = "#d66522"
    COLOR_ACCENT_3 = "#de8044"
    COLOR_ACCENT_4 = "#e79b65"
    COLOR_ACCENT_5 = "#efb587"

    TITLEBAR_BOTTOM_BORDER = '#1f1f1f'
    TITLE_BAR_BACKGROUND_COLOR = COLOR_BACKGROUND_1
    TITLE_BAR_BUTTONS_HOVER_COLOR = "#3f3e3e"
    TITLE_BAR_BUTTONS_DISABLED_COLOR = COLOR_BACKGROUND_4
    TITLE_BAR_TEXT_COLOR = '#bdae93'


class Light(BasePalette):
    
    COLOR_BACKGROUND_1 = "#e5e5e5"
    COLOR_BACKGROUND_2 = "#dbdbdb"
    COLOR_BACKGROUND_3 = "#d7d7d7"
    COLOR_BACKGROUND_4 = "#c6c6c6" 
    COLOR_BACKGROUND_5 = "#c1c1c1" 
    COLOR_BACKGROUND_6 = "#acacac"

    COLOR_TEXT_1 = '#312e2b'
    COLOR_TEXT_2 = '#1f1e1c'
    COLOR_TEXT_3 = '#050505'
    COLOR_TEXT_4 = '#000000'
    
    COLOR_ACCENT_1 = "#ce4b01"
    COLOR_ACCENT_2 = "#d66522"
    COLOR_ACCENT_3 = "#de8044"
    COLOR_ACCENT_4 = "#e79b65"
    COLOR_ACCENT_5 = "#efb587"

    TITLEBAR_BOTTOM_BORDER = '#e0e0e0'
    TITLE_BAR_BACKGROUND_COLOR = COLOR_BACKGROUND_1
    TITLE_BAR_BUTTONS_HOVER_COLOR = "#c0c1c1"
    TITLE_BAR_BUTTONS_DISABLED_COLOR = COLOR_BACKGROUND_4
    TITLE_BAR_TEXT_COLOR = '#312e2b'