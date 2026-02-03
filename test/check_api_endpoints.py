#!/usr/bin/env python3
"""
检查 API 根路径，获取可用的接口列表
"""

import sys
import json
from pathlib import Path

# 直接导入 API 模块
import importlib.util
import sys
from pathlib import Path

# 加载 API 模块
api_file = Path(__file__).parent.parent / '.claude' / 'skills' / 'crm' / 'scripts' / 'monica_api.py'
spec = importlib.util.spec_from_file_location("monica_api", api_file)
monica_api = importlib.util.module_from_spec(spec)
sys.modules["monica_api"] = monica_api
spec.loader.exec_module(monica_api)

MonicaAPI = monica_api.MonicaAPI
MonicaAPIError = monica_api.MonicaAPIError

def check_api_endpoints():
    """检查 API 根路径"""
    print("检查 API 根路径...")
    print("=" * 60)
    
    try:
        # 初始化 API 客户端
        api = MonicaAPI()
        print(f"✅ API 客户端初始化成功")
        print(f"基础 URL: {api.api_url}")
        print("=" * 60)
        
        # 测试根路径
        print("测试 API 根路径...")
        try:
            # 尝试获取 API 根路径
            import requests
            headers = api._get_headers()
            response = requests.get(api.api_url, headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试其他可能的路径
        print("测试其他可能的路径...")
        test_paths = [
            '/api',
            '/api/v1',
            '/api/v2',
            '/conversations',
            '/conversation'
        ]
        
        for path in test_paths:
            try:
                import requests
                headers = api._get_headers()
                url = api.api_url.rstrip('/') + path
                response = requests.get(url, headers=headers, timeout=5)
                print(f"{path}: {response.status_code}")
            except Exception as e:
                print(f"{path}: 错误 - {e}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_api_endpoints()
