import os
import json
import requests
from dotenv import load_dotenv

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

# 测试模块列表
modules = [
    {'name': 'Contacts', 'endpoint': '/contacts'},
    {'name': 'Notes', 'endpoint': '/notes'},
    {'name': 'Activities', 'endpoint': '/activities'},
    {'name': 'Reminders', 'endpoint': '/reminders'},
    {'name': 'Tasks', 'endpoint': '/tasks'},
    {'name': 'Tags', 'endpoint': '/tags'}
]

# 测试结果
results = []

print("开始测试 Monica API 接口...")
print(f"基础URL: {BASE_URL}")
print("=" * 60)

# 测试每个模块
for module in modules:
    print(f"\n测试模块: {module['name']}")
    print(f"Endpoint: {module['endpoint']}")
    print("-" * 40)
    
    try:
        # 发送GET请求
        response = requests.get(
            f"{BASE_URL}{module['endpoint']}",
            headers=headers,
            params={'limit': 5, 'page': 1}
        )
        
        # 检查响应状态码
        status_code = response.status_code
        print(f"状态码: {status_code}")
        
        # 打印响应内容（前200字符）
        response_text = response.text
        print(f"响应内容: {response_text[:200]}..." if len(response_text) > 200 else f"响应内容: {response_text}")
        
        if status_code == 200:
            try:
                # 解析响应数据
                data = response.json()
                
                # 提取关键信息
                total = data.get('meta', {}).get('total', 0)
                current_page = data.get('meta', {}).get('current_page', 1)
                per_page = data.get('meta', {}).get('per_page', 0)
                items_count = len(data.get('data', []))
                
                print(f"成功获取数据!")
                print(f"总记录数: {total}")
                print(f"当前页码: {current_page}")
                print(f"每页数量: {per_page}")
                print(f"返回项目数: {items_count}")
                
                # 保存测试结果
                results.append({
                    'module': module['name'],
                    'status': 'success',
                    'status_code': status_code,
                    'total': total,
                    'message': f'成功获取 {items_count} 条记录'
                })
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}")
                # 保存测试结果
                results.append({
                    'module': module['name'],
                    'status': 'error',
                    'status_code': status_code,
                    'message': f'JSON解析错误: {str(e)}'
                })
            
        else:
            # 处理错误响应
            error_message = response.text
            print(f"错误: {error_message}")
            
            # 保存测试结果
            results.append({
                'module': module['name'],
                'status': 'error',
                'status_code': status_code,
                'message': error_message
            })
            
    except Exception as e:
        # 处理异常
        print(f"异常: {str(e)}")
        
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
for result in results:
    status = result['status']
    if status == 'success':
        print(f"✅ {result['module']}: 成功 (状态码: {result['status_code']}, 总记录: {result['total']})")
    elif status == 'error':
        print(f"❌ {result['module']}: 失败 (状态码: {result['status_code']})")
    else:
        print(f"⚠️  {result['module']}: 异常")

# 统计成功和失败的数量
success_count = sum(1 for r in results if r['status'] == 'success')
error_count = sum(1 for r in results if r['status'] == 'error')
exception_count = sum(1 for r in results if r['status'] == 'exception')

total_tests = len(results)
print(f"\n总计: {total_tests} 个接口")
print(f"成功: {success_count} 个")
print(f"失败: {error_count} 个")
print(f"异常: {exception_count} 个")

# 保存详细结果到文件
with open('test_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n详细结果已保存到: test_results.json")
print("测试完成!")
