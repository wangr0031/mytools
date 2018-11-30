#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wangrong'
import logging.config
import os
import yaml

'''
setup logging configuration
'''
log_conf = os.path.dirname(os.path.dirname(__file__)) + '/CONFIG/log.cfg'
if not os.path.exists("./mytools/logs"):
    os.mkdir('./mytools/logs')

if os.path.exists(log_conf):
    with open(log_conf, 'rt') as f:
        config = yaml.safe_load(f.read())
        # print (config)
    logging.config.dictConfig(config)
else:
    logging.basicConfig(level=logging.INFO)
    print('[ERR]The logging config file [%s] not exist', log_conf)

logger = logging.getLogger()
