# 省钱旅游小程序

## 一、项目概述

一款面向大学生及预算敏感型旅行者的微信小程序，核心目标是帮助用户以最低成本规划旅行。首期核心功能为：**输入出发城市，一键获取所有可直达城市的剩余火车票**，用户从结果中选择心仪目的地，后续逐步扩展更多省钱出行功能。

---

## 二、核心功能

### 2.1 火车票直达查询（已实现）

核心交互流程：**输入出发城市 → 查看所有可直达城市 → 选择目的地查看车次详情**

#### 已实现功能

- ✅ 用户输入出发城市和出发日期，无需指定目的地
- ✅ 系统自动展示从该城市出发所有可直达城市列表
- ✅ 点击目的城市后展开所有车次详情（车次、时间、余票、票价）
- ✅ 支持车次类型筛选（高铁动车/普通列车）
- ✅ 票价智能估算（内置热门线路真实票价 + 基于车次类型的费率估算）
- ✅ 41个热门城市映射，覆盖全国主要城市

### 2.2 智能路线推荐（已实现）

- ✅ 中转换乘方案推荐（如 A→B 直达贵，推荐 A→C→B 更便宜）
- ✅ 对比直达价格，标注"更省钱"或"可到达"标签
- ✅ 展示每段路线的最低价、时长、车次数量

### 2.3 青旅住宿推荐（已实现）

- ✅ 28个城市的经济型住宿/青旅数据
- ✅ 按价格/评分排序，按类型筛选
- ✅ 展示住宿名称、价格、评分、位置、标签

---

## 三、技术方案

### 3.1 整体架构

```
┌──────────────────────────────────────────────────────┐
│                  微信小程序（前端）                      │
│  ┌──────────┐ ┌───────────┐ ┌─────────────────────┐  │
│  │ 出发城市   │ │ 日期选择   │ │ 可直达城市列表       │  │
│  │ + 日期    │ │           │ │ → 点击进入车次详情    │  │
│  └──────────┘ └───────────┘ └─────────────────────┘  │
└────────────────────┬─────────────────────────────────┘
                     │ HTTPS（必须）
┌────────────────────▼─────────────────────────────────┐
│             后端服务（Python Flask）                    │
│  ┌──────────┐ ┌────────────────┐ ┌────────────────┐  │
│  │ 路由控制  │ │ 12306批量查询   │ │ 聚合&缓存       │  │
│  │ (Blueprint)│ │ (并发请求多城市) │ │ (按城市聚合余票) │  │
│  └──────────┘ └────────────────┘ └────────────────┘  │
└────────────────────┬─────────────────────────────────┘
                     │
            ┌────────▼────────┐
            │  12306 数据源    │
            │ (官方接口+聚合数据) │
            └─────────────────┘
```

### 3.2 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | 微信小程序原生框架 | WXML + WXSS + JavaScript |
| 后端 | Python + Flask | 轻量、高效、数据处理能力强 |
| HTTP 客户端 | requests + aiohttp | 同步+异步请求支持 |
| 并发处理 | asyncio + Semaphore | 控制并发数，避免被封 |
| CORS | flask-cors | 跨域请求支持 |
| 生产部署 | gunicorn | WSGI 服务器 |
| 部署平台 | Railway | 免费云平台部署 |

---

## 四、项目目录结构

### 4.1 Python 后端（独立仓库 travel-app-server）

```
server-python/
├── app.py                          # Flask 主入口
├── config.py                       # 配置文件（端口、API Key、缓存等）
├── requirements.txt                # Python 依赖
├── Dockerfile                      # Docker 部署配置
├── Procfile                        # Railway 启动命令
├── start.sh                        # 启动脚本
├── data/
│   ├── city_mapping.json           # 热门城市直达映射表（41个城市）
│   └── hostel_data.json            # 青旅住宿数据（28个城市）
├── routes/
│   ├── ticket.py                   # 车票查询 API 路由
│   ├── city.py                     # 城市列表 API 路由
│   ├── route.py                    # 路线推荐 API 路由
│   └── hostel.py                   # 住宿推荐 API 路由
└── services/
    ├── station_service.py          # 12306 站点代码映射服务
    ├── ticket_service.py           # 火车票查询核心服务
    ├── aggregator.py               # 批量聚合查询服务
    ├── route_service.py            # 中转路线推荐服务
    └── hostel_service.py           # 住宿数据查询服务
```

### 4.2 小程序前端

```
miniprogram/
├── app.js                          # 小程序入口（全局配置 baseUrl）
├── app.json                        # 页面路由配置
├── app.wxss                        # 全局样式
├── project.config.json             # 项目配置（AppID 等）
├── components/
│   └── city-picker/                # 城市选择器组件
├── pages/
│   ├── index/                      # 首页（出发城市 + 日期选择）
│   ├── city-list/                  # 可直达城市列表
│   ├── ticket-list/                # 车次详情列表
│   ├── route-recommend/            # 省钱路线推荐
│   └── hostel-list/                # 住宿推荐
└── utils/
    ├── request.js                  # 网络请求封装（超时60秒）
    └── city-data.js                # 城市数据
```

---

## 五、API 接口文档

### 5.1 快速获取可直达城市列表（推荐，秒级返回）

```
GET /api/ticket/quick-destinations

请求参数：
  from_city    string  出发城市（如"南宁"）

响应示例：
{
  "code": 0,
  "message": "success",
  "data": {
    "fromCity": "南宁",
    "destinations": ["广州", "深圳", "北京", "上海", ...]
  }
}
```

### 5.2 查询某城市车次详情

```
GET /api/ticket/trains

请求参数：
  from_city    string  出发城市（如"北京"）
  to_city      string  目的城市（如"上海"）
  date         string  出发日期（如"2026-05-01"）
  train_type   string  车次类型筛选（可选，all/G-D/K-T-Z）

响应示例：
{
  "code": 0,
  "message": "success",
  "data": {
    "fromStation": "北京南",
    "toStation": "上海虹桥",
    "date": "2026-05-01",
    "tickets": [
      {
        "trainNo": "G1",
        "fromStation": "北京南",
        "toStation": "上海虹桥",
        "startTime": "06:36",
        "arriveTime": "11:48",
        "duration": "05:12",
        "prices": { "二等座": 553, "一等座": 933, "商务座": 1748 },
        "seats": { "二等座": "有", "一等座": 15, "商务座": 8 }
      }
    ]
  }
}
```

### 5.3 获取城市列表

```
GET /api/city/list
```

### 5.4 获取中转路线推荐

```
GET /api/route/transfer

请求参数：
  from_city    string  出发城市
  to_city      string  目的城市
  date         string  出发日期
```

### 5.5 获取住宿推荐

```
GET /api/hostel/list?city=北京&sort_by=price

GET /api/hostel/cities
```

---

## 六、🚀 部署上线完整教程（小白专用）

### 原理说明

微信小程序的运行原理：

```
┌─────────────┐    HTTPS请求     ┌──────────────────┐    HTTP请求    ┌─────────┐
│  用户手机     │ ──────────────→ │  你的后端服务器    │ ────────────→ │  12306   │
│  (小程序前端)  │ ←────────────── │  (Railway云服务器) │ ←──────────── │  接口    │
└─────────────┘    返回JSON数据   └──────────────────┘    返回余票数据  └─────────┘
```

**关键规则：**
1. 小程序前端代码运行在用户手机上（微信客户端）
2. 小程序只能通过 **HTTPS** 协议请求后端服务器
3. 后端服务器地址必须在**微信公众平台**的"服务器域名"中配置
4. 后端服务器负责调用 12306 接口获取数据，再返回给小程序
5. 小程序代码必须通过**微信开发者工具上传**，经**审核通过**后才能发布

---

### 第1步：注册微信小程序正式账号

1. 访问 **https://mp.weixin.qq.com/**
2. 点击 **"立即注册"** → 选择 **"小程序"**
3. 填写未绑定过的邮箱，设置密码，到邮箱激活
4. 主体类型选 **"个人"**（免费，适合学生）
5. 填写身份证信息，微信扫码验证
6. 填写小程序名称、简介、类目（选"工具→出行指南"）

### 第2步：获取 AppID

1. 登录 **https://mp.weixin.qq.com/**
2. 左侧 **"开发"** → **"开发管理"**
3. 在 **"开发者ID"** 区域找到 **AppID**（格式如 `wx1234567890abcdef`）

### 第3步：部署后端到 Railway

#### 3.1 创建 GitHub 仓库

1. 访问 **https://github.com/new**
2. 仓库名填 `travel-app-server`
3. 选择 **Public**
4. **不要**勾选 "Add a README"
5. 点击 **"Create repository"**

#### 3.2 推送代码到 GitHub

```bash
cd server-python
git init
git add -A
git commit -m "省钱旅游小程序后端服务"
git remote add origin https://github.com/你的用户名/travel-app-server.git
git branch -M main
git push -u origin main
```

#### 3.3 在 Railway 上部署

1. 访问 **https://railway.app/** → 用 GitHub 登录
2. 点击 **"New Project"** → **"Deploy from GitHub repo"**
3. 选择 `travel-app-server` 仓库
4. 点击服务 → **"Settings"** → **"Environment"** 添加变量：
   - `API_KEY` = `你的聚合数据API Key`
5. 点击 **"Deployments"** → **"Redeploy"**
6. 等待 2-3 分钟，部署成功后获得域名（如 `https://travel-app-server-production-xxxx.up.railway.app`）

#### 3.4 验证部署

在浏览器中访问：
```
https://你的域名/
https://你的域名/api/city/list
https://你的域名/api/ticket/quick-destinations?from_city=南宁
```
看到 JSON 数据说明部署成功。

### 第4步：配置微信公众平台

1. 登录 **https://mp.weixin.qq.com/**
2. 左侧 **"开发"** → **"开发管理"** → **"开发设置"**
3. 找到 **"服务器域名"** → 点击 **"修改"**
4. 在 **"request合法域名"** 中添加：
```
https://travel-app-server-production-xxxx.up.railway.app
```
5. 点击 **"保存并提交"**

> ⚠️ **这一步非常重要！** 不配置服务器域名，手机上的小程序无法请求后端，会报"加载失败"。

### 第5步：修改小程序配置

1. 打开 `miniprogram/app.js`
2. 修改 `baseUrl` 为你的 Railway 域名：
```javascript
globalData: {
  baseUrl: 'https://travel-app-server-production-xxxx.up.railway.app/api',
}
```
3. 打开 `miniprogram/project.config.json`
4. 修改 `appid` 为你的正式 AppID：
```json
{
  "appid": "wx你的正式AppID"
}
```

### 第6步：上传代码并审核

1. 打开微信开发者工具，导入项目
2. 确认 AppID 是正式的（不是测试号）
3. 点击 **"上传"** 按钮
4. 填写版本号 `1.0.0`，备注 `首次发布`
5. 登录 **https://mp.weixin.qq.com/**
6. 左侧 **"管理"** → **"版本管理"**
7. 在 **"开发版本"** 中点击 **"提交审核"**
8. 等待 1-3 天审核通过

### 第7步：发布上线

1. 审核通过后，在 **"版本管理"** 中点击 **"发布"**
2. 你的小程序就可以在微信中搜索到了！

---

## 七、🔄 以后如何更新代码

### 更新后端代码

```bash
# 1. 修改代码后，进入后端目录
cd server-python

# 2. 提交并推送到 GitHub
git add -A
git commit -m "描述你修改了什么"
git push origin main

# 3. Railway 会自动检测到更新并重新部署（约2-3分钟）
# 如果没有自动部署，去 Railway 点击 "Redeploy"
```

### 更新小程序前端代码

1. 在微信开发者工具中修改代码
2. 点击 **"上传"** 按钮
3. 填写新版本号（如 `1.0.1`）
4. 登录 **https://mp.weixin.qq.com/**
5. **"管理"** → **"版本管理"** → 提交审核
6. 审核通过后发布

### 更新流程图

```
修改代码 → 测试 → 提交Git → 推送GitHub → Railway自动部署 → 上传小程序 → 提交审核 → 发布
```

---

## 八、🔧 部署新小程序的通用步骤

如果你以后要开发并上线其他小程序，按以下步骤操作：

### 1. 后端部署

| 步骤 | 操作 |
|------|------|
| ① | 把后端代码推送到 GitHub 仓库 |
| ② | 在 Railway 创建新项目，关联仓库 |
| ③ | 配置环境变量（API Key、PORT等） |
| ④ | 等待部署完成，获取域名 |
| ⑤ | 验证 API 是否正常 |

### 2. 小程序上线

| 步骤 | 操作 |
|------|------|
| ① | 注册微信小程序正式账号 |
| ② | 获取 AppID |
| ③ | 在微信公众平台配置服务器域名 |
| ④ | 修改小程序的 baseUrl 和 AppID |
| ⑤ | 用微信开发者工具上传代码 |
| ⑥ | 提交审核 |
| ⑦ | 审核通过后发布 |

### 3. 常见问题排查

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| 手机上"加载失败" | 服务器域名未配置 | 在微信公众平台添加 request 合法域名 |
| 开发者工具超时 | 后端查询太慢 | 使用 quick-destinations 接口，减少查询量 |
| Railway 部署失败 | Dockerfile 配置错误 | 确保使用 `$PORT` 环境变量，不硬编码端口 |
| 上传按钮灰色 | 使用了测试号 | 注册正式小程序账号，使用正式 AppID |
| API 返回 Cannot GET | 路由未注册 | 检查 Flask Blueprint 是否正确注册 |
| 12306 查询失败 | 反爬机制 | 使用多端点切换 + Cookie 缓存 + 请求间隔 |

---

## 九、⚠️ 部署踩坑记录

### 坑1：Railway 子目录部署问题

**问题**：代码在 `travel.app/server-python/` 子目录，Railway 找不到启动文件
**解决**：创建独立的 `travel-app-server` GitHub 仓库，所有文件放在根目录

### 坑2：python-dotenv 导致 Railway 崩溃

**问题**：`load_dotenv()` 在没有 `.env` 文件时可能导致应用崩溃
**解决**：移除 `python-dotenv` 依赖，直接使用 `os.environ.get()` 读取环境变量

### 坑3：Dockerfile 端口硬编码

**问题**：`EXPOSE 3000` 和 `ENV PORT=3000` 导致 Railway 无法正确路由
**解决**：移除硬编码端口，使用 `${PORT:-3000}` 动态读取 Railway 分配的端口

### 坑4：Docker CMD 中 $PORT 不展开

**问题**：`CMD ["gunicorn", "--bind", "0.0.0.0:$PORT"]` 中 `$PORT` 不会展开
**解决**：使用 `ENTRYPOINT ["sh", "-c", "exec gunicorn app:app --bind 0.0.0.0:${PORT:-3000} --timeout 120"]`

### 坑5：查询30+城市余票超时

**问题**：首页查询所有城市余票需要30-60秒，小程序超时
**解决**：首页用 `quick-destinations` 接口只返回城市列表（秒级），用户点击具体城市后再查余票

### 坑6：真机无法请求后端

**问题**：手机上小程序显示"加载失败"
**解决**：必须在微信公众平台配置 request 合法域名（HTTPS）

---

## 十、注意事项

1. **合规性**：12306 数据仅供学习使用，不得用于商业倒票等违法行为
2. **请求频率**：后端并发数 ≤ 3，请求间隔 ≥ 200ms，避免对 12306 服务器造成压力
3. **数据缓存**：相同查询条件在 5 分钟内返回缓存数据，减少重复请求
4. **隐私安全**：不收集用户个人敏感信息，API Key 等密钥不可提交到代码仓库
5. **反爬处理**：12306 接口需携带有效 Cookie 和 User-Agent，多端点自动切换
6. **HTTPS 必须**：微信小程序真机只允许 HTTPS 请求，开发工具可关闭校验
