#!/usr/bin/env bash

# 输出蓝色分隔线
echo -e "\033[34m-------------------wsgi process-------------------\033[0m"

# 查找包含nb_uwsgi.ini的进程，排除grep自身
ps -ef|grep nb_uwsgi.ini | grep -v grep

# 暂停0.5秒
sleep 0.5

# 输出即将关闭的提示
echo -e '\n-----------------going to close-------------------'

# 查找包含nb_uwsgi.ini的进程，排除grep自身，获取进程ID并强制杀死
ps -ef | grep nb_uwsgi.ini | grep -v grep | awk '{print $2}' | xargs kill -9