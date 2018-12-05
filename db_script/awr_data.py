#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wangrong'

from myfunc.logger_def import logger
import os, datetime
from db_script.ora_factory import ConfigFactory, OracleExecFactory


class OracleAwr:

    def __init__(self):
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'CONFIG', 'ora_setting_awr.yml')
        cfg_data = ConfigFactory(cfg_path).get_settings()
        if cfg_data['database_type'] != 'ORACLE':
            logger.error('database type: [{}] not support'.format(cfg_data['database_type']))
            exit()
        self.db_config = cfg_data['database_setting']
        self.awr_sql = cfg_data['database_awr_sql']
        self.awr_interval_time = cfg_data['awr_interval_time']
        logger.debug('self.db_config={}'.format(self.db_config))

    def get_single_db_info(self, db_map):
        try:
            host = db_map['db_url'].split(':')[0]
            listen_port = db_map['db_url'].split(':')[1]
            service_name = db_map['db_url'].split(':')[2]
            db_username = db_map['db_username']
            db_password = db_map['db_password']
            return host, listen_port, service_name, db_username, db_password
        except Exception as err:
            logger.error('error: {}'.format(err))

    def make_single_awr(self, db, dbid, inst_num, bid, eid, filename):
        one_awr_report_html_sql = self.awr_sql['awr_report_html']
        awr_report_html_sql = one_awr_report_html_sql.format(dbid, inst_num, bid, eid)
        filepath = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'awr', filename))
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        logger.info('make awr report: {}'.format(filepath))
        res = db.select_db(awr_report_html_sql)
        for oneline in res:
            newline = oneline[0]
            if newline is None:
                newline = '\n'

            try:
                fh = open(filepath, 'ab+')
                newline = newline.encode('utf-8')
                fh.write(newline)
            except Exception as err:
                print("err:", oneline)
                print(err)
            finally:
                fh.close()

    def isEmptyValue(self, list_object):
        if list_object is None:
            list_object = 0
            return list_object
        else:
            while [] in list_object:
                list_object.remove([])
            while '' in list_object:
                list_object.remove('')
            return list_object

    def get_awr_element(self, db, start_str, end_str):
        one_snap_id_sql = self.awr_sql['awr_snap_id']
        one_db_id_sql = self.awr_sql['awr_db_id']
        res = db.select_db(one_db_id_sql, 1)
        db_id = res[0][0]
        logger.debug('db_id: {}'.format(db_id))
        one_instance_number_sql = self.awr_sql['awr_instance_number']
        res = db.select_db(one_instance_number_sql, 1)
        inst_num = res[0][0]
        logger.debug('inst_num: {}'.format(inst_num))
        if start_str is not None:
            start_snap_id_sql = one_snap_id_sql.format(start_str)
            res = db.select_db(start_snap_id_sql, 1)
            res = self.isEmptyValue(res)
            bid = res[0][0]
            logger.debug('bid: {}'.format(bid))
        if end_str is not None:
            end_snap_id_sql = one_snap_id_sql.format(end_str)
            res = db.select_db(end_snap_id_sql, 1)
            res = self.isEmptyValue(res)
            eid = res[0][0]
            logger.debug('eid: {}'.format(eid))

        return db_id, inst_num, bid, eid

    def isVaildDate(self, date_str):
        try:
            if ":" in date_str:
                datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            else:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except:
            return False

    def format_date(self, date_str):
        if ":" in date_str:
            date_time = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        else:
            date_time = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return date_time

    def main_process(self, collect_date):
        rescode = self.isVaildDate(collect_date)
        if not rescode:
            logger.error('invaild date: {}'.format(collect_date))
            exit()
        for onekey in self.db_config:
            onerow = self.db_config[onekey]
            logger.info(onerow)
            (host, listen_port, service_name, db_username, db_password) = self.get_single_db_info(onerow)
            ora = OracleExecFactory(host, listen_port, service_name, db_username, db_password)
            col_date = self.format_date(collect_date)
            start_date = col_date
            end_date = col_date
            flag = True
            while start_date.strftime("%Y-%m-%d") == end_date.strftime("%Y-%m-%d") and flag:
                cur_date = datetime.datetime.now() + datetime.timedelta(hours=-1)
                start_date = end_date
                end_date = end_date + datetime.timedelta(hours=self.awr_interval_time)
                start_str = start_date.strftime("%Y%m%d%H")
                end_str = end_date.strftime("%Y%m%d%H")
                if end_date < cur_date:
                    (db_id, inst_num, bid, eid) = self.get_awr_element(ora, start_str, end_str)
                    filename = 'awrrpt_{}_{}_{}_{}-{}.html'.format(host, service_name, start_date.strftime("%Y%m%d"),
                                                                   start_str, end_str)
                    logger.info('db_id: {}, inst_num: {}, bid: {}, eid: {}'.format(db_id, inst_num, bid, eid))
                    self.make_single_awr(ora, db_id, inst_num, bid, eid, filename)
                else:
                    end_str = cur_date.strftime("%Y%m%d%H")
                    flag = False
                    if start_str != end_str:
                        (db_id, inst_num, bid, eid) = self.get_awr_element(ora, start_str, end_str)
                        filename = 'awrrpt_{}_{}_{}_{}-{}.html'.format(host, service_name,
                                                                       start_date.strftime("%Y%m%d"),
                                                                       start_str, end_str)
                        logger.info('db_id: {}, inst_num: {}, bid: {}, eid: {}'.format(db_id, inst_num, bid, eid))
                        self.make_single_awr(ora, db_id, inst_num, bid, eid, filename)
                    else:
                        break


if __name__ == '__main__':
    a = OracleAwr()
    a.main_process('2018-12-5')
