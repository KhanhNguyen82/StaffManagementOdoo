# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (c) 2025 tmistones.com
#
###################################################################################
import sys
import os

vendor_path = os.path.join(os.path.dirname(__file__), 'openai_vendor')
if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)

rarfile_path = os.path.join(os.path.dirname(__file__), 'rarfile')
if rarfile_path not in sys.path:
    sys.path.insert(0, rarfile_path)

from . import models
from . import wizards
from . import controllers

