#!/usr/bin/env python3
"""
测试 Activities 接口
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

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

def test_activities_api():
    """测试 Activities API"""
    print("开始测试 Activities API...")
    print("=" * 60)
    
    try:
        # 初始化 API 客户端
        api = MonicaAPI()
        print(f"✅ API 客户端初始化成功")
        print(f"基础 URL: {api.api_url}")
        print("=" * 60)
        
        # 测试 list_activities 接口
        print("测试 list_activities 接口")
        try:
            result = api.list_activities(limit=5)
            if result.get('data'):
                print(f"✅ 成功获取活动列表，共 {len(result['data'])} 个活动")
            else:
                print(f"⚠️  活动列表为空")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_activities_api()
