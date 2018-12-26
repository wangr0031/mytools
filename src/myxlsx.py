#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wangrong'

import xlrd
import xlwt
import os, re
from lib.logger_def import logger


class myxlsx(object):
    def __init__(self, src_path):
        if src_path[-1] == '/':
            src_path = src_path[:-1]

        self.src_file_list = self.list_all_files(src_path, match_postfix=['.xlsx'])

    # 去除空格，空值
    def remove_empty_from_list(self, list_object):
        if list_object is None:
            return list_object
        else:
            while [] in list_object:
                list_object.remove([])
            while '' in list_object:
                list_object.remove('')
            return list_object

    def list_all_files(self, list_dir, skip_file=None, match_postfix=None):
        all_file_list = []
        skip_file_list = []
        list_dir = list_dir.replace('\\', '/')
        if os.path.isfile(list_dir):
            all_file_list.append(list_dir)
        elif os.path.isdir(list_dir):
            ##skip_file & match_postfix格式规整，去除空值，空格等无效数据
            match_postfix = self.remove_empty_from_list(match_postfix)
            skip_file = self.remove_empty_from_list(skip_file)
            for dirpath, dirnames, filenames in os.walk(list_dir):
                for file in filenames:
                    if match_postfix:
                        # match_postfix=self.remove_empty_from_list(match_postfix)
                        if os.path.splitext(file)[1] in match_postfix:
                            if skip_file:
                                # skip_file = self.remove_empty_from_list(skip_file)
                                for skip_key in skip_file:
                                    if not re.search(skip_key, file.lower()):
                                        fullfile = (dirpath + '/' + file).replace('\\', '/')
                                        all_file_list.append(fullfile)
                                    else:
                                        fullfile = (dirpath + '/' + file).replace('\\', '/')
                                        skip_file_list.append(fullfile)
                            else:
                                fullfile = (dirpath + '/' + file).replace('\\', '/')
                                all_file_list.append(fullfile)
                    else:
                        if skip_file:
                            # skip_file = self.remove_empty_from_list(skip_file)
                            for skip_key in skip_file:
                                if not re.search(skip_key, file.lower()):
                                    fullfile = (dirpath + '/' + file).replace('\\', '/')
                                    all_file_list.append(fullfile)
                                else:
                                    fullfile = (dirpath + '/' + file).replace('\\', '/')
                                    skip_file_list.append(fullfile)
                        else:
                            fullfile = (dirpath + '/' + file).replace('\\', '/')
                            all_file_list.append(fullfile)

        return all_file_list

    def open_xlsx(self, xlsx_name):
        try:
            xh = xlrd.open_workbook(xlsx_name)
            return xh
        except Exception as err:
            logger.error('open file: [{}] error, error msg: [{}]'.format(xlsx_name, err))
            return False

    # TODO: read xlsx sheet data
    def read_data(self, xlsx_handle, sheet_name, read_rows=None):
        pass

    # TODO: read specified sheet

    # TODO: write data
