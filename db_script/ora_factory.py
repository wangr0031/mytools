#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'wangrong'

import cx_Oracle
import yaml
import os, sys
from myfunc.logger_def import logger


class ConfigFactory:
    def __init__(self, cfg_path):
        self.cfg_path = cfg_path
        if not os.path.exists(self.cfg_path):
            logger.error('file: [{}] not found'.format(self.cfg_path))
            exit()

    def get_settings(self):
        with open(self.cfg_path, 'rt') as f:
            ora_setting = yaml.safe_load(f.read())
        return ora_setting
        # print (self.ora_setting)


class OracleExecFactory:
    def __init__(self, host, port, sid, username, password, mode=None):
        self.db = self.make_ora_connect(host, port, sid, username, password, mode)

    def make_ora_connect(self, host, port, sid, username, password, mode=None):
        try:
            ora_dsn = cx_Oracle.makedsn(host, port, sid)
            if mode is not None:
                ora_db = cx_Oracle.connect(username, password, dsn=ora_dsn, mode=mode)
            else:
                ora_db = cx_Oracle.connect(username, password, dsn=ora_dsn)
            return ora_db
        except cx_Oracle.DatabaseError as exce:
            error, = exce.args
            logger.error(
                "username: [{}], password: [{}], dsn: [{}], Oracle-Error-Code:{}".format(username, password, ora_dsn,
                                                                                         error.code))
            logger.error("Oracle-Error-Message:{}", error.message)

    def select_db(self, sql, numRows=None):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            if numRows is not None:
                res_msg = cursor.fetchmany(numRows=numRows)
            else:
                res_msg = cursor.fetchall()
            cursor.close()
            return res_msg
        except cx_Oracle.DatabaseError as exce:
            error, = exce.args
            logger.error("sql statment: [{}], Oracle-Error-Code:{}".format(sql, error.code))
            logger.error("Oracle-Error-Message:{}", error.message)
            cursor.close()
            exit()

    def ddl_db(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            cursor.close()
        except cx_Oracle.DatabaseError as exce:
            error, = exce.args
            logger.error("sql statment: [{}], Oracle-Error-Code:{}".format(sql, error.code))
            logger.error("Oracle-Error-Message:{}", error.message)
            cursor.close()

    def dml_db(self, sql):
        try:
            cursor = self.db.cursor()

            if isinstance(sql, str):
                cursor.execute(sql)
            elif isinstance(sql, list):
                rownum = 1
                for onesql in sql:
                    onesql = onesql.strip()
                    cursor.execute(onesql)
                    rownum += 1
                    if rownum >= 500:
                        self.db.commit()

            cursor.close()
            self.db.commit()
        except cx_Oracle.DatabaseError as exce:
            error, = exce.args
            logger.error("sql statment: [{}], Oracle-Error-Code:".format(sql, error.code))
            logger.error("Oracle-Error-Message:{}", error.message)
            self.db.rollback()
            cursor.close()
