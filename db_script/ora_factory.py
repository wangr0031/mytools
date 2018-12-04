#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'wangrong'

import cx_Oracle
import os, sys


class ConfigFactory:
    pass

class OracleAwrFactory:
    # todo: 使用@property从config文件中获取属性，需要新增一个configfactory类，用来处理config文件
    def __init__(self,db_config):
        self.db_config=db_config