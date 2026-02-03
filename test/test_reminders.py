#!/usr/bin/env python3
"""
测试提醒模块（Reminders）的功能
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

def test_reminders_api():
    """测试提醒模块 API"""
    print("开始测试提醒模块 API...")
    print("=" * 60)
    
    try:
        # 初始化 API 客户端
        api = MonicaAPI()
        print(f"✅ API 客户端初始化成功")
        print(f"基础 URL: {api.api_url}")
        print("=" * 60)
        
        # 测试 1: 测试 list_reminders 接口
        print("测试 1: list_reminders 接口")
        try:
            result = api.list_reminders(limit=5)
            if result.get('data'):
                print(f"✅ 成功获取提醒列表，共 {len(result['data'])} 个提醒")
            else:
                print(f"⚠️  提醒列表为空")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 2: 测试 create_reminder 接口
        print("测试 2: create_reminder 接口")
        try:
            # 获取第一个联系人的 ID
            contacts = api.list_contacts(limit=1)
            if contacts.get('data'):
                contact_id = contacts['data'][0]['id']
                
                # 创建提醒
                reminder_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                reminder = api.create_reminder(
                    title="测试提醒",
                    date=reminder_date,
                    contact_id=contact_id
                )
                print(f"✅ 成功创建提醒: {reminder['title']} (ID: {reminder['id']})")
                
                # 测试 3: 测试 get_reminder 接口
                print("测试 3: get_reminder 接口")
                try:
                    result = api.get_reminder(reminder['id'])
                    print(f"✅ 成功获取提醒详情: {result['title']}")
                except Exception as e:
                    print(f"❌ 测试失败: {e}")
                print("-" * 60)
                
                # 测试 4: 测试 delete_reminder 接口
                print("测试 4: delete_reminder 接口")
                try:
                    result = api.delete_reminder(reminder['id'])
                    print(f"✅ 成功删除提醒: ID {reminder['id']}")
                except Exception as e:
                    print(f"❌ 测试失败: {e}")
            else:
                print("⚠️  没有联系人，跳过测试")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        print("=" * 60)
        print("🎉 所有提醒模块 API 测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reminders_api()
