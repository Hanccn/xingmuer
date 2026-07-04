# 行木儿

> 出发前的准备，从这里开始就够了。

**行木儿**是一个面向中国自由行用户的旅游规划决策工具，填补「小红书种草」和「携程下单」之间的决策辅助层。

🔗 在线原型：[hanccn.github.io/xingmuer](https://hanccn.github.io/xingmuer/)

---

## 为什么做这个

自由行用户出发前通常要横跳 6-8 个 App：小红书查攻略 → 携程看酒店 → 高德查距离 → 马蜂窝看点评 → 微信问朋友 → 备忘录写行程。信息散落各处，最关键的三个决策——**住哪里、怎么走、先去哪**——反而没人帮你。

行木儿只做一件事：**把你选中的景点，变成一条能导出到手机的路线**。

核心差异化：
- **选址推荐** — 基于收藏景点分布 + 高德实时路况，自动推荐最省交通时间的住宿区域
- **80 字 Tips** — 不写长篇游记，像朋友发微信一样一句话说清楚"值不值得去"
- **弹性路线** — 紧凑型按分钟排、弹性型只分天，两种节奏自由切换
- **Agent 搜索** — 输入"周末两天上海周边适合爬山"，AI 拆分约束匹配目的地

---

## 产品文档

| 文档 | 内容 |
|------|------|
| [01-需求分析文档](./01-需求分析文档.md) | 竞品分析（7款）、用户研究、差异化定位、MoSCoW、可行性分析 |
| [02-PRD产品需求文档](./02-PRD产品需求文档.md) | 用户画像、信息架构、6 项功能详述、交互流程、数据模型、API 设计 |

---

## 原型

8 页 HTML 原型，全链路导航互通：

首页 → 发现 → 城市列表 → 景点详情 → 主题灵感 → 我的规划 → 路线生成 → 我的行程

在线体验：[hanccn.github.io/xingmuer](https://hanccn.github.io/xingmuer/)

---

## 技术栈

| 层 | 选型 |
|----|------|
| 后端 | Django 6.0 + SQLite（生产切 PostgreSQL） |
| 前端 | 原生 HTML / CSS / JS + 高德 JS API 2.0 |
| AI Agent | DeepSeek API |
| 部署 | Railway + GitHub Pages |
| 设计 | Noto Serif SC 标题 + Noto Sans SC 正文，珊瑚橙暖调 |

---

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境变量并填入你的 Key
cp .env.example .env
# 编辑 .env 填入高德和 DeepSeek 的 Key

# 初始化数据库
python manage.py migrate
python manage.py createsuperuser

# 启动
python manage.py runserver
```

访问 `http://127.0.0.1:8000/`

测试账号：`demo` / `demo123`

---

## 项目结构

```
xiangmuer/
├── 01-需求分析文档.md        # 13 章需求分析
├── 02-PRD产品需求文档.md      # 14 章产品需求文档
├── travel/                    # Django 应用
│   ├── models.py              # 7 个数据模型
│   ├── views.py               # 10 个页面视图 + 5 个 API
│   ├── amap.py                # 高德 API 封装
│   └── context_processors.py
├── templates/travel/          # Django 模板
├── static/                    # 静态资源 + PWA
├── prototype/                 # 8 页独立 HTML 原型
└── xingmuer/                  # Django 配置
```

---

## 数据模型

```
City ──< POI ──< PoiTip
  │        │
  │        └──< PoiCollection >── User
  │        │
  │        └──< ThemePOI >── Theme
  │
  └──< Trip >── User
```

---

## API

| 端点 | 说明 |
|------|------|
| `GET /api/search/city/?q=` | 城市搜索 |
| `POST /api/collect/<poi_id>/` | 收藏/取消 |
| `POST /api/tip/<poi_id>/` | 写 Tips（≤80 字） |
| `POST /api/location/` | 住宿选址推荐 |
| `POST /api/route/` | 路线生成（贪心 + 按天拆分） |
| `GET /api/agent/search/?q=` | Agent 自然语言搜索 |
| `GET /s/<code>/` | 行程分享（公开访问） |

---

## 待完成

- [ ] 面试自述文稿
- [ ] Figma 高保真原型
