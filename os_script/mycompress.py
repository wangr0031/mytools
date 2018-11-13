#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wangrong'
import zipfile, os, re


class mycompress(object):
    def __init__(self, src_path, dest_path):
        src_path = src_path.replace('\\', '/')
        dest_path = dest_path.replace('\\', '/')
        if src_path[-1] == '/':
            self.src_path = src_path[:-1]
        else:
            self.src_path = src_path

        if dest_path[-1] == '/':
            self.dest_path = dest_path[:-1]
        else:
            self.dest_path = dest_path
        if not os.path.exists(self.dest_path):
            os.makedirs(self.dest_path)

    def is_correct_zip_file(self, zip_instance):
        res = zip_instance.testzip()
        if res is None:
            return True
        else:
            return False

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

    def compress_files(self, need_zip_object, need_current_dir='Y'):
        dirname, filename = os.path.split(need_zip_object)
        fname, fename = os.path.splitext(filename)
        zipfilename = self.dest_path + '/' + fname + '.zip'
        print("压缩文件路径：", zipfilename)
        azip = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
        all_list = self.list_all_files(need_zip_object)
        for onefile in all_list:
            in_zip_file = onefile.replace(self.src_path, '')
            azip.write(onefile, in_zip_file)
        azip.close()
        # print (all_list)

    def main_process(self):
        if os.path.isfile(self.src_path):
            print("输入路径【{}】为文件，无法处理".format(self.src_path))
        elif os.path.isdir(self.src_path):
            all_objects = os.listdir(self.src_path)
            # print (self.src_path)
            # print (all_objects)
            for one in all_objects:
                one_object = self.src_path + '/' + one
                self.compress_files(one_object)


if __name__ == '__main__':
    a = mycompress(r'C:\Users\cc\Desktop\tmp\dirs', r'C:\Users\cc\Desktop\tmp\zip')
    a.main_process()
