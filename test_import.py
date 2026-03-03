#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入MainWindow
"""

import sys
print('Python version:', sys.version)
print('sys.path:', sys.path)

try:
    from ui.main_window import MainWindow
    print('MainWindow imported successfully')
except Exception as e:
    print('Import error:', e)
    import traceback
    traceback.print_exc()
