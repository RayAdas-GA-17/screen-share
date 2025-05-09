# -*- encoding: utf-8 -*-
"""
@File: main.py
@Description: 通过 Web 共享本地屏幕
@Author: Ray
@Time: 2025/04/26 21:50:15
"""


import io
import threading
import time
from datetime import datetime

import pyautogui
from flask import Flask, jsonify, render_template, send_file

app = Flask(__name__)
app.config["SCREENSHOT_INTERVAL"] = 1  # 每隔1秒截屏一次
# app.config["SCREENSHOT_INTERVAL"] = 1 / 25  # FPS 25
app.config["LATEST_SCREESHOT"] = None  # 用于存储最新的截图字节数据


# 创建一个可复用的BytesIO缓冲区
screenshot_buffer = io.BytesIO()


def capture_screenshot():
    """截取屏幕并返回图像字节数据"""
    global screenshot_buffer  # 使用全局变量来复用缓冲区

    # 截取屏幕
    screenshot = pyautogui.screenshot()

    # 将图像保存到复用的BytesIO缓冲区
    # 首先清空缓冲区
    screenshot_buffer.seek(0)
    screenshot_buffer.truncate(0)

    # 保存图像到缓冲区
    screenshot.save(screenshot_buffer, format="PNG")

    # 获取缓冲区中的字节数据
    img_byte_arr = screenshot_buffer.getvalue()

    # 更新最新的截图数据
    app.config["LATEST_SCREESHOT"] = img_byte_arr
    # print(f"截图已捕获，保存在内存中: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def screenshot_scheduler():
    """定期截屏的调度器"""
    while True:
        capture_screenshot()
        time.sleep(app.config["SCREENSHOT_INTERVAL"])


@app.route("/capture")
def capture():
    """立即截取屏幕"""
    capture_screenshot()
    return jsonify({"status": "success"})


@app.route("/")
def index():
    """主页面，显示最新截图"""
    return render_template("index.html")


@app.route("/latest_screenshot")
def latest_screenshot():
    """获取最新的截图"""
    if app.config["LATEST_SCREESHOT"]:
        return send_file(io.BytesIO(app.config["LATEST_SCREESHOT"]), mimetype="image/png")
    return jsonify({"error": "没有可用的截图"}), 404


if __name__ == "__main__":
    # 启动截图线程
    screenshot_thread = threading.Thread(target=screenshot_scheduler)
    screenshot_thread.daemon = True  # 设置为守护线程，当主线程结束时自动结束
    screenshot_thread.start()

    # 启动Flask应用
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
