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

print("测试 Monica API 根路径...")
print(f"基础URL: {BASE_URL}")
print("=" * 60)

# 测试不同的路径
paths_to_test = [
    '',
    '/',
    '/v1',
    '/v1/',
    '/contacts',
    '/contacts/',
    '/api',
    '/api/',
    '/api/v1',
    '/api/v1/'
]

for path in paths_to_test:
    test_url = f"{BASE_URL}{path}"
    print(f"\n测试路径: {test_url}")
    print("-" * 40)
    
    try:
        response = requests.get(test_url, headers=headers)
        status_code = response.status_code
        print(f"状态码: {status_code}")
        
        # 打印响应内容（前100字符）
        response_text = response.text
        print(f"响应内容: {response_text[:100]}..." if len(response_text) > 100 else f"响应内容: {response_text}")
        
        # 尝试解析JSON
        try:
            data = response.json()
            print("✓ 响应是有效的JSON")
        except json.JSONDecodeError:
            print("✗ 响应不是有效的JSON")
            
    except Exception as e:
        print(f"异常: {str(e)}")
    
    print("-" * 40)

print("\n测试完成!")
