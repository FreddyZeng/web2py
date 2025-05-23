#!/bin/python
# -*- coding: utf-8 -*-

"""
    Unit tests for gluon.serializers
"""

import datetime
import decimal
import unittest

from gluon.html import SPAN
# careful with the import path 'cause of isinstance() checks
from gluon.languages import TranslatorFactory
from gluon.serializers import *
from gluon.storage import Storage

from .fix_path import fix_sys_path


class TestSerializers(unittest.TestCase):
    def testJSON(self):
        # the main and documented "way" is to use the json() function
        # it has a few corner-cases that make json() be somewhat
        # different from the standard buyt being compliant
        # it's just a matter of conventions

        # incompatible spacing, newer simplejson already account
        # for this but it's still better to remember
        weird = {"JSON": "ro" + "\u2028" + "ck" + "\u2029" + "s!"}
        rtn = json(weird)
        self.assertEqual(rtn, '{"JSON": "ro\\u2028ck\\u2029s!"}')
        # date, datetime, time strictly as strings in isoformat, minus the T
        objs = [
            datetime.datetime(2014, 1, 1, 12, 15, 35),
            datetime.date(2014, 1, 1),
            datetime.time(12, 15, 35),
        ]
        iso_objs = [obj.isoformat()[:19].replace("T", " ") for obj in objs]
        json_objs = [json(obj) for obj in objs]
        json_web2pyfied = [json(obj) for obj in iso_objs]
        self.assertEqual(json_objs, json_web2pyfied)
        # int or long int()ified
        # self.assertEqual(json(1), json(1))
        # decimal stringified
        obj = {"a": decimal.Decimal("4.312312312312")}
        self.assertEqual(json(obj), '{"a": 4.312312312312}')
        # lazyT translated
        T = TranslatorFactory("", "en")
        lazy_translation = T("abc")
        self.assertEqual(json(lazy_translation), '"abc"')
        # html helpers are xml()ed before too
        self.assertEqual(json(SPAN("abc"), cls=None), '"<span>abc</span>"')
        self.assertEqual(
            json(SPAN("abc")), '"\\u003cspan\\u003eabc\\u003c/span\\u003e"'
        )
        # unicode keys make a difference with loads_json
        base = {"è": 1, "b": 2}
        base_enc = json(base)
        base_load = loads_json(base_enc)
        self.assertEqual(base, base_load)
        # if unicode_keys is false, the standard behaviour is assumed
        base_load = loads_json(base_enc, unicode_keys=False)
        self.assertEqual(base, base_load)
