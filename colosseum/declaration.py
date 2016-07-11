from __future__ import print_function, absolute_import, division, unicode_literals

from .constants import *
from .exceptions import *


_CSS_PROPERTIES = []


def css_property(name, choices=None, default=None):
    "Define a simple CSS property attribute."
    def getter(self):
        return getattr(self, '_%s' % name, default)

    def setter(self, value):
        if value != getattr(self, '_%s' % name, default):
            if choices and value not in choices:
                raise InvalidCSSStyleException("Invalid value for CSS property '%s'; Valid values are: %s" % (
                    name,
                    ', '.join(s.replace('-', '_').upper() for s in choices))
                )
            setattr(self, '_%s' % name, value)
            self.dirty = True

    def deleter(self):
        try:
            delattr(self, '_%s' % name)
            self.dirty = True
        except AttributeError:
            # Attribute doesn't exist
            pass

    _CSS_PROPERTIES.append(name)
    return property(getter, setter, deleter)


def css_directional_property(name, default=0):
    "Define a CSS property attribute that defers to top/right/bottom/left alternatives."
    def getter(self):
        return (
            getattr(self, name % '_top', default),
            getattr(self, name % '_right', default),
            getattr(self, name % '_bottom', default),
            getattr(self, name % '_left', default),
        )

    def setter(self, value):
        try:
            if len(value) == 4:
                setattr(self, name % '_top', value[0])
                setattr(self, name % '_right', value[1])
                setattr(self, name % '_bottom', value[2])
                setattr(self, name % '_left', value[3])
            elif len(value) == 3:
                setattr(self, name % '_top', value[0])
                setattr(self, name % '_right', value[1])
                setattr(self, name % '_bottom', value[2])
                setattr(self, name % '_left', value[1])
            elif len(value) == 2:
                setattr(self, name % '_top', value[0])
                setattr(self, name % '_right', value[1])
                setattr(self, name % '_bottom', value[0])
                setattr(self, name % '_left', value[1])
            elif len(value) == 1:
                setattr(self, name % '_top', value[0])
                setattr(self, name % '_right', value[0])
                setattr(self, name % '_bottom', value[0])
                setattr(self, name % '_left', value[0])
            else:
                raise InvalidCSSStyleException("Invalid value for '%s'; value must be an number, or a 1-4 tuple." % (name % ''))
        except TypeError:
            setattr(self, name % '_top', value)
            setattr(self, name % '_right', value)
            setattr(self, name % '_bottom', value)
            setattr(self, name % '_left', value)

    def deleter(self):
        delattr(self, name % '_top')
        delattr(self, name % '_right')
        delattr(self, name % '_bottom')
        delattr(self, name % '_left')

    _CSS_PROPERTIES.append(name % '')
    _CSS_PROPERTIES.append(name % '_top')
    _CSS_PROPERTIES.append(name % '_right')
    _CSS_PROPERTIES.append(name % '_bottom')
    _CSS_PROPERTIES.append(name % '_left')
    return property(getter, setter, deleter)


class Declaration(object):
    def __init__(self, **style):
        self.measure = style.pop('measure', None)
        self.style(**style)

    ######################################################################
    # Style properties
    ######################################################################

    width = css_property('width')
    height = css_property('height')
    min_width = css_property('min_width')
    min_height = css_property('min_height')
    max_width = css_property('max_width')
    max_height = css_property('max_height')

    position = css_property('position', choices=set([RELATIVE, ABSOLUTE]), default=RELATIVE)
    top = css_property('top')
    bottom = css_property('bottom')
    left = css_property('left')
    right = css_property('right')

    flex_direction = css_property('flex_direction', choices=set([COLUMN, ROW]), default=COLUMN)
    flex_wrap = css_property('flex_wrap', choices=set([WRAP, NOWRAP]), default=NOWRAP)
    flex = css_property('flex')

    margin_top = css_property('margin_top', default=0)
    margin_right = css_property('margin_right', default=0)
    margin_bottom = css_property('margin_bottom', default=0)
    margin_left = css_property('margin_left', default=0)

    padding_top = css_property('padding_top', default=0)
    padding_right = css_property('padding_right', default=0)
    padding_bottom = css_property('padding_bottom', default=0)
    padding_left = css_property('padding_left', default=0)

    border_top_width = css_property('border_top_width', default=0)
    border_right_width = css_property('border_right_width', default=0)
    border_bottom_width = css_property('border_bottom_width', default=0)
    border_left_width = css_property('border_left_width', default=0)

    justify_content = css_property('justify_content', choices=set([FLEX_START, CENTER, FLEX_END, SPACE_BETWEEN, SPACE_AROUND]), default=FLEX_START)
    align_items = css_property('align_items', choices=set([FLEX_START, CENTER, FLEX_END, STRETCH]), default=STRETCH)
    align_self = css_property('align_self', choices=set([FLEX_START, CENTER, FLEX_END, STRETCH, AUTO]), default=AUTO)

    # Some special case meta-properties that defer to underlying top/bottom/left/right base properties
    margin = css_directional_property('margin%s')
    padding = css_directional_property('padding%s')
    border_width = css_directional_property('border%s_width')

    ######################################################################
    # Style manipulation
    ######################################################################

    def style(self, **styles):
        "Set multiple styles on the CSS definition."
        for style, value in styles.items():
            if not hasattr(self, style):
                raise UnknownCSSStyleException("Unknown CSS style '%s'" % style)
            setattr(self, style, value)

    def copy(self, source):
        for style in _CSS_PROPERTIES:
            setattr(self, style, getattr(source, style))