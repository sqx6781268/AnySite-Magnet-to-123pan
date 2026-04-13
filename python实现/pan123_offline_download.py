#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
123云盘离线下载工具
基于 dmhy123 油猴脚本的接口逆向实现
支持磁力链接解析和离线下载任务提交
"""

import requests
import json
import time
import os
from typing import Optional, Dict, List


# ==================== 用户配置区域 ====================
# 在此处填入您的 123 云盘 Token（从浏览器获取）
# 获取方式详见 README.md 文件
USER_TOKEN = ""  # 例如: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 如果设置为 True，将自动选择所有文件；False 则需要手动选择
AUTO_SELECT_ALL = True

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30
# ====================================================


class Pan123OfflineDownload:
    """123云盘离线下载客户端"""
    
    def __init__(self, token: str = None):
        """
        初始化客户端
        
        Args:
            token: 123云盘授权Token (Bearer Token)，如果不提供则使用全局配置
        """
        # 优先级：参数 > 环境变量 > 全局变量
        self.token = token or os.getenv('PAN123_TOKEN') or USER_TOKEN
        
        if not self.token:
            raise ValueError(
                "未找到有效的Token！\n"
                "请通过以下任一方式配置Token：\n"
                "1. 在脚本顶部的 USER_TOKEN 变量中填写\n"
                "2. 设置环境变量 PAN123_TOKEN\n"
                "3. 调用时传入 token 参数\n"
                "详见 README.md 获取Token教程"
            )
        
        self.base_url = "https://www.123pan.com"
        self.session = requests.Session()
        
        # 设置通用请求头
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'App-Version': '3',
            'platform': 'web',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://www.123pan.com',
            'Referer': 'https://www.123pan.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def _request(self, method: str, url: str, data: dict = None) -> dict:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET/POST)
            url: 请求URL路径
            data: 请求体数据
            
        Returns:
            响应JSON数据
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        full_url = f"{self.base_url}{url}"
        
        try:
            response = self.session.request(
                method=method,
                url=full_url,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            
            # 检查HTTP状态码
            if response.status_code == 401:
                raise Exception("TOKEN_EXPIRED: Token已过期，请重新获取")
            
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            
            # 检查业务状态码
            if result.get('code') != 0:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"API错误 (code={result.get('code')}): {error_msg}")
            
            return result
            
        except requests.exceptions.JSONDecodeError:
            raise Exception("JSON解析失败: 响应内容不是有效的JSON格式")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接失败: 无法连接到123云盘服务器")
        except requests.exceptions.Timeout:
            raise Exception("请求超时: 服务器响应时间过长")
        except Exception as e:
            if str(e).startswith(("TOKEN_EXPIRED", "API错误", "JSON解析失败", "网络连接失败", "请求超时")):
                raise
            raise Exception(f"请求失败: {str(e)}")
    
    def resolve_magnet(self, magnet_link: str) -> dict:
        """
        解析磁力链接，获取文件列表和任务ID
        
        Args:
            magnet_link: 磁力链接字符串
            
        Returns:
            包含任务信息和文件列表的字典
            
        Raises:
            Exception: 解析失败时抛出异常
        """
        print(f"[INFO] 正在解析磁力链接...")
        print(f"[DEBUG] 磁力链接: {magnet_link[:50]}...")
        
        payload = {
            "urls": magnet_link
        }
        
        response = self._request(
            method='POST',
            url='/b/api/v2/offline_download/task/resolve',
            data=payload
        )
        
        # 提取任务信息
        task_list = response.get('data', {}).get('list', [])
        if not task_list:
            raise Exception("解析失败: 未获取到任务信息")
        
        task_info = task_list[0]
        
        # 检查解析错误码
        if task_info.get('err_code') != 0:
            raise Exception(f"解析失败 (err_code={task_info.get('err_code')})")
        
        # 提取文件列表
        files = task_info.get('files', [])
        if not files:
            raise Exception("解析失败: 未找到可下载的文件")
        
        print(f"[SUCCESS] 解析成功!")
        print(f"[INFO] 任务ID: {task_info.get('id')}")
        print(f"[INFO] 文件数量: {len(files)}")
        
        for idx, file in enumerate(files, 1):
            size_mb = file.get('size', 0) / (1024 * 1024)
            print(f"  [{idx}] {file.get('name')} ({size_mb:.2f} MB)")
        
        return task_info
    
    def submit_task(self, task_id: str, file_ids: List[str]) -> dict:
        """
        提交离线下载任务
        
        Args:
            task_id: 任务ID (来自resolve_magnet的返回值)
            file_ids: 要下载的文件ID列表
            
        Returns:
            提交结果信息
            
        Raises:
            Exception: 提交失败时抛出异常
        """
        print(f"\n[INFO] 正在提交离线下载任务...")
        print(f"[DEBUG] 任务ID: {task_id}")
        print(f"[DEBUG] 文件数量: {len(file_ids)}")
        
        payload = {
            "resource_list": [
                {
                    "resource_id": task_id,
                    "select_file_id": file_ids
                }
            ]
        }
        
        response = self._request(
            method='POST',
            url='/b/api/v2/offline_download/task/submit',
            data=payload
        )
        
        task_data = response.get('data', {})
        print(f"[SUCCESS] 任务提交成功!")
        print(f"[INFO] 下载任务ID: {task_data.get('task_id')}")
        print(f"[INFO] 任务状态: {task_data.get('status')}")
        
        return task_data
    
    def save_to_123pan(self, magnet_link: str, select_all: bool = None) -> dict:
        """
        一键转存：解析磁力链接并提交离线下载任务
        
        Args:
            magnet_link: 磁力链接字符串
            select_all: 是否选择所有文件 (默认使用全局配置 AUTO_SELECT_ALL)
            
        Returns:
            完整的任务信息
            
        Raises:
            Exception: 任何步骤失败时抛出异常
        """
        # 如果未指定，使用全局配置
        if select_all is None:
            select_all = AUTO_SELECT_ALL
        
        print("=" * 60)
        print("123云盘离线下载工具")
        print("=" * 60)
        
        # 步骤1: 解析磁力链接
        task_info = self.resolve_magnet(magnet_link)
        
        # 步骤2: 提取文件ID
        files = task_info.get('files', [])
        if select_all:
            file_ids = [f['id'] for f in files]
        else:
            # 这里可以添加交互式选择逻辑
            file_ids = [f['id'] for f in files]
            print(f"\n[INFO] 默认选择所有 {len(file_ids)} 个文件")
        
        # 步骤3: 提交任务
        task_data = self.submit_task(task_info['id'], file_ids)
        
        print("\n" + "=" * 60)
        print(f"[COMPLETE] 成功添加 {len(file_ids)} 个文件到离线下载")
        print("=" * 60)
        
        return {
            'task_id': task_info['id'],
            'files': files,
            'submit_result': task_data
        }


def get_token_from_user() -> str:
    """
    从用户输入获取Token
    
    Returns:
        用户输入的Token字符串
    """
    print("\n请提供123云盘授权Token:")
    print("获取方式:")
    print("1. 访问 https://www.123pan.com/ 并登录")
    print("2. 打开浏览器开发者工具 (F12)")
    print("3. 在 Application/Storage -> Local Storage 中查找 'authorToken' 或 'userInfo'")
    print("4. 复制Token值并粘贴到下方\n")
    
    token = input("请输入Token: ").strip()
    
    if not token:
        raise ValueError("Token不能为空")
    
    if len(token) < 50:
        raise ValueError("Token长度异常，请确认是否正确复制")
    
    return token


def main():
    """主函数"""
    try:
        # 检查Token配置
        if not USER_TOKEN and not os.getenv('PAN123_TOKEN'):
            print("[WARNING] 未在脚本中配置Token，将使用交互式输入")
            print("提示：您可以在脚本顶部的 USER_TOKEN 变量中直接配置Token\n")
            token = get_token_from_user()
        else:
            token = None  # 使用已配置的Token
        
        # 创建客户端
        client = Pan123OfflineDownload(token)
        
        # 获取磁力链接
        print("\n请输入磁力链接:")
        magnet_link = input(">>> ").strip()
        
        if not magnet_link.startswith('magnet:'):
            raise ValueError("无效的磁力链接格式（应以 magnet: 开头）")
        
        # 执行离线下载
        result = client.save_to_123pan(magnet_link)
        
        print("\n任务详情:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except KeyboardInterrupt:
        print("\n\n[INFO] 用户取消操作")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())