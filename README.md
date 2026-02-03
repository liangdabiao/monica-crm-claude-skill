# Monica CRM 集成 SKILL

一个功能完整的 Monica Personal CRM API 集成工具，用于管理联系人、笔记、活动、任务、提醒和标签。
聊天就是CRM - claude skill 做一个crm，直接通讯聊天管理crm - 在claude code , openclaw 方便使用
claude code , openclaw 是有记忆功能，但是crm往往比较复杂和严肃，如果有一个系统的crm整理客户信息，显然会更好 。所以有这个项目。直接聊天就是CRM - claude skill 做一个crm。

## 项目结构

```
.
├── .claude/
│   └── skills/
│       └── crm/
│           ├── references/         # API 参考文档
│           │   └── api.md
│           ├── scripts/            # Python 脚本
│           │   ├── __pycache__/
│           │   └── monica_api.py   # 核心 API 客户端
│           ├── monica-api-documentation.md  # Monica API 文档
│           └── skill.md            # 技能描述文件
├── .env.example                    # 环境变量示例文件
├── .gitignore                      # Git 忽略文件
└── README.md                       # 项目说明文件
```

## 功能特性

- **自动配置检测**：自动检测并加载 `.env` 文件
- **完整的 API 覆盖**：支持所有 Monica CRM API 端点
- **智能联系人管理**：查找、创建、更新联系人
- **丰富的字段支持**：添加电话、邮箱等联系人字段
- **笔记管理**：为联系人添加和管理笔记
- **活动跟踪**：记录与联系人的互动活动
- **任务管理**：创建和跟踪任务
- **提醒功能**：设置重要提醒
- **标签系统**：为联系人添加标签进行分类
- **命令行界面**：方便的 CLI 工具
- **Python API**：可集成到其他项目中

## 快速开始

### 1. 安装依赖

```bash
申请一个免费crm: https://app.monicahq.com
```

### 2. 配置环境变量

复制 `.env.example` 文件并填写你的 Monica API 令牌：

```bash
cp .env.example .env
# 编辑 .env 文件，填写你的 API 令牌
```

**.env 文件示例：**

```env
# Monica CRM Configuration
# Get your API token from: https://app.monicahq.com/settings
MONICA_API_TOKEN=your_monica_api_token_here
MONICA_BASE_URL=https://app.monicahq.com/api

# Rate Limiting (Optional - Monica API limit is 60 req/min)
# RATE_LIMIT_REQUESTS=60
# RATE_LIMIT_PERIOD=60
```

### 3. 基本使用

#### 命令行界面

```bash
# 列出所有联系人
python .claude/skills/crm/scripts/monica_api.py contacts

# 添加新联系人（带电话和备注）
python .claude/skills/crm/scripts/monica_api.py add-contact "John Doe" --phone "1234567890" --note "新客户"

# 查找或创建联系人
python .claude/skills/crm/scripts/monica_api.py find-or-create "Jane Smith" --phone "9876543210"

# 添加笔记到联系人
python .claude/skills/crm/scripts/monica_api.py add-note 123 "会议笔记"

# 管理任务
python .claude/skills/crm/scripts/monica_api.py tasks list
python .claude/skills/crm/scripts/monica_api.py tasks create "跟进客户" --due-date "2025-01-31"

# 管理提醒
python .claude/skills/crm/scripts/monica_api.py reminders list
python .claude/skills/crm/scripts/monica_api.py reminders create "生日提醒" --date "2025-02-15" --contact-id 123

# 管理标签
python .claude/skills/crm/scripts/monica_api.py tags list
python .claude/skills/crm/scripts/monica_api.py tags create "VIP"
python .claude/skills/crm/scripts/monica_api.py tags set 123 "VIP" "客户"
```

#### Python API

```python
from .claude.skills.crm.scripts.monica_api import MonicaAPI

# 自动从 .env 加载配置
api = MonicaAPI()

# 获取联系人列表
contacts = api.list_contacts(limit=50, query="john")

# 查找联系人
contact = api.find_contact("John Doe")

# 查找或创建联系人
contact, created = api.find_or_create_contact("John", "Doe")

# 创建新联系人
new_contact = api.create_contact(first_name="Jane", gender_id=2)

# 添加联系人字段（电话、邮箱等）
api.set_contact_field(contact['id'], 'phone', '1234567890', is_favorite=True)
api.set_contact_field(contact['id'], 'email', 'jane@example.com')

# 添加笔记
note = api.create_note(body="会议笔记", contact_id=contact['id'])

# 创建活动
activity = api.create_activity(
    activity_type_id=2,
    summary="电话会议",
    happened_at="2025-01-15",
    contacts=[contact['id']]
)

# 创建任务
task = api.create_task(
    title="跟进项目",
    due_date="2025-01-31",
    contact_id=contact['id']
)

# 创建提醒
reminder = api.create_reminder(
    title="项目截止提醒",
    date="2025-01-30",
    contact_id=contact['id']
)

# 管理标签
api.set_contact_tags(contact_id=contact['id'], tags=['VIP', '客户'])
```

## 核心功能

### 联系人管理

- **列出联系人**：支持分页、搜索和排序
- **查找联系人**：通过名称查找联系人
- **创建联系人**：添加新联系人
- **更新联系人**：修改联系人信息
- **删除联系人**：移除联系人
- **添加联系人字段**：添加电话、邮箱等字段

### 笔记管理

- **添加笔记**：为联系人添加笔记
- **获取笔记**：查看联系人的笔记

### 活动管理

- **创建活动**：记录与联系人的互动
- **列出活动**：查看所有活动

### 任务管理

- **创建任务**：设置待办事项
- **列出任务**：查看所有任务
- **更新任务**：修改任务状态
- **删除任务**：移除任务

### 提醒管理

- **创建提醒**：设置重要提醒
- **列出提醒**：查看所有提醒
- **获取提醒**：查看提醒详情
- **删除提醒**：移除提醒

### 标签管理

- **创建标签**：添加新标签
- **列出标签**：查看所有标签
- **为联系人设置标签**：分类联系人
- **删除标签**：移除标签

## 环境变量配置

| 变量名 | 描述 | 必填 | 默认值 |
|-------|------|------|--------|
| `MONICA_API_TOKEN` | Monica CRM API 令牌 | 是 | 无 |
| `MONICA_BASE_URL` | Monica API 基础 URL | 是 | `https://app.monicahq.com/api` |
| `RATE_LIMIT_REQUESTS` | 速率限制请求数 | 否 | 60 |
| `RATE_LIMIT_PERIOD` | 速率限制周期（秒） | 否 | 60 |

## 命令行参考

### 联系人命令

```bash
# 列出联系人
python .claude/skills/crm/scripts/monica_api.py contacts [--limit LIMIT] [--page PAGE] [--query QUERY] [--sort SORT]

# 查找联系人
python .claude/skills/crm/scripts/monica_api.py find NAME

# 获取联系人详情
python .claude/skills/crm/scripts/monica_api.py get ID [--with-fields]

# 添加联系人（查找或创建）
python .claude/skills/crm/scripts/monica_api.py add-contact NAME [--phone PHONE] [--email EMAIL] [--note NOTE] [--gender GENDER]

# 查找或创建联系人
python .claude/skills/crm/scripts/monica_api.py find-or-create NAME [--phone PHONE] [--note NOTE]

# 添加笔记到联系人
python .claude/skills/crm/scripts/monica_api.py add-note CONTACT_ID BODY
```

### 任务命令

```bash
# 列出任务
python .claude/skills/crm/scripts/monica_api.py tasks list [--limit LIMIT] [--page PAGE]

# 创建任务
python .claude/skills/crm/scripts/monica_api.py tasks create TITLE --due-date DATE [--contact-id CONTACT_ID]

# 删除任务
python .claude/skills/crm/scripts/monica_api.py tasks delete TASK_ID
```

### 提醒命令

```bash
# 列出提醒
python .claude/skills/crm/scripts/monica_api.py reminders list [--limit LIMIT] [--page PAGE]

# 创建提醒
python .claude/skills/crm/scripts/monica_api.py reminders create TITLE --date DATE [--contact-id CONTACT_ID]

# 删除提醒
python .claude/skills/crm/scripts/monica_api.py reminders delete REMINDER_ID
```

### 标签命令

```bash
# 列出标签
python .claude/skills/crm/scripts/monica_api.py tags list [--limit LIMIT] [--page PAGE]

# 创建标签
python .claude/skills/crm/scripts/monica_api.py tags create NAME

# 删除标签
python .claude/skills/crm/scripts/monica_api.py tags delete TAG_ID

# 为联系人设置标签
python .claude/skills/crm/scripts/monica_api.py tags set CONTACT_ID TAG1 TAG2 ...
```

## 性别 ID 参考

- `1` - 男性
- `2` - 女性
- `3` - 非二元性别
- `4` - 其他

## 已知问题和解决方案

### 笔记 API 问题

**问题**：Monica Notes API (`POST /notes/`) 存在一个 bug，当指定 `contact_id` 时，它返回的是不同联系人的笔记数据。请求会成功（HTTP 200），但笔记不会与预期的联系人关联。

**解决方案**：使用联系人的 `description` 字段来存储笔记，而不是使用 Notes API：

```python
from .claude.skills.crm.scripts.monica_api import MonicaAPI
api = MonicaAPI()

# 更新联系人描述（可靠方法）
api.update_contact(contact_id, description="会议笔记内容")
```

### 联系人字段 API 问题

**问题**：Monica Contact Fields API 要求 `contact field type id` 字段，但此 ID 在不同 Monica 实例中可能不同。

**解决方案**：目前，`add-contact` 和 `find-or-create` 命令会将电话号码和邮箱添加到笔记中，而不是使用 Contact Fields API。

## 技术细节

- **自动配置检测**：自动检测并加载当前或父目录中的 `.env` 文件
- **API URL 处理**：自动处理 `/api` 后缀，只需使用基础 URL
- **日期格式**：活动使用 `YYYY-MM-DD` 格式
- **联系人 ID**：整数类型，作为数字传递，而非字符串
- **幂等操作**：`add-contact` 命令会自动查找现有联系人或创建新联系人

## 依赖

- **Python 3.7+**
- **可选依赖**：
  - `requests`：用于 HTTP 请求
  - `python-dotenv`：用于加载环境变量

## 安全注意事项

- **API 令牌**：不要将你的 Monica API 令牌提交到版本控制系统
- **环境变量**：使用 `.env` 文件存储敏感信息，并确保 `.env` 文件被添加到 `.gitignore`
- **速率限制**：Monica API 限制为每分钟 60 个请求，请合理使用

## 许可证

MIT 许可证

## 贡献

欢迎提交问题和拉取请求！

## 鸣谢

- [Monica Personal CRM](https://www.monicahq.com/) - 优秀的个人 CRM 系统
- [Python](https://www.python.org/) - 强大的编程语言

## 联系方式

如果有任何问题或建议，请随时联系我们。
