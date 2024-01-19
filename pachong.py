#!/use/bin/env python3.10
# coding:utf-8

"""
@version: 3.10
@author: huluobo
@file: pachong.py
@time: 2023/12/28 16:51
"""
import re
import sys
import time
from typing import Any, List

import requests
import urllib3
from bs4 import BeautifulSoup

from log import *

urllib3.disable_warnings()

# ssl._create_default_https_context = ssl._create_unverified_context

save_directory = "d:\爬取的种子"  # 保存目录
target_url = "http://www.btbtt12.com/forum-index-fid-951-page-{}.htm"  # 爬取网址
page_nums = 6  # 爬取页数，默认是4，一页50条
sleep_time = 1200  # 等待时间-默认30分钟
run_status = True  # 爬取状态，默认为True，程序开启时自动开启爬虫。为False时，程序不会开启爬虫。
a_url = 'http://www.btbtt12.com/'
web_post = 5020  # 网站端口
web_host = '127.0.0.1'  # 网站地址


class Movies:
    def __init__(self):
        pass

    def get_link(self, url, movie_name):

        # 发送HTTP请求
        response = requests.get(url, verify=False)

        # 检查请求是否成功
        if response.status_code == 200:
            # 使用BeautifulSoup解析HTML
            soup1 = BeautifulSoup(response.text, 'html.parser')
            links1 = soup1.find('div', class_='width border bg1')
            links1 = links1.find_all('a')
            for link1 in links1:
                url = a_url + (link1.get('href'))
                self.dow_torrent(url, movie_name)

    def get_list(self):
        # 初始化一个空字典列表
        movies_list: list[Any] = []

        for page_num in range(1, page_nums + 1):
            url = target_url.format(page_num)

            # 发送HTTP请求
            try:
                response = requests.get(url, verify=False)
            except:
                logger.error("获取页面失败", url)
                continue

            # 检查请求是否成功
            if response.status_code == 200:
                # 使用BeautifulSoup解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all(title=re.compile('BT下载'))
                for link in links:
                    href = a_url + link.get('href', '')
                    title = link.get('title', '')
                    name = re.findall(r'\[([^]]+)\]', title)[1]
                    if href and title:
                        link_dict = {'movie_name': name, 'title': title, 'url': href}
                        Movies.add_dict_with_unique_name(self, movies_list, link_dict)

        return movies_list

    def add_dict_with_unique_name(self, movies_list, dictionary):
        if 'movie_name' in dictionary:
            txt_file_path = os.path.join("已下载的种子.txt")
            if Movies.is_unique_name(movies_list, dictionary['movie_name'], txt_file_path):
                movies_list.append(dictionary)
                logger.debug(f"已添加电影 {dictionary['movie_name']} 的进入下载列表.")
            else:
                logger.debug(f"电影 {dictionary['movie_name']} 已存在.")
        else:
            logger.debug("字典必须有一个“movie_name”键.")

    @staticmethod
    def is_unique_name(lst, id_to_check, downloaded_file_path):
        """
        检查列表中是否存在具有相同 'movie_name' 的字典，并检查 'movie_name' 是否在已下载的种子文件中。

        Parameters:
            - lst (list): 包含字典的列表。
            - id_to_check (str): 要检查的 'movie_name'。
            - downloaded_file_path (str): 已下载种子文件的路径。

        Returns:
            bool: 如果列表中不存在具有相同 'movie_name' 的字典，并且 'movie_name' 不在已下载的种子文件中，返回 True；否则返回 False。
        """
        # 检查列表中是否存在相同 'movie_name' 的字典
        if any(item.get('movie_name') == id_to_check for item in lst):
            return False

        # 检查 'movie_name' 是否在已下载的种子文件中
        with open(downloaded_file_path, 'r') as file:
            downloaded_movies = [line.strip() for line in file]

        return id_to_check not in downloaded_movies

    def get_movie_bt_download_url(self, movies_list):
        """
        获取电影BT下载链接
        :param movies_list: 电影列表
        """
        for movie_info in movies_list:
            response = requests.get(movie_info['url'], verify=False)  # 发送GET请求获取网页内容
            soup = BeautifulSoup(response.text, 'html.parser')  # 解析网页内容

            try:
                # 例如，提取所有链接
                links = soup.find('div', class_='attachlist')  # 找到包含链接的div标签
                if links:
                    links = links.find_all('a')  # 获取所有链接标签
                    for link in links:
                        url = a_url + (link.get('href'))  # 获取链接地址
                        movie_name = movie_info['movie_name']  # 获取电影名称
                        self.dow_torrent(url, movie_name)  # 处理链接和电影名称
                else:
                    logger.info(f"没有找到下载链接",movie_info['movie_name'])

            except Exception as e:
                logger.info("电影的种子下载完毕", e)  # 记录异常信息

    def dow_torrent(self, url, movie_name):
        save_path = save_directory + movie_name + '.torrent'

        # 下载 .torrent 文件
        response = requests.get(url, verify=False)

        # 确保下载文件夹存在，如果不存在则创建
        os.makedirs(save_directory, exist_ok=True)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # 构建本地文件的完整路径
        try:
            # movie_name1 = re.findall(r'\[([^]]+)\]', movie_names)[1]
            torrent_name = movie_name + ".torrent"

            local_file_path = os.path.join(save_directory, torrent_name)
            # logger.info(local_file_path)
            txt_file_path = os.path.join("已下载的种子.txt")

            # 以二进制写入模式保存Torrent文件
            if os.path.exists(txt_file_path):
                with open(txt_file_path, "r") as txt_file:
                    downloaded_files = txt_file.read().splitlines()
                    if movie_name not in downloaded_files:
                        with open(local_file_path, "wb") as torrent_file:
                            torrent_file.write(response.content)
                        logger.info(f"Torrent文件已保存到：{local_file_path}")
                        with open(txt_file_path, "a") as txt_file:
                            txt_file.write(movie_name + "\n")
                            logger.debug(f"文件 '{movie_name}' 下载完成，并已记录。")

                    else:
                        logger.debug(f"文件 '{movie_name}' 已经下载过，跳过下载。")
        except Exception as e:
            logger.info("下载完毕，等待下一个循环", e)


def create_download_log_file():  # 创建已下载电影列表
    # 获取当前工作目录
    current_folder = os.getcwd()
    # 拼接种子文件路径
    txt_file_path = os.path.join(current_folder, "已下载的种子.txt")

    # 如果种子文件不存在，则创建
    if not os.path.exists(txt_file_path):
        # 打开种子文件，并写入内容
        with open(txt_file_path, "w") as txt_file:
            # 打印提示信息，种子文件已创建在当前目录
            logger.info(f"已下载的种子.txt 文件已创建在 {current_folder}。")


def run():
    # 调用爬虫函数
    while True:
        if run_status:
            logger.debug("爬虫运行中")

            create_download_log_file()  # 创建已下载电影列表
            # Movies().get_list()  # 获取需要下载的电影列表
            Movies().get_movie_bt_download_url(Movies().get_list())  # 下载种子
            try:
                # 等待时间-默认30分钟
                logger.info("爬虫开始休息")
                for i in range(sleep_time):
                    time.sleep(1)
                    if i % 30 == 0:
                        logger.debug(f"爬虫等待{i}秒")
                    if not run_status:
                        break
                else:
                    logger.info("爬虫等待完成")
            except Exception as e:
                logger.error(f"发生异常：{e}")
                sys.exit("爬虫被中断")  # 等待时间-默认30分钟

            if not os.path.exists(save_directory):
                logger.info("种子文件下载完成，等待下一个循环")
        else:
            pass
        time.sleep(1)


if __name__ == "__main__":
    run()  # 启动爬虫
