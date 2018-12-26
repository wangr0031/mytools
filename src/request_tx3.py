#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wangrong'

import requests

# http://bang.tx3.163.com/bang/role/21_10885
url = 'http://bang.tx3.163.com/bang/ranks?school=2&order_key=equ_xiuwei&server='
r = requests.post(url)
print(r.text)
