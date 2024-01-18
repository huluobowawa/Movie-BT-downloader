import os
import threading
import time
import signal

from flask import Flask, render_template
from flask_socketio import SocketIO

import pachong
from log import *

app = Flask(__name__)
socketio = SocketIO(app)
thread = None
pid = os.getpid() # 获取当前进程的PID


# 读取日志文件
def read_log_file():
    """
    读取日志文件的函数

    Returns:
        str: 日志文件的内容
    """
    with open(log_file_path, "r") as file:
        return file.read()


# 主页路由
@app.route('/')
def index():
    """
    渲染主页

    从日志文件中读取内容
    并将其传递给index.html模板进行渲染
    """
    log_content = read_log_file()
    return render_template('index.html', log_content=log_content)


# 后台线程函数
def background_thread():
    while True:  # 当True时循环执行以下代码
        time.sleep(0.1)  # 程序休眠1秒
        log_content = read_log_file()  # 读取日志文件内容
        status_info = "爬虫正在运行" if pachong.run_status else "爬虫未运行"
        socketio.emit('updated_variable2', status_info)
        socketio.emit('update_log', log_content)  # 发送"update_log"事件，传递log_content作为数据


# 爬虫线程函数
def pc_thread():
    # 创建一个线程对象pc
    pc = threading.Thread(target=pachong.run)
    ht = threading.Thread(target=background_thread)
    # 启动线程
    logging.debug("爬虫主线程启动中...")
    pc.start()
    logging.debug("后台主线程启动中...")
    ht.start()


# 启动爬虫
@socketio.on('start_pachong')
def start_pachong():
    logging.debug("单击爬虫启动按钮...")
    if pachong.run_status:  # 如果pachong的运行状态为True
        return  # 直接返回，不执行后续代码
    else:
        pachong.run_status = True  # 将pachong的运行状态设置为True
        # 添加开始记录进程的代码
        pachong.logger.info("爬虫启动中...")  # 记录日志，提示爬虫正在启动


# 停止爬虫
@socketio.on('stop_pachong')
def stop_logging():
    logging.debug("单击爬虫关闭按钮...")
    if not pachong.run_status:
        return  # 直接返回，不执行后续代码
    else:
        pachong.run_status = False  # 将pachong的运行状态设置为True
        # 添加开始记录进程的代码
        pachong.logger.info("爬虫关闭中...")


# 退出程序
@socketio.on('exit_def')
def exit_def():
    logging.debug("单击退出按钮...")
    pachong.run_status = False
    pachong.logger.info("爬虫关闭中...")
    print(4)
    os._exit(0)
    print(5)
    os.kill(pid, signal.SIGTERM)  # 主动结束指定ID的程序运行


# 启动Flask和SocketIO服务器
if __name__ == '__main__':
    pc_thread()
    socketio.run(app, use_reloader=False, allow_unsafe_werkzeug=True, port=pachong.web_post, host=pachong.web_host)
