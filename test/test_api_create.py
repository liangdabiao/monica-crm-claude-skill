import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 加载环境变量
load_dotenv('../.env')

# 获取API配置
API_TOKEN = os.getenv('MONICA_API_TOKEN')
BASE_URL = os.getenv('MONICA_BASE_URL')

# 设置请求头
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# 测试结果
results = []

print("开始测试 Monica API Create 接口...")
print(f"基础URL: {BASE_URL}")
print("=" * 60)

# 先获取一些必要的ID
def get_contact_id():
    """获取第一个联系人的ID"""
    try:
        response = requests.get(f"{BASE_URL}/contacts", headers=headers, params={'limit': 1})
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                return data['data'][0]['id']
    except Exception as e:
        print(f"获取联系人ID失败: {e}")
    return None

def get_activity_type_id():
    """获取第一个活动类型的ID"""
    try:
        response = requests.get(f"{BASE_URL}/activitytypes", headers=headers, params={'limit': 1})
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                return data['data'][0]['id']
    except Exception as e:
        print(f"获取活动类型ID失败: {e}")
    return None

# 准备测试数据
contact_id = get_contact_id()
activity_type_id = get_activity_type_id()
print(f"\n准备测试数据:")
print(f"联系人ID: {contact_id}")
print(f"活动类型ID: {activity_type_id}")
print("=" * 60)

# 测试模块列表
modules_to_test = [
    {
        'name': 'Tags',
        'endpoint': '/tags',
        'data': {
            'name': f'test_tag_{int(datetime.now().timestamp())}'
        },
        'requires_deps': False
    },
    {
        'name': 'Notes',
        'endpoint': '/notes',
        'data': {
            'body': '这是一个测试笔记',
            'contact_id': contact_id,
            'is_favorited': 0
        },
        'requires_deps': True,
        'deps': {'contact_id': contact_id}
    },
    {
        'name': 'Tasks',
        'endpoint': '/tasks',
        'data': {
            'title': '这是一个测试任务',
            'description': '任务描述',
            'completed': 0,
            'contact_id': contact_id
        },
        'requires_deps': True,
        'deps': {'contact_id': contact_id}
    },
    {
        'name': 'Reminders',
        'endpoint': '/reminders',
        'data': {
            'title': '这是一个测试提醒',
            'description': '提醒描述',
            'initial_date': datetime.now().strftime('%Y-%m-%d'),
            'next_expected_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'frequency_type': 'one_time',
            'frequency_number': 1,
            'contact_id': contact_id
        },
        'requires_deps': True,
        'deps': {'contact_id': contact_id}
    },
    {
        'name': 'Activities',
        'endpoint': '/activities',
        'data': {
            'activity_type_id': activity_type_id,
            'summary': '这是一个测试活动',
            'description': '活动描述',
            'happened_at': datetime.now().strftime('%Y-%m-%d'),
            'contacts': [contact_id]
        },
        'requires_deps': True,
        'deps': {'contact_id': contact_id, 'activity_type_id': activity_type_id}
    }
]

# 测试每个模块
for module in modules_to_test:
    print(f"\n测试模块: {module['name']}")
    print(f"Endpoint: {module['endpoint']}")
    print("-" * 40)
    
    # 检查依赖
    if module['requires_deps']:
        deps_valid = True
        for dep_name, dep_value in module['deps'].items():
            if not dep_value:
                print(f"❌ 缺少依赖: {dep_name}")
                deps_valid = False
        if not deps_valid:
            print("跳过测试")
            results.append({
                'module': module['name'],
                'status': 'skipped',
                'message': '缺少必要的依赖'
            })
            print("-" * 40)
            continue
    
    try:
        # 发送POST请求
        response = requests.post(
            f"{BASE_URL}{module['endpoint']}",
            headers=headers,
            json=module['data']
        )
        
        # 检查响应状态码
        status_code = response.status_code
        print(f"状态码: {status_code}")
        
        # 打印响应内容（前200字符）
        response_text = response.text
        print(f"响应内容: {response_text[:200]}..." if len(response_text) > 200 else f"响应内容: {response_text}")
        
        if status_code in [200, 201]:
            # 解析响应数据
            data = response.json()
            
            print(f"✅ 创建成功!")
            
            # 保存测试结果
            results.append({
                'module': module['name'],
                'status': 'success',
                'status_code': status_code,
                'message': '创建成功'
            })
            
        else:
            # 处理错误响应
            error_message = response.text
            print(f"❌ 创建失败: {error_message}")
            
            # 保存测试结果
            results.append({
                'module': module['name'],
                'status': 'error',
                'status_code': status_code,
                'message': error_message
            })
            
    except Exception as e:
        # 处理异常
        print(f"⚠️  异常: {str(e)}")
        
        # 保存测试结果
        results.append({
            'module': module['name'],
            'status': 'exception',
            'message': str(e)
        })
    
    print("-" * 40)

print("\n" + "=" * 60)
print("测试结果汇总")
print("=" * 60)

# 打印汇总结果
success_count = 0
error_count = 0
exception_count = 0
skipped_count = 0

for result in results:
    status = result['status']
    if status == 'success':
        print(f"✅ {result['module']}: 成功 (状态码: {result['status_code']})")
        success_count += 1
    elif status == 'error':
        print(f"❌ {result['module']}: 失败 (状态码: {result['status_code']})")
        error_count += 1
    elif status == 'exception':
        print(f"⚠️  {result['module']}: 异常")
        exception_count += 1
    else:
        print(f"⏭️  {result['module']}: 跳过")
        skipped_count += 1

total_tests = len(results)
print(f"\n总计: {total_tests} 个接口")
print(f"成功: {success_count} 个")
print(f"失败: {error_count} 个")
print(f"异常: {exception_count} 个")
print(f"跳过: {skipped_count} 个")

# 保存详细结果到文件
with open('test_create_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n详细结果已保存到: test_create_results.json")
print("测试完成!")
