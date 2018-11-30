#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wangrong'
import cx_Oracle
import os, sys


class OraDataExport(object):
    def __init__(self, ora_server_ip, ora_server_username='oracle', ora_server_password='oracle'):
        self.ora_ip = ora_server_ip
        self.username = ora_server_username
        self.password = ora_server_password

    def pre_export_data(self):
        pass

    def export_ora_data(self):
        pass

    def pos_export_data(self):
        pass

    def export_data(self):
        pass
