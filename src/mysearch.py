#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wangrong'
import re
import os
from lib.logger_def import logger


class mysearch(object):
    def __init__(self, src_path, search_key):
        self.match_keys = list()
        src_path = src_path.replace('\\', '/')
        if src_path[-1] == '/':
            self.src_path = src_path[:-1]
        else:
            self.src_path = src_path
        if isinstance(search_key, str):
            self.match_keys = search_key.upper()
        elif isinstance(search_key, list):
            for onekey in search_key:
                self.match_keys.append(onekey.upper())

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

    # 支持按文件后缀匹配和过滤文件
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

    def search(self):
        all_list = self.list_all_files(self.src_path)
        for one_file in all_list:
            fh = open(one_file, mode='r+t', encoding='utf-8')
            try:
                text_lines = fh.readlines()
                row = 1
                for one_line in text_lines:
                    for match_key in self.match_keys:
                        if re.search(match_key, one_line):
                            logger.info('file: [{}], lines: [{}] match the key: {} '.format(one_file, row, match_key))
                            logger.debug('match row content: [{}]'.format(one_line))
                            # print('file: [{}], lines: [{}] match the key: {} '.format(match_key, one_file, row))

                    row += 1
            except Exception as err:
                logger.error('skip file: {}, \n error: {}'.format(one_file, err))
                # print('[Warning]skip file: {}, error: {}'.format(err, one_file))
            finally:
                fh.close()


if __name__ == '__main__':
    a = mysearch(r'C:\Users\cc\Desktop\tmp\20181130\20181130', ['TAB_POS', 'TAB_BTC', 'IDX_POS', 'IDX_BTC'])
    a.search()
