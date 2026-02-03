#!/usr/bin/env python3
"""
测试修复后的 Monica API 客户端
验证接口路径和参数修复是否成功
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

def test_api_fixes():
    """测试修复后的 API 客户端"""
    print("开始测试修复后的 Monica API 客户端...")
    print("=" * 60)
    
    try:
        # 初始化 API 客户端
        api = MonicaAPI()
        print(f"✅ API 客户端初始化成功")
        print(f"基础 URL: {api.api_url}")
        print("=" * 60)
        
        # 测试 1: 测试 list_contacts 接口（修复尾部斜杠）
        print("测试 1: list_contacts 接口")
        try:
            result = api.list_contacts(limit=5)
            if result.get('data'):
                print(f"✅ 成功获取联系人列表，共 {len(result['data'])} 个联系人")
            else:
                print(f"⚠️  联系人列表为空")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 2: 测试 list_tags 接口（修复尾部斜杠）
        print("测试 2: list_tags 接口")
        try:
            result = api.list_tags(limit=5)
            if result.get('data'):
                print(f"✅ 成功获取标签列表，共 {len(result['data'])} 个标签")
            else:
                print(f"⚠️  标签列表为空")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 3: 测试 create_tag 接口（修复尾部斜杠）
        print("测试 3: create_tag 接口")
        try:
            tag_name = f"test_fix_tag_{int(datetime.now().timestamp())}"
            result = api.create_tag(name=tag_name)
            print(f"✅ 成功创建标签: {result['name']} (ID: {result['id']})")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 4: 测试 list_tasks 接口（修复尾部斜杠）
        print("测试 4: list_tasks 接口")
        try:
            result = api.list_tasks(limit=5)
            if result.get('data'):
                print(f"✅ 成功获取任务列表，共 {len(result['data'])} 个任务")
            else:
                print(f"⚠️  任务列表为空")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 5: 测试 list_reminders 接口（修复尾部斜杠）
        print("测试 5: list_reminders 接口")
        try:
            result = api.list_reminders(limit=5)
            if result.get('data'):
                print(f"✅ 成功获取提醒列表，共 {len(result['data'])} 个提醒")
            else:
                print(f"⚠️  提醒列表为空")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 6: 测试 create_reminder 接口（修复参数问题）
        print("测试 6: create_reminder 接口")
        try:
            # 获取第一个联系人的 ID 作为测试用
            contacts = api.list_contacts(limit=1)
            if contacts.get('data'):
                contact_id = contacts['data'][0]['id']
                reminder_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                result = api.create_reminder(
                    title="测试提醒（修复后）",
                    date=reminder_date,
                    contact_id=contact_id
                )
                print(f"✅ 成功创建提醒: {result['title']} (ID: {result['id']})")
            else:
                print("⚠️  没有联系人，跳过提醒创建测试")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 7: 测试 list_activities 接口（修复尾部斜杠）
        print("测试 7: list_activities 接口")
        try:
            result = api.list_activities(limit=5)
            if result.get('data'):
                print(f"✅ 成功获取活动列表，共 {len(result['data'])} 个活动")
            else:
                print(f"⚠️  活动列表为空")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 8: 测试 list_notes 接口（修复尾部斜杠）
        print("测试 8: list_notes 接口")
        try:
            result = api.list_notes(limit=5)
            if result.get('data'):
                print(f"✅ 成功获取笔记列表，共 {len(result['data'])} 个笔记")
            else:
                print(f"⚠️  笔记列表为空")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("=" * 60)
        
        print("🎉 所有测试完成！")
        print("=" * 60)
        
    except MonicaAPIError as e:
        print(f"❌ API 客户端初始化失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_api_fixes()
    sys.exit(0 if success else 1)
