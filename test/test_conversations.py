#!/usr/bin/env python3
"""
测试新添加的 Conversations 接口
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

def test_conversations_api():
    """测试 Conversations API"""
    print("开始测试 Conversations API...")
    print("=" * 60)
    
    try:
        # 初始化 API 客户端
        api = MonicaAPI()
        print(f"✅ API 客户端初始化成功")
        print(f"基础 URL: {api.api_url}")
        print("=" * 60)
        
        # 测试 1: 测试 list_conversations 接口
        print("测试 1: list_conversations 接口")
        try:
            result = api.list_conversations(limit=5)
            if result.get('data'):
                print(f"✅ 成功获取对话列表，共 {len(result['data'])} 个对话")
            else:
                print(f"⚠️  对话列表为空")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 2: 测试 list_contact_conversations 接口
        print("测试 2: list_contact_conversations 接口")
        try:
            # 获取第一个联系人的 ID
            contacts = api.list_contacts(limit=1)
            if contacts.get('data'):
                contact_id = contacts['data'][0]['id']
                result = api.list_contact_conversations(contact_id, limit=5)
                if result.get('data'):
                    print(f"✅ 成功获取联系人的对话列表，共 {len(result['data'])} 个对话")
                else:
                    print(f"⚠️  联系人的对话列表为空")
            else:
                print("⚠️  没有联系人，跳过测试")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        # 测试 3: 测试 create_conversation 和 add_message_to_conversation 接口
        print("测试 3: create_conversation 和 add_message_to_conversation 接口")
        try:
            # 获取第一个联系人的 ID
            contacts = api.list_contacts(limit=1)
            if contacts.get('data'):
                contact_id = contacts['data'][0]['id']
                
                # 尝试不同的 contact_field_type_id 值
                for field_type_id in [1, 2, 3, 4, 5]:
                    try:
                        # 创建对话
                        happened_at = datetime.now().isoformat()
                        print(f"  尝试使用 contact_field_type_id={field_type_id}...")
                        conversation = api.create_conversation(
                            contact_id=contact_id,
                            contact_field_type_id=field_type_id,
                            happened_at=happened_at
                        )
                        print(f"✅ 成功创建对话: ID {conversation['id']}")
                        
                        # 添加消息到对话
                        message_content = "这是一条测试消息"
                        written_at = datetime.now().isoformat()
                        message = api.add_message_to_conversation(
                            conversation_id=conversation['id'],
                            content=message_content,
                            written_at=written_at
                        )
                        print(f"✅ 成功添加消息到对话: ID {message['id']}")
                        break
                    except Exception as e:
                        print(f"  ❌ 尝试失败: {e}")
                        continue
            else:
                print("⚠️  没有联系人，跳过测试")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        print("-" * 60)
        
        print("=" * 60)
        print("🎉 所有 Conversations API 测试完成！")
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
    success = test_conversations_api()
    sys.exit(0 if success else 1)
