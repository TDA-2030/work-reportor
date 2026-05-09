# Work Reportor 项目开发计划：Web 控制台版本

## 1. 项目目标

Work Reportor 是一个基于电脑行为采集的自动工作日报/周报生成工具。

新版目标改为：

> 后台采集电脑行为，浏览器作为统一操作入口。

用户不需要使用命令行，所有配置、查看、统计、报告生成和 AI 总结都在网页中完成。

核心目标：

* 自动采集电脑工作行为
* 使用浏览器展示每日/每周工作轨迹
* 支持网页配置监听目录、项目规则、分类规则
* 自动生成日报/周报
* 支持 AI 总结
* 默认本地运行，保护隐私

---

## 2. 总体架构

推荐架构：

```txt
Work Reportor Desktop App
│
├── 后台采集服务
│   ├── 窗口采集器
│   ├── 文件监听器
│   ├── Git 采集器
│   └── 数据写入器
│
├── 本地 Web 服务
│   ├── REST API
│   ├── WebSocket 实时事件推送
│   └── 报告生成接口
│
├── 本地数据库
│   └── SQLite
│
└── 浏览器 Web 控制台
    ├── 首页仪表盘
    ├── 时间线页面
    ├── 项目统计页面
    ├── 文件活动页面
    ├── Git 活动页面
    ├── 报告生成页面
    └── 设置页面
```

---

## 3. 技术栈选择

### 后端

推荐：

```txt
Python + FastAPI
```

原因：

* 写 API 很快
* 和现有 Python 采集逻辑结合方便
* 支持 WebSocket
* 适合本地服务

依赖：

```txt
fastapi
uvicorn
pydantic
sqlalchemy
sqlite-utils
pyyaml
watchdog
psutil
pywin32
GitPython
openai
```

---

### 前端

推荐：

```txt
Vue 3 + Vite + TypeScript
```

或者：

```txt
React + Vite + TypeScript
```

如果想快速漂亮，推荐：

```txt
Vue 3 + Element Plus
```

原因：

* 表格、表单、弹窗、菜单组件齐全
* 做管理后台速度快
* 很适合配置型工具

---

### 桌面启动方式

第一版：

```txt
启动 Python 后端服务，自动打开浏览器
```

后续正式版：

```txt
pystray 系统托盘 + 本地 Web 控制台
```

最终可以考虑：

```txt
Tauri 壳 + Rust 文件监听 Agent + Web 前端
```

---

## 4. 新项目目录结构

```txt
work-reportor/
├── README.md
├── PLAN.md
├── config.yaml
├── requirements.txt
├── main.py
│
├── backend/
│   ├── app.py
│   ├── api/
│   │   ├── dashboard_api.py
│   │   ├── activity_api.py
│   │   ├── report_api.py
│   │   ├── settings_api.py
│   │   └── websocket_api.py
│   │
│   ├── collectors/
│   │   ├── window_collector.py
│   │   ├── file_collector.py
│   │   └── git_collector.py
│   │
│   ├── core/
│   │   ├── event.py
│   │   ├── classifier.py
│   │   ├── project_detector.py
│   │   ├── aggregator.py
│   │   └── scheduler.py
│   │
│   ├── storage/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   │
│   ├── reporter/
│   │   ├── daily_report.py
│   │   ├── weekly_report.py
│   │   └── ai_reporter.py
│   │
│   └── utils/
│       ├── time_utils.py
│       └── path_utils.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/
│       │   └── index.ts
│       ├── api/
│       │   ├── dashboard.ts
│       │   ├── activity.ts
│       │   ├── report.ts
│       │   └── settings.ts
│       ├── views/
│       │   ├── Dashboard.vue
│       │   ├── Timeline.vue
│       │   ├── Projects.vue
│       │   ├── Files.vue
│       │   ├── Git.vue
│       │   ├── Reports.vue
│       │   └── Settings.vue
│       └── components/
│           ├── StatCard.vue
│           ├── ActivityTimeline.vue
│           ├── ProjectHeatmap.vue
│           └── ReportPreview.vue
│
├── data/
│   └── work-reportor.db
│
└── reports/
    ├── daily/
    └── weekly/
```

---

## 5. Web 页面设计

## 5.1 首页仪表盘 Dashboard

用途：打开网页后第一眼看到今天的工作状态。

展示内容：

* 今日总活跃时间
* 今日主要项目
* 今日主要工作类型
* 当前正在使用的软件
* 当前正在编辑/活跃的项目
* 最近文件变化
* 最近 Git 提交

页面布局：

```txt
┌────────────────────────────────────┐
│ Work Reportor 今日概览                  │
├──────────┬──────────┬──────────────┤
│ 活跃时间 │ 专注时间 │ 主要项目      │
├──────────┴──────────┴──────────────┤
│ 工作类型分布图                      │
├────────────────────────────────────┤
│ 项目活跃度排行                      │
├────────────────────────────────────┤
│ 实时活动流                          │
└────────────────────────────────────┘
```

---

## 5.2 时间线页面 Timeline

用途：查看一天内电脑行为轨迹。

展示内容：

```txt
09:00 - 09:45  VSCode       PulseMeter 开发
09:45 - 10:10  Chrome       技术调研
10:10 - 11:20  VSCode       PulseMeter 开发
14:00 - 15:30  Word/Typora  文档整理
```

功能：

* 按日期筛选
* 按项目筛选
* 按工作类型筛选
* 查看窗口标题
* 查看对应文件事件

---

## 5.3 项目统计页面 Projects

用途：看这一周主要精力花在哪些项目上。

展示内容：

* 项目活跃时间排行
* 项目文件修改次数
* 项目 Git 提交数量
* 项目活跃趋势图

示例：

```txt
PulseMeter    12.5h   83 次文件修改   6 次提交
Thesis         5.2h   31 次文件修改   0 次提交
Work Reportor      3.8h   24 次文件修改   2 次提交
```

---

## 5.4 文件活动页面 Files

用途：查看文件监听记录。

展示内容：

* 文件路径
* 事件类型
* 所属项目
* 文件扩展名
* 发生时间

功能：

* 按项目筛选
* 按文件类型筛选
* 忽略某个文件/目录
* 添加到忽略规则

---

## 5.5 Git 活动页面 Git

用途：查看开发成果。

展示内容：

* 仓库名称
* commit message
* 提交时间
* 修改文件数
* 增删行数量

功能：

* 扫描 Git 仓库
* 手动刷新
* 选择是否写入报告

---

## 5.6 报告生成页面 Reports

这是核心页面。

功能：

* 选择日报/周报
* 选择时间范围
* 选择报告风格
* 预览结构化数据
* 生成 Markdown 报告
* 调用 AI 生成正式周报
* 支持复制、下载、保存

报告风格：

```txt
正式周报
技术总结
日报简版
项目复盘
```

页面流程：

```txt
选择时间范围
    ↓
系统聚合行为数据
    ↓
展示可编辑摘要
    ↓
点击生成报告
    ↓
预览 Markdown
    ↓
复制/下载/保存
```

---

## 5.7 设置页面 Settings

所有配置都放到网页里，不再手写 config.yaml。

设置项：

### 监听目录

* 添加目录
* 删除目录
* 启用/禁用目录监听

### 项目规则

* 项目名称
* 项目路径
* 项目类型
* 是否启用 Git 扫描

### 忽略规则

* 忽略目录
* 忽略扩展名
* 忽略文件名关键词

### 分类规则

* 应用程序分类
* 文件扩展名分类
* 窗口标题关键词分类

### AI 设置

* API Key
* 模型名称
* 报告语言
* 报告风格

---

## 6. 后端 API 设计

### Dashboard API

```txt
GET /api/dashboard/today
GET /api/dashboard/week
```

返回：

```json
{
  "active_time": 18200,
  "top_projects": [
    {"name": "PulseMeter", "duration": 7200},
    {"name": "Work Reportor", "duration": 3600}
  ],
  "categories": [
    {"name": "开发", "duration": 10800},
    {"name": "调研", "duration": 2400}
  ],
  "recent_events": []
}
```

---

### Activity API

```txt
GET /api/activity/timeline?date=2026-05-09
GET /api/activity/files?date=2026-05-09
GET /api/activity/windows?date=2026-05-09
```

---

### Projects API

```txt
GET /api/projects
GET /api/projects/{project_name}/stats
POST /api/projects
PUT /api/projects/{project_name}
DELETE /api/projects/{project_name}
```

---

### Reports API

```txt
POST /api/reports/preview
POST /api/reports/generate
POST /api/reports/generate-ai
GET /api/reports/list
GET /api/reports/{report_id}
```

---

### Settings API

```txt
GET /api/settings
PUT /api/settings
POST /api/settings/watch-dirs
DELETE /api/settings/watch-dirs/{id}
POST /api/settings/ignore-rules
DELETE /api/settings/ignore-rules/{id}
```

---

### WebSocket API

```txt
WS /ws/events
```

推送实时事件：

```json
{
  "type": "file_modified",
  "project": "PulseMeter",
  "path": "D:/Projects/PulseMeter/main.py",
  "timestamp": "2026-05-09 10:15:00"
}
```

---

## 7. 数据库设计

### window_events

```sql
CREATE TABLE window_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name TEXT,
    process_name TEXT,
    window_title TEXT,
    category TEXT,
    project TEXT,
    start_time TEXT,
    end_time TEXT,
    duration INTEGER
);
```

### file_events

```sql
CREATE TABLE file_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    file_path TEXT,
    file_name TEXT,
    file_ext TEXT,
    project TEXT,
    category TEXT,
    timestamp TEXT
);
```

### git_events

```sql
CREATE TABLE git_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT,
    repo_path TEXT,
    commit_hash TEXT,
    message TEXT,
    timestamp TEXT,
    files_changed INTEGER,
    insertions INTEGER,
    deletions INTEGER
);
```

### projects

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    path TEXT,
    type TEXT,
    enable_git INTEGER DEFAULT 1,
    created_at TEXT
);
```

### settings

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

### ignore_rules

```sql
CREATE TABLE ignore_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type TEXT,
    pattern TEXT,
    enabled INTEGER DEFAULT 1
);
```

---

## 8. 采集器设计

## 8.1 窗口采集器

职责：

* 获取当前前台窗口
* 获取窗口标题
* 获取进程名
* 合并连续相同窗口
* 写入数据库
* 通过 WebSocket 推送当前活动

---

## 8.2 文件监听器

职责：

* 根据网页设置的监听目录启动监听
* 捕获 created / modified / deleted / moved 事件
* 应用忽略规则
* 合并短时间重复事件
* 写入数据库
* 推送实时文件活动

性能策略：

* 不监听系统盘根目录
* 默认忽略大缓存目录
* 文件事件先进入队列
* 后台批量写入数据库
* 对同一个文件短时间内的 modified 事件进行合并

---

## 8.3 Git 采集器

职责：

* 根据项目路径扫描 Git 仓库
* 定时获取最近 commit
* 避免重复写入
* 为报告提供开发成果依据

---

## 9. 报告生成逻辑

报告生成不直接使用原始事件，而是先聚合成结构化摘要。

聚合内容：

```json
{
  "range": "2026-05-04 ~ 2026-05-09",
  "projects": [
    {
      "name": "PulseMeter",
      "active_time": "12.5h",
      "file_changes": 83,
      "main_files": ["main.py", "tcp_server.py", "README.md"],
      "commits": [
        "fix: improve reconnect logic",
        "feat: add temperature monitor"
      ]
    }
  ],
  "categories": {
    "开发": "18h",
    "文档": "5h",
    "调研": "3h"
  }
}
```

报告生成页面允许用户在 AI 生成前编辑摘要，避免系统误判。

---

## 10. AI 总结 Prompt

```txt
你是一个工作周报助手。请根据下面的结构化工作记录，生成一份简洁、正式、适合提交给领导的中文周报。

要求：
1. 不要编造没有出现的信息
2. 按项目归纳
3. 输出包括：本周工作内容、问题与优化、下周计划
4. 语气正式，不要空洞
5. 如果数据不足，请保守总结

工作记录：
{{data}}
```

---

## 11. 本地启动流程

第一版启动方式：

```bash
python main.py
```

启动后自动执行：

```txt
1. 初始化数据库
2. 加载配置
3. 启动采集器
4. 启动 FastAPI 服务
5. 自动打开浏览器 http://127.0.0.1:8765
```

---

## 12. 页面路由设计

```txt
/              首页仪表盘
/timeline      时间线
/projects      项目统计
/files         文件活动
/git           Git 活动
/reports       报告生成
/settings      设置
```

---

## 13. 第一版开发顺序

### Sprint 1：后端基础

* [ ] 创建 FastAPI 项目
* [ ] 初始化 SQLite
* [ ] 实现 settings API
* [ ] 实现 dashboard API
* [ ] 实现静态前端托管

### Sprint 2：采集器接入

* [ ] 实现窗口采集器
* [ ] 实现文件监听器
* [ ] 实现事件写入数据库
* [ ] 实现 WebSocket 实时事件推送

### Sprint 3：前端页面

* [ ] 首页仪表盘
* [ ] 时间线页面
* [ ] 文件活动页面
* [ ] 设置页面

### Sprint 4：项目识别和统计

* [ ] 项目规则配置
* [ ] 项目自动识别
* [ ] 工作类型分类
* [ ] 项目统计页面

### Sprint 5：报告生成

* [ ] 报告预览接口
* [ ] 报告生成页面
* [ ] Markdown 导出
* [ ] AI 周报生成

---

## 14. MVP 最小可运行目标

第一版做到：

```txt
打开浏览器后可以看到：

1. 今天使用了哪些软件
2. 哪些项目最活跃
3. 哪些文件被修改
4. 最近有哪些 Git 提交
5. 点击按钮生成一份 Markdown 日报/周报
```

这就是 Work Reportor Web 版的第一个可用版本。

---

## 15. 隐私原则

Work Reportor 默认：

* 不记录键盘输入
* 不截图
* 不读取聊天内容
* 不读取文件正文
* 不上传原始文件
* 数据默认保存在本机 SQLite
* AI 总结前展示将要发送的数据摘要

---

## 16. 后续增强方向

### 桌面化

* 系统托盘运行
* 开机自启
* 后台静默采集
* 一键打开 Web 控制台

### 性能优化

* 文件监听 Agent 独立为 Rust / Go 服务
* 批量写数据库
* 事件去重队列
* 前端按需分页加载

### 智能增强

* 自动识别项目
* 自动识别工作主题
* 自动发现本周完成事项
* 自动生成下周计划草稿

### 可视化增强

* 项目热力图
* 工作类型饼图
* 每日时间分布图
* 专注时间曲线
* 上下文切换次数统计
