from flask import Flask, render_template
from flask_socketio import SocketIO
import os
import time
import threading
from log import *
import pachong

app = Flask(__name__)
socketio = SocketIO(app)
# logging_active = True  # 默认为True，表示启动应用程序时开始日志记录
thread = None
STATUS_COLOR = "green"  # 初始颜色为绿色


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
    '''
    渲染主页

    从日志文件中读取内容
    并将其传递给index.html模板进行渲染
    '''
    log_content = read_log_file()
    return render_template('index.html', log_content=log_content)


# # 客户端连接成功时执行的函数
# @socketio.on('connect')
# def handle_connect():
#     # 客户端连接成功时执行的函数
#     global STATUS_COLOR
#
#     while True:
#         time.sleep(0.5)  # 每秒钟刷新两次日志文件内容
#         log_content = read_log_file()  # 读取日志文件内容
#         socketio.emit('update_log', log_content)  # 发送更新日志的内容给客户端
#         if pachong.run_status:  # 如果pachong运行状态为True
#             STATUS_COLOR = "green"  # 状态颜色为绿色
#         else:
#             STATUS_COLOR = "red"  # 状态颜色为红色
#         socketio.emit('update_status_color', STATUS_COLOR)  # 发送更新状态颜色的内容给客户端
#         if pachong.run_status:
#             status_info = "正在运行"
#         else:
#             status_info = "未运行"
#         socketio.emit('update_status_info', status_info)



def background_thread():
    while True:
        time.sleep(0.5)
        log_content = pachong.read_log_file()
        socketio.emit('update_log', log_content)
        socketio.emit('update_status_color', STATUS_COLOR)
        status_info = "正在运行" if pachong.run_status else "未运行"
        socketio.emit('update_status_info', status_info)

@socketio.on('connect')
def handle_connect():
    global STATUS_COLOR
    socketio.emit('update_status_color', STATUS_COLOR)
    threading.Thread(target=background_thread).start()

@socketio.on('update_backend_variable2')
def update_backend_variable2(new_value):
    global backend_variable2
    backend_variable2 = new_value
    if pachong.run_status:
        backend_variable2 = "正在运行"
    else:
        backend_variable2 = "未运行"
    socketio.emit('updated_variable2', backend_variable2)


# 后台线程函数
def background_thread():
    global STATUS_COLOR  # 全局变量STATUS_COLOR
    while True:  # 当True时循环执行以下代码
        time.sleep(1)  # 程序休眠1秒
        log_content = read_log_file()  # 读取日志文件内容
        socketio.emit('update_log', log_content)  # 发送"update_log"事件，传递log_content作为数据
        if pachong.run_status:  # 如果pachong的运行状态为True
            STATUS_COLOR = "green"  # 将STATUS_COLOR设为"green"
        else:  # 否则
            STATUS_COLOR = "red"  # 将STATUS_COLOR设为"red"
        socketio.emit('update_status_color', STATUS_COLOR)  # 发送"update_status_color"事件，传递STATUS_COLOR作为数据


# 爬虫线程函数
def pc_thread():
    # 创建一个线程对象pc
    pc = threading.Thread(target=pachong.run)
    # 启动线程
    logging.debug("爬虫主线程启动中...")
    pc.start()


# # 启动爬虫
# @socketio.on('start_pachong')
# def start_pachong():
#     print('爬虫启动')
#
#
# # 停止爬虫
# @socketio.on('stop_pachong')
# def stop_logging():
#     print('单击爬虫关闭按钮')
#
#
#
#












# 启动爬虫
@socketio.on('start_pachong')
def start_pachong():
    logging.debug("以单击爬虫启动按钮...")
    if pachong.run_status:  # 如果pachong的运行状态为True
        return  # 直接返回，不执行后续代码
    else:
        pachong.run_status = True  # 将pachong的运行状态设置为True
        # 添加开始记录进程的代码
        pachong.logger.info("爬虫启动中...")  # 记录日志，提示爬虫正在启动


# 停止爬虫
@socketio.on('stop_pachong')
def stop_logging():
    logging.debug("以单击爬虫关闭按钮...")
    pachong.run_status = False
    if not pachong.run_status:
        return
    else:
        # Add code to stop logging process

        pachong.logger.info("爬虫关闭中...")


# 启动Flask和SocketIO服务器
if __name__ == '__main__':
    pc_thread()
    socketio.run(app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
