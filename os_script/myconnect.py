#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wangrong'

import paramiko
from myfunc.logger_def import logger
import os, re
from stat import *
from time import sleep


class myconnect(object):
    def __init__(self, host, username, password=None, port=22):
        self.server_ip_address = host
        self.server_username = username
        if password is None:
            self.server_password = username
        elif password.strip() == '':
            self.server_password = username
        else:
            self.server_password = password

        self.server_port = port
        # transport,channel
        # self.connections=[]
        # 重试次数
        self.try_times = 3
        self.connect_server()

    def connect_server(self):
        while True:
            try:
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(hostname=self.server_ip_address, port=self.server_port, username=self.server_username,
                                 password=self.server_password)
                logger.info('Connect server :{} Success'.format(self.server_ip_address))
                # print('Connect server :{} Success'.format(self.server_ip_address))
                return
            except Exception as err:
                if self.try_times != 0:
                    logger.warn('Connect failed, Begin to retry [{}]...'.format(4 - self.try_times))
                    # print('Connect failed, Begin to retry ...')
                    self.try_times -= 1
                else:
                    logger.error(
                        'Retry {0} times, Catch an error {1}, Skip connect to {2} !'.format(self.try_times, err,
                                                                                            self.server_ip_address))
                    # print('Retry {0} times, Catch an error {1}, Skip connect to {2} !'.format(self.try_times, err,
                    #                                                                           self.server_ip_address))
                    break

    def close_server(self):
        logger.info('disconnect from [{}]'.format(self.server_ip_address))
        self.ssh.close()

    def exec_commands(self, cmd_str):
        '''
        :param exec_cmd: 需要执行的命令(单个命令)
        :return:
        '''
        if not isinstance(cmd_str, str):
            logger.error("Only suppoort commands in one string")
            # print("Only suppoort commands in one string")
            exit()
        # ssh = paramiko.SSHClient()
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # ssh.connect(hostname=self.server_ip_address, port=self.server_port, username=self.server_username,
        #             password=self.server_password)
        exec_cmd = 'source .bash_profile || source .profile;' + cmd_str
        logger.info('run cmd: {}'.format(cmd_str))
        stdin, stdout, stderr = self.ssh.exec_command(exec_cmd)
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        logger.debug("[%s]".center(50, "-") % self.server_ip_address)
        # print("[%s]".center(50, "-") % self.server_ip_address)
        logger.info('[{}] status: {}'.format(self.server_ip_address, 'cmd executed'))
        # print('run cmd: {}'.format(cmd_str))
        logger.debug(result.decode())
        # print(result.decode())
        # self.ssh.close()

    def format_output(self, output_buf, cmd_str):
        # print (type(output_buf))
        output_format_buf = ''

        for oneline in output_buf.splitlines():
            oneline = oneline.strip() + '\n'
            if oneline == '\n':
                continue
            elif re.search(cmd_str, oneline):
                continue
            output_format_buf += oneline
        return output_format_buf

    def exec_multi_commands(self, cmd_list, recv_bytes=1024):
        shell_cmd = self.ssh.invoke_shell()

        for one_cmd in cmd_list:
            logger.info('[{}] run: {}'.format(self.server_ip_address, one_cmd))
            # print ('[{}] run: {}'.format(self.server_ip_address,one_cmd))
            shell_cmd.send(one_cmd + '\n')
            receive_buf = ''
            while True:
                sleep(0.5)
                # print (shell_cmd.recv(recv_bytes))
                result = shell_cmd.recv(recv_bytes).decode('utf-8')
                receive_buf += result
                if len(result) != recv_bytes:
                    receive_buf = self.format_output(receive_buf, one_cmd)
                    logger.debug(receive_buf)
                    logger.info('[{}] status: {}'.format(self.server_ip_address, 'cmd executed'))
                    # print (receive_buf)
                    break
            # sleep(0.5)
            # receive_buf=shell_cmd.recv(1024).decode('utf-8')
            # print ('[{}] out: {}'.format(self.server_ip_address,receive_buf))

    def __get_all_files_in_remote_dir(self, sftp, remote_dir):
        all_files = list()
        file_stat = sftp.lstat(remote_dir)
        if S_ISREG(file_stat.st_mode):
            all_files.append(remote_dir)
        elif S_ISDIR(file_stat.st_mode):
            if remote_dir[-1] == '/':
                remote_dir = remote_dir[:-1]

            files = sftp.listdir_attr(remote_dir)
            for x in files:
                filename = remote_dir + '/' + x.filename
                if S_ISDIR(x.st_mode):
                    all_files.extend(self.__get_all_files_in_remote_dir(sftp, filename))
                else:
                    all_files.append(filename)
        return all_files

    def __trunc_prefix_path(self, prefix_path, src_path):
        match_instace = re.match(prefix_path, src_path)
        src_path = src_path[match_instace.end() + 1:]
        return src_path

    def __makedirs_if_not_exist(self, full_path, sftp_instacne=None):
        if sftp_instacne is None:
            try:
                if not os.path.exists(full_path):
                    os.makedirs(full_path)
            except Exception as error:
                logger.error("create directory [{}] error! {}".format(full_path, error))
                # print("create directory [{}] error! {}".format(full_path, error))
        else:
            try:
                file_stat = sftp_instacne.lstat(full_path)
            except Exception as err:
                sftp_instacne.mkdir(full_path)

    def get_file(self, src_path, dest_path):
        '''
        :param src_path: 远端目录
        :param dest_path: 本地目录
        :return:
        '''
        if src_path[-1] == '/':
            src_path = src_path[:-1]
        if dest_path[-1] == '/':
            dest_path = dest_path[:-1]
        src_path = src_path.replace('\\', '/')
        dest_path = dest_path.replace('\\', '/')
        self.__makedirs_if_not_exist(dest_path)
        try:
            transport = paramiko.Transport((self.server_ip_address, self.server_port))
            transport.connect(username=self.server_username, password=self.server_password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            all_files = self.__get_all_files_in_remote_dir(sftp, src_path)
            for full_file_path in all_files:
                # filename = os.path.split(full_file_path)[1]
                # filepath = os.path.split(full_file_path)[0]
                prefix_dir_path = os.path.dirname(src_path)
                relative_path = self.__trunc_prefix_path(prefix_dir_path, full_file_path)
                dest_full_path = dest_path + '/' + relative_path
                dest_dir_path = os.path.dirname(dest_full_path)
                self.__makedirs_if_not_exist(dest_dir_path)
                # dest_full_path = dest_full_path.replace('\\', '/')
                logger.info('[{}] get: {} to [Local]: {}'.format(self.server_ip_address, src_path, dest_full_path))
                # print(
                #     '[{}] get: {} to [Local]: {}'.format(self.server_ip_address,src_path,dest_full_path)
                #     )
                sftp.get(full_file_path, dest_full_path)
        except Exception as error:
            logger.error("Get File ERR: [{}] [{}]".format(self.server_ip_address, error))
            # print("Get File ERR: [{}] [{}]".format(self.server_ip_address, error))

    def __get_all_files_in_local_dir(self, local_dir):
        all_files = list()
        files = os.listdir(local_dir)
        for x in files:
            filename = os.path.join(local_dir, x)
            filename = filename.replace('\\', '/')
            if os.path.isdir(filename):
                all_files.extend(self.__get_all_files_in_local_dir(filename))
            else:
                all_files.append(filename)
        return all_files

    def put_file(self, src_path, dest_path):
        '''
        :param src_path: 本地目录
        :param dest_path: 对端目录
        :return:
        '''
        if src_path[-1] == '/':
            src_path = src_path[:-1]
        if dest_path[-1] == '/':
            dest_path = dest_path[:-1]
        src_path = src_path.replace('\\', '/')
        dest_path = dest_path.replace('\\', '/')
        try:
            transport = paramiko.Transport((self.server_ip_address, self.server_port))
            transport.connect(username=self.server_username, password=self.server_password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            if os.path.isfile(src_path):
                filename = os.path.split(src_path)[1]
                dest_full_path = dest_path + '/' + filename
                logger.info('[Local] put: {} to [{}]: {}'.format(src_path, self.server_ip_address, dest_full_path))
                # print(
                #     '[Local] put: {} to [{}]: {}'.format(src_path,self.server_ip_address,dest_full_path)
                #     )
                sftp.put(src_path, dest_full_path)
            else:
                all_files = self.__get_all_files_in_local_dir(src_path)
                for full_file_path in all_files:
                    prefix_dir_path = os.path.dirname(src_path)
                    relative_path = self.__trunc_prefix_path(prefix_dir_path, full_file_path)
                    dest_full_path = dest_path + '/' + relative_path
                    dest_dir_path = os.path.dirname(dest_full_path)
                    self.__makedirs_if_not_exist(dest_dir_path, sftp)

                    logger.info('[Local] put: {} to [{}]: {}'.format(
                        full_file_path,
                        self.server_ip_address,
                        dest_full_path))

                    # print(
                    #     '[Local] put: {} to [{}]: {}'.format(
                    #         full_file_path,
                    #         self.server_ip_address,
                    #         dest_full_path))
                    sftp.put(full_file_path, dest_full_path)
        except Exception as error:
            logger.error("Put File ERR: [{}] [{}]".format(self.server_ip_address, error))
            # print("Put File ERR: [{}] [{}]".format(self.server_ip_address, error))


if __name__ == '__main__':
    a = myconnect('172.16.80.61', 'oracle')
    # a.connect_server()
    # a.send_cmd('expdp system/system schemas=VCOFF DIRECTORY=my_expdata DUMPFILE=VCOFF1.dmp logfile=exp_VCOFF1.log')
    # a.connect_close()
    # a.exec_command('sqlplus -s / as sysdba <<! \n select * from dual; \n !')
    a.exec_multi_commands(['cd clean', 'ls -l'])
    a.close_server()
    # a.exec_command('echo $PATH')
    # a.put_file(r'C:\Users\cc\Desktop\tmp\clean', '/oracle/tmp')
    # a.exec_command('export ORACLE_SID=123;echo $ORACLE_SID')
    # a.exec_command('echo $ORACLE_SID')
