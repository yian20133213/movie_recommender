#!/usr/bin/env python3

import os
import subprocess
import webbrowser
import time
import platform
from dotenv import load_dotenv

def check_requirements():
    """检查依赖是否已安装"""
    try:
        import streamlit
        import pandas
        import requests
        import plotly
        from PIL import Image
        return True
    except ImportError as e:
        print(f"缺少必要的依赖: {e}")
        install = input("是否自动安装依赖? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
            return True
        else:
            print("请手动安装依赖: pip install -r requirements.txt")
            return False

def check_api_key():
    """检查API密钥是否已设置"""
    # 尝试从.env文件加载
    load_dotenv()
    
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("未找到TMDB API密钥")
        api_key = input("请输入您的TMDB API密钥: ")
        
        # 保存到.env文件
        with open(".env", "w") as f:
            f.write(f"TMDB_API_KEY={api_key}\n")
        
        # 更新环境变量
        os.environ["TMDB_API_KEY"] = api_key
        
        print("API密钥已保存到.env文件")

def create_directories():
    """创建必要的目录"""
    dirs = ["data", "assets/images", "assets/css"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def run_app():
    """运行Streamlit应用"""
    print("正在启动AI观影助手...")
    
    # 启动Streamlit应用
    process = subprocess.Popen(["streamlit", "run", "app.py"])
    
    # 等待服务器启动
    time.sleep(2)
    
    # 打开浏览器
    webbrowser.open("http://localhost:8501")
    
    print("应用已启动！按Ctrl+C停止服务器")
    
    try:
        # 保持脚本运行直到用户中断
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        print("\n应用已停止")

def display_welcome():
    """显示欢迎信息"""
    welcome_text = """
    #########################################
    #                                       #
    #          AI观影助手启动器             #
    #                                       #
    #########################################
    
    欢迎使用AI观影助手！
    这个应用会帮助你基于心情和喜好发现完美电影。
    
    正在准备启动...
    """
    print(welcome_text)

def clear_screen():
    """清除控制台屏幕"""
    # 根据操作系统使用不同的清屏命令
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def main():
    """主函数"""
    clear_screen()
    display_welcome()
    
    # 检查依赖
    if not check_requirements():
        return
    
    # 检查API密钥
    check_api_key()
    
    # 创建必要的目录
    create_directories()
    
    # 运行应用
    run_app()

if __name__ == "__main__":
    main()