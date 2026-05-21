# 🎬 Pixelle-Video 产品功能分析文档

> **分析范围**: 完整产品功能、用户流程、配置体系、UI 结构、流水线类型  
> **技术栈**: Python + Streamlit (Web UI) / FastAPI (API) + Pydantic + ComfyUI/ComfyKit + Edge-TTS  
> **许可证**: Apache 2.0 (AIDC-AI)  
> **分析日期**: 2026-01-28

---

## 一、核心功能清单

### P0 — 核心必需功能（无此则产品不可用）

| 编号 | 功能 | 入口 | 交互方式 | 输出 |
|------|------|------|----------|------|
| **P0-1** | **AI 智能文案生成** | Home 页 → 标准流水线 → 输入主题 + 点击「生成视频」 | 用户输入主题关键词，LLM 自动生成 n_scenes 段叙事文案 | 分镜文案列表（每条对应一个视频画面） |
| **P0-2** | **固定文案模式** | Home 页 → 标准流水线 → 切换「固定文案内容」模式 → 粘贴文案 | 用户提供完整文案，系统按段落/行/句子分割 | 分镜文案列表 |
| **P0-3** | **AI 语音合成 (TTS)** | 中间栏「语音设置」→ 选择 TTS 工作流/音色 | 为每段分镜文案合成语音；支持 Edge-TTS 本地（默认）和 ComfyUI 云端 TTS | 每个分镜的 .mp3 音频文件 |
| **P0-4** | **视频合成** | 右侧栏 → 点击「🎬 生成视频」 | 逐帧处理 → 拼接所有分镜 → 合成最终 MP4 | 完整视频文件（保存到 output/ 目录） |
| **P0-5** | **LLM 配置** | 顶部「⚙️ 系统配置」→ LLM 配置 | 用户配置 API Key / Base URL / Model | 配置持久化到 config.yaml |
| **P0-6** | **视频模板渲染** | 中间栏「视觉设置」→ 选择模板 | 使用 HTML 模板 + AI 图片 + 字幕渲染每帧画面 | 每帧的 MP4 分镜片段 |

### P1 — 重要功能（增强用户体验和生成质量）

| 编号 | 功能 | 入口 | 交互方式 | 输出 |
|------|------|------|----------|------|
| **P1-1** | **AI 配图生成** | 中间栏「视觉设置」→ 选择图像工作流 → 设置 Prompt Prefix | 调用 ComfyUI / RunningHub 工作流生图；默认使用 image_flux.json | 每段文案对应的 AI 插图（作为模板背景） |
| **P1-2** | **AI 视频生成** | 中间栏「视觉设置」→ 选择视频工作流 | 调用 WAN 2.1/WAN 2.2 等工作流生成动态视频素材 | 每段文案对应的 AI 短视频 |
| **P1-3** | **背景音乐 (BGM)** | 左侧栏「背景音乐」→ 选择内置/自定义 BGM | 支持无 BGM、内置音乐、自定义音乐（放到 bgm/ 目录），点击可试听 | 混入最终视频的背景音轨 |
| **P1-4** | **LLM 模型预设** | 「⚙️ 系统配置」→ LLM 预设下拉 | 一键切换：通义千问 (qwen-max)、GPT-4o、DeepSeek、Ollama 等 | 自动填充 base_url 和 model |
| **P1-5** | **视频尺寸支持** | 中间栏「视觉设置」→ 选择模板（按尺寸分组） | 竖屏 1080×1920、方形 1080×1080、横屏 1920×1080 | 不同尺寸的视频 |
| **P1-6** | **实时进度显示** | 右侧栏生成视频时 | 分步显示：生成文案 → 生成配图 → 合成语音 → 分镜 N/M → 拼接视频 | 进度百分比 + 当前步骤文本 |
| **P1-7** | **视频预览与下载** | 右侧栏生成完成后 | 自动播放预览 + 显示时长/大小/分镜数 + 下载按钮 | 内嵌播放器 + 下载 MP4 |
| **P1-8** | **ComfyUI 连接测试** | 「⚙️ 系统配置」→ 点击「测试连接」 | 验证 ComfyUI 服务是否可访问 | 成功/失败提示 |
| **P1-9** | **RunningHub 并行处理** | 后台自动（使用 runninghub 工作流时） | 通过 asyncio.Semaphore 并发控制（默认 1，可配 1-10） | 加速视频生成 |

### P2 — 锦上添花功能（差异化体验）

| 编号 | 功能 | 入口 | 说明 |
|------|------|------|------|
| **P2-1** | **数字人口播流水线** | Home → Tab「🤖 数字人」 | 上传参考图片/视频，生成数字人播报视频（支持韩语等多语言） |
| **P2-2** | **图生视频流水线** | Home → Tab「🎥 图生视频」 | 上传图片 + 文本，AI 将图片动态化生成视频 |
| **P2-3** | **动作迁移流水线** | Home → Tab「💃 动作迁移」 | 上传参考视频 + 图片，进行动作迁移生成（如跳舞小猫） |
| **P2-4** | **自定义素材流水线** | Home → Tab「🎨 自定义素材」 | 上传自有图片/视频素材，AI 智能分析后生成脚本并合成视频 |
| **P2-5** | **声音克隆** | 中间栏「语音设置」→ 上传参考音频 | 上传 MP3/WAV/FLAC 参考音频用于 Index-TTS 等工作流的声音克隆 |
| **P2-6** | **历史记录页** | 导航栏 → 「📚 历史记录」 | 查看过往所有视频生成任务、元数据和输出文件 |
| **P2-7** | **FastAPI 接口** | `uv run python api/app.py` | 提供 RESTful API 供第三方调用（LLM/TTS/图片/视频/任务管理） |
| **P2-8** | **国际化 (i18n)** | 页面顶部语言切换器 | 支持中文/英文界面切换 |
| **P2-9** | **自定义模板** | 将 HTML 放到 templates/ 目录 | 用户自定义视频画面模板，命名约定：static_*/image_*/video_*.html |
| **P2-10** | **静态模板（无 AI 生图）** | 选择 static_*.html 模板 | 纯文字样式模板，跳过 AI 生图，更快更低成本 |
| **P2-11** | **FAQ 侧边栏** | 页面内置 FAQ | 常见问题解答（嵌入侧边栏） |
| **P2-12** | **Docker 部署** | docker-compose.yml | 容器化部署方案 |

---

## 二、用户操作流程

### 2.1 标准流程：主题 → 视频（约 2-8 分钟）

```
┌─────────────────────────────────────────────────────────────────────┐
│                    用户操作路径图 (Happy Path)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ① 打开 Web UI        ② 配置 LLM          ③ 选择流水线              │
│  (localhost:8501)      ⚙️ 系统配置          Tab: ⚡ 快速创作          │
│       │                API Key +            (默认选中)               │
│       ▼                Base URL + Model                             │
│                        [保存配置]                                    │
│                                                                     │
│  ④ 输入内容            ⑤ 配置样式           ⑥ 生成与预览             │
│  ┌────────────┐        ┌────────────┐       ┌────────────┐          │
│  │ 左栏        │        │ 中栏        │       │ 右栏        │         │
│  │            │        │            │       │            │         │
│  │ 模式选择    │        │ 语音设置    │       │ 🎬 生成视频 │         │
│  │ · AI生成   │        │ · TTS工作流 │       │ [点击按钮]  │         │
│  │ · 固定文案  │        │ · 参考音频  │       │            │         │
│  │            │        │            │       │ ▼ 进度条   │         │
│  │ 输入主题    │        │ 视觉设置    │       │ 生成文案... │         │
│  │ "旅行见闻"  │        │ · 图像工作流│       │ 分镜 3/5... │         │
│  │            │        │ · 图像尺寸  │       │            │         │
│  │ 分镜数量    │        │ · Prompt前缀│       │ ▼ 视频预览  │         │
│  │ (1-10)     │        │ · 视频模板  │       │ [▶ 播放]   │         │
│  │            │        │            │       │ ⏱️ 45s     │         │
│  │ BGM 选择   │        │            │       │ 📦 12.5MB  │         │
│  │ · 无       │        │            │       │ 🎬 5个分镜 │         │
│  │ · 内置     │        │            │       │ [⬇ 下载]   │         │
│  │ · 自定义   │        │            │       │            │         │
│  └────────────┘        └────────────┘       └────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 后台处理流程（用户不可见）

```
输入主题 ──→ [LLM] 生成标题 ──→ [LLM] 生成分镜文案 ──→ [LLM] 生成图提示词
                                                              │
                                                              ▼
                                               ┌──────────────────────┐
                                               │   逐帧处理（并行/串行）  │
                                               │                      │
                                               │ ① [TTS] 生成语音      │
                                               │ ② [ComfyUI] 生成图片  │
                                               │ ③ [FrameProcessor]    │
                                               │    渲染 HTML 模板      │
                                               │    合成单帧视频        │
                                               └──────┬───────────────┘
                                                      │
                                                      ▼
                      [VideoService] 拼接所有分镜 ──→ [VideoService] 叠加 BGM
                                                      │
                                                      ▼
                                               output/ 最终视频.mp4
```

### 2.3 各流水线入口路径

| 流水线 | 导航路径 | 核心交互 |
|--------|----------|----------|
| ⚡ 快速创作 | Home → Tab「⚡」 | 输入主题 → 生成视频（标准三栏布局） |
| 🎨 自定义素材 | Home → Tab「🎨」 | 上传图片/视频 → 设置标题/意图 → 设置时长/来源/语音 → 生成 |
| 🤖 数字人 | Home → Tab「🤖」 | 上传参考图片 → 选择数字人模式 → 生成口播视频 |
| 🎥 图生视频 | Home → Tab「🎥」 | 上传图片 + 文本 → 选择工作流 → 生成动态视频 |
| 💃 动作迁移 | Home → Tab「💃」 | 上传参考视频 + 图片 → 生成动作迁移视频 |

### 2.4 关键页面交互设计

- **系统配置栏**: 页面顶部可展开/折叠区域（st.expander），含 LLM 预设选择、API Key 输入、ComfyUI URL 配置、连接测试按钮
- **流水线 Tab 切换**: 使用 st.tabs 实现，每个 Tab 内独立渲染对应流水线的完整 UI
- **三栏布局**: 左侧（输入 + BGM）、中间（样式配置）、右侧（生成 + 预览），使用 st.columns([1,1,1])
- **BGM 试听**: st.audio 组件内嵌播放
- **模板预览**: 独立按钮触发 markdown 渲染模板效果图

---

## 三、配置体系

### 3.1 配置分类总览（基于 config.example.yaml + schema.py）

```
PixelleVideoConfig
├── project_name: str = "Pixelle-Video"
│
├── 📝 LLM 配置 (llm)
│   ├── api_key: str          [必填] LLM API 密钥
│   ├── base_url: str         [必填] API 端点地址
│   └── model: str            [必填] 模型名称
│
├── 🎨 ComfyUI 配置 (comfyui)
│   ├── comfyui_url: str                         [可选] ComfyUI 服务地址 (默认 127.0.0.1:8188)
│   ├── comfyui_api_key: Optional[str]           [可选] ComfyUI API Key
│   ├── runninghub_api_key: Optional[str]         [可选] RunningHub API Key
│   ├── runninghub_concurrent_limit: int          [可选] 并发限制 1-10 (默认 1)
│   ├── runninghub_instance_type: Optional[str]   [可选] 实例类型 (plus=48GB VRAM)
│   │
│   ├── 🎤 TTS 配置 (tts)
│   │   ├── inference_mode: str                   [可选] "local" | "comfyui" (默认 local)
│   │   ├── local:
│   │   │   ├── voice: str                        [可选] Edge-TTS 音色 (默认 zh-CN-YunjianNeural)
│   │   │   └── speed: float                      [可选] 语速 0.5-2.0 (默认 1.2)
│   │   └── comfyui:
│   │       └── default_workflow: Optional[str]   [可选] 默认 TTS 工作流 (默认 selfhost/tts_edge.json)
│   │
│   ├── 🖼️ 图片配置 (image)
│   │   ├── default_workflow: Optional[str]       [推荐] 默认图片工作流 (默认 runninghub/image_flux.json)
│   │   └── prompt_prefix: str                    [可选] 图片生成提示词前缀
│   │
│   └── 🎬 视频配置 (video)
│       ├── default_workflow: Optional[str]       [推荐] 默认视频工作流 (默认 runninghub/video_wan2.1_fusionx.json)
│       └── prompt_prefix: str                    [可选] 视频生成提示词前缀
│
└── 📐 模板配置 (template)
    └── default_template: str                     [可选] 默认模板 (默认 1080x1920/image_default.html)
```

### 3.2 配置必填/可选对照表

| 配置项 | 必填 | 条件 | 默认值 |
|--------|------|------|--------|
| `llm.api_key` | ✅ | 始终需要 | 空 |
| `llm.base_url` | ✅ | 始终需要 | 空 |
| `llm.model` | ✅ | 始终需要 | 空 |
| `comfyui.comfyui_url` | 条件 | 使用 selfhost 工作流时需要 | `http://127.0.0.1:8188` |
| `comfyui.runninghub_api_key` | 条件 | 使用 runninghub 工作流时需要 | 空 |
| `comfyui.tts.local.voice` | ❌ | 可选 | `zh-CN-YunjianNeural` |
| `comfyui.tts.local.speed` | ❌ | 可选 | 1.2 |
| `comfyui.image.default_workflow` | ❌ | 有默认值 | `runninghub/image_flux.json` |
| `comfyui.video.default_workflow` | ❌ | 有默认值 | `runninghub/video_wan2.1_fusionx.json` |
| `comfyui.image.prompt_prefix` | ❌ | 可选 | 火柴人风格英文前缀 |
| `template.default_template` | ❌ | 有默认值 | `1080x1920/image_default.html` |

### 3.3 LLM 预设一览

| 预设 | Base URL | Model |
|------|----------|-------|
| 通义千问 Max | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-max` |
| OpenAI GPT-4o | `https://api.openai.com/v1` | `gpt-4o` |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| Ollama (本地) | `http://localhost:11434/v1` | `llama3.2` |

### 3.4 运行时配置项（Web UI 中动态设置，不持久化到 config.yaml）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 生成模式 (mode) | generate / fixed | generate |
| 分镜数量 (n_scenes) | AI 生成模式下的分镜数 | 5 |
| 文案分割方式 (split_mode) | paragraph / line / sentence | paragraph |
| 图像尺寸 (media_width/height) | 生成图片的宽高 | 1024×1024 |
| Prompt 前缀覆盖 | 运行时覆盖 config 中的 prompt_prefix | - |
| BGM 路径/音量/模式 | bgm_path / bgm_volume / bgm_mode | - / 0.2 / loop |
| 视频标题 (title) | 可选覆盖自动生成的标题 | - |

---

## 四、UI 结构

### 4.1 页面层级

```
web/app.py                                            ← Streamlit 入口
├── st.navigation([...])
│   ├── pages/1_🎬_Home.py                            ← 主页（默认页）
│   │   ├── render_header()                          ← 标题 + 语言切换
│   │   ├── render_faq_sidebar()                     ← FAQ 侧边栏
│   │   ├── render_advanced_settings()                ← ⚙️ 系统配置（LLM + ComfyUI）
│   │   └── st.tabs([...])                            ← 流水线 Tab 切换
│   │       ├── ⚡ 快速创作 (StandardPipelineUI)
│   │       │   ├── 左栏: render_content_input()     ← 模式选择 + 主题/文案输入 + 分镜数
│   │       │   ├── 左栏: render_bgm_section()        ← BGM 选择 + 试听
│   │       │   ├── 左栏: render_version_info()       ← 版本号 + GitHub 链接
│   │       │   ├── 中栏: render_style_config()       ← TTS + 模板 + 工作流 + 尺寸
│   │       │   └── 右栏: render_output_preview()     ← 生成按钮 + 进度 + 视频预览 + 下载
│   │       ├── 🎨 自定义素材 (AssetBasedPipelineUI)
│   │       │   ├── 左栏: 素材上传 + 视频标题/意图 + BGM
│   │       │   ├── 中栏: 时长 + 来源选择 + TTS配置
│   │       │   └── 右栏: 生成 + 进度 + 预览
│   │       ├── 🤖 数字人 (DigitalHumanPipelineUI)
│   │       │   ├── 左栏: 数字人素材输入 + TTS样式
│   │       │   ├── 中栏: 模式选择 + 工作流配置
│   │       │   └── 右栏: 生成 + 预览
│   │       ├── 🎥 图生视频 (ImageToVideoPipelineUI)
│   │       │   └── 两栏布局: 素材/配置 | 生成/预览
│   │       └── 💃 动作迁移 (ActionTransferPipelineUI)
│   │           └── 三栏布局: 视频/图片上传 | 配置 | 生成/预览
│   │
│   └── pages/2_📚_History.py                         ← 历史记录页
│       └── 任务列表 + 历史视频查看
```

### 4.2 Web 组件清单

| 组件文件 | 职责 | 被哪些流水线引用 |
|----------|------|-----------------|
| `header.py` | 页面标题 + 语言选择器 | Home 页（全局） |
| `settings.py` | LLM/ComfyUI 系统配置表单 | Home 页（全局） |
| `content_input.py` | 内容输入（模式/主题/分镜数）+ BGM + 版本信息 | Standard, AssetBased |
| `style_config.py` | 视觉/语音样式配置（TTS/模板/工作流/尺寸） | Standard |
| `output_preview.py` | 生成按钮 + 进度条 + 视频预览 + 下载 | Standard |
| `digital_tts_config.py` | 数字人的 TTS 样式配置 | DigitalHuman |
| `faq.py` | 侧边栏 FAQ | Home 页（全局） |
| `session.py` | Streamlit session state 初始化 | Home 页 |

### 4.3 关键交互细节

- **配置保存**: 点击「保存配置」后写入 config.yaml，同时更新内存中的 config_manager
- **模板分组**: 模板按尺寸（1080×1920 / 1080×1080 / 1920×1080）分组显示在下拉菜单
- **模板预览**: 需要单独点击预览按钮，系统渲染模板 HTML + 默认参数展示效果
- **语音预览**: 输入测试文本 + 点击「预览语音」按钮，调用 TTS 实时试听
- **BGM 试听**: 选择 BGM 后直接播放预览
- **RunningHub 并发**: 在 settings 中可配 1-10，配置后热生效无需重启
- **进度事件模型 (ProgressEvent)**: event_type + progress(0-1) + frame_current + frame_total + step + action + extra_info

---

## 五、流水线类型

### 5.1 流水线注册表

| 流水线 | 注册名 | Tab图标 | 核心类 | 说明 |
|--------|--------|---------|--------|------|
| ⚡ 快速创作 | `quick_create` | ⚡ | `StandardPipeline` + `StandardPipelineUI` | 默认流水线，主题→视频 |
| 🎨 自定义素材 | `custom_media` | 🎨 | `AssetBasedPipeline` + `AssetBasedPipelineUI` | 用户上传素材→智能分析→视频 |
| 🤖 数字人 | `digital_human` | 🤖 | (独立实现) + `DigitalHumanPipelineUI` | 数字人播报视频 |
| 🎥 图生视频 | `image_to_video` | 🎥 | (独立实现) + `ImageToVideoPipelineUI` | 图片动态化 |
| 💃 动作迁移 | `action_transfer` | 💃 | (独立实现) + `ActionTransferPipelineUI` | 参考视频驱动图片动作 |

### 5.2 各流水线详细特征对比

| 维度 | ⚡ 快速创作 | 🎨 自定义素材 | 🤖 数字人 | 🎥 图生视频 | 💃 动作迁移 |
|------|-----------|-------------|----------|-----------|-----------|
| **输入** | 主题文本 / 固定文案 | 图片/视频文件 + 标题/意图 | 参考图片/视频 + 音频 | 图片 + 文本 | 参考视频 + 图片 |
| **LLM调用** | ✅ 标题+文案+图提示词 | ✅ 素材分析+脚本生成 | ❌ (可能) | ❌ | ❌ |
| **图片生成** | ✅ (可选) | ❌ (使用用户素材) | ❌ | ❌ (用户提供) | ❌ |
| **视频生成** | ✅ (可选) | ❌ | ✅ (数字人合成) | ✅ (图→视频) | ✅ (动作迁移) |
| **TTS** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **BGM** | ✅ | ✅ | ❌ (当前UI不展示) | ❌ | ❌ |
| **继承体系** | `LinearVideoPipeline` | `BasePipeline` 直接 | 独立实现 | 独立实现 | 独立实现 |
| **布局** | 三栏 | 三栏 | 三栏 | 两栏 | 三栏 |
| **进度步骤** | setup→content→title→visuals→storyboard→assets→post→finalize | analyzing→script→frames→concat | 自定义 | 自定义 | 自定义 |
| **并行处理** | ✅ (RunningHub) | ❌ | ❌ | ❌ | ❌ |
| **适合场景** | 通用短视频创作 | 产品展示/旅行Vlog/营销视频 | 虚拟主播/口播 | 图片动效/趣味视频 | 趣味动作/舞蹈 |

### 5.3 标准流水线 (StandardPipeline) 生命周期详解

StandardPipeline 继承 `LinearVideoPipeline`，使用 **模板方法模式**，8 个生命周期步骤：

```
┌────────────────────────────────────────────────────────────────┐
│  Phase 1: Preparation                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 1: setup_environment                                │  │
│  │    → 创建独立任务目录 (output/tasks/{task_id}/)           │  │
│  │    → 确定最终视频路径                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Phase 2: Content Creation                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 2: generate_content                                 │  │
│  │    → generate 模式: LLM 根据主题生成 N 段分镜文案          │  │
│  │    → fixed 模式: 按 paragraph/line/sentence 分割文案       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 3: determine_title                                  │  │
│  │    → 用户指定标题 OR LLM 自动生成                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Phase 3: Visual Planning                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 4: plan_visuals                                     │  │
│  │    → 检测模板类型 (static/image/video)                     │  │
│  │    → static 模板: 跳过 AI 生图 (省时省钱)                  │  │
│  │    → image/video 模板: LLM 生成图提示词 + 拼合 Prompt 前缀  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 5: initialize_storyboard                            │  │
│  │    → 创建 StoryboardConfig (FPS, TTS参数, 模板, 尺寸等)   │  │
│  │    → 创建 Storyboard + StoryboardFrame 列表               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Phase 4: Asset Production                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 6: produce_assets                                   │  │
│  │    → RunningHub 工作流: asyncio.Semaphore 并行处理        │  │
│  │    → 非 RunningHub: 逐帧串行处理                           │  │
│  │    → 每帧: TTS生成音频 + 生成图片 → FrameProcessor 渲染   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Phase 5: Post Production                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 7: post_production                                  │  │
│  │    → VideoService.concat_videos() 拼接所有分镜            │  │
│  │    → 叠加 BGM (可选，支持 loop 模式)                       │  │
│  │    → 复制到用户指定路径 (如有)                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Phase 6: Finalization                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 8: finalize                                         │  │
│  │    → 创建 VideoGenerationResult                           │  │
│  │    → 持久化任务元数据 + Storyboard (PersistenceService)    │  │
│  │    → 记录日志 (时长/大小/分镜数)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### 5.4 核心数据模型

```
PipelineContext (dataclass)          Storyboard
├── input_text: str                  ├── title: str
├── params: Dict[str, Any]           ├── config: StoryboardConfig
├── progress_callback: Callable      ├── frames: List[StoryboardFrame]
├── task_id: str                     ├── total_duration: float
├── task_dir: str                    ├── final_video_path: str
├── title: str                       ├── created_at: datetime
├── narrations: List[str]            └── completed_at: datetime
├── image_prompts: List[str]
├── config: StoryboardConfig         StoryboardFrame
├── storyboard: Storyboard           ├── index: int
├── final_video_path: str            ├── narration: str
└── result: VideoGenerationResult    ├── image_prompt: str
                                     ├── audio_path: str
VideoGenerationResult                ├── image_url: str
├── video_path: str                  ├── video_segment_path: str
├── storyboard: Storyboard           ├── html_path: str
├── duration: float                  └── duration: float
└── file_size: int
```

### 5.5 服务层架构 (PixelleVideoCore)

```
PixelleVideoCore (facade)
├── llm: LLMService              ← OpenAI SDK 兼容接口
├── tts: TTSService              ← Edge-TTS 本地 + ComfyUI TTS
├── media: MediaService          ← 图片/视频生成 (ComfyKit 封装)
├── image_analysis: ImageAnalysisService  ← 素材分析 (视觉模型)
├── video_analysis: VideoAnalysisService   ← 视频素材分析
├── video: VideoService          ← 视频拼接 + BGM 叠加
├── frame_processor: FrameProcessor  ← 单帧渲染（模板+图片+音频）
├── persistence: PersistenceService   ← 任务元数据持久化
├── history_manager: HistoryManager   ← 历史记录管理
├── config: Dict                ← 运行时配置引用
├── frame_html: FrameHTMLService ← HTML 模板处理
└── pipelines:                  ← 流水线注册
    ├── StandardPipeline
    ├── CustomPipeline
    └── AssetBasedPipeline
```

---

## 六、工作流资源

### 6.1 RunningHub 工作流（云端）

| 类别 | 工作流文件 | 用途 |
|------|-----------|------|
| 图片 | `image_flux.json` | FLUX 模型生图（推荐默认） |
| 图片 | `image_flux2.json` | FLUX 二代模型生图 |
| 图片 | `image_qwen.json` | 通义千问生图 |
| 图片 | `image_qwen_chinese_cartoon.json` | 通义千问中国风卡通 |
| 图片 | `image_sd3.5.json` | Stable Diffusion 3.5 |
| 图片 | `image_sdxl.json` | SDXL 生图 |
| 图片 | `image_Z-image.json` | Z-Image 模型 |
| 视频 | `video_wan2.1_fusionx.json` | WAN 2.1 文生视频（推荐默认） |
| 视频 | `video_wan2.2.json` | WAN 2.2 文生视频 |
| 视频 | `video_qwen_wan2.2.json` | 通义千问 + WAN 2.2 |
| 视频 | `video_Z_image_wan2.2.json` | Z-Image + WAN 2.2 |
| 视频 | `video_understanding.json` | 视频理解 |
| 视频 | `i2v_LTX2.json` | 图生视频 LTX2 |
| TTS | `tts_edge.json` | Edge TTS 云端版 |
| TTS | `tts_index2.json` | Index-TTS 2（支持声音克隆） |
| TTS | `tts_spark.json` | Spark TTS |
| 分析 | `analyse_image.json` | 图片智能分析 |
| 分析 | `af_scail.json` | AF Scail |
| 数字人 | `digital_combination.json` | 数字人组合 |
| 数字人 | `digital_customize.json` | 数字人定制 |
| 数字人 | `digital_image.json` | 数字人图片模式 |

### 6.2 Selfhost 工作流（本地 ComfyUI）

| 类别 | 工作流文件 | 用途 |
|------|-----------|------|
| 图片 | `image_flux.json` | FLUX 本地生图 |
| 图片 | `image_qwen.json` | 通义千问本地生图 |
| 图片 | `image_nano_banana.json` | Nano Banana 模型 |
| 视频 | `video_wan2.1_fusionx.json` | WAN 2.1 本地生视频 |
| TTS | `tts_edge.json` | Edge TTS 本地 |
| TTS | `tts_index2.json` | Index-TTS 2 本地 |
| 分析 | `analyse_image.json` | 图片分析 |
| 分析 | `analyse_video.json` | 视频分析 |

### 6.3 视频模板一览

| 尺寸 | 模板文件 | 类型 | 风格描述 |
|------|----------|------|----------|
| 1080×1920 | `image_default.html` | 图片 | ✅ 默认竖屏模板 |
| 1080×1920 | `image_modern.html` | 图片 | 现代风格 |
| 1080×1920 | `image_elegant.html` | 图片 | 优雅风格 |
| 1080×1920 | `image_blur_card.html` | 图片 | 模糊卡片 |
| 1080×1920 | `image_book.html` | 图片 | 书籍风格 |
| 1080×1920 | `image_cartoon.html` | 图片 | 卡通风格 |
| 1080×1920 | `image_full.html` | 图片 | 全屏图片 |
| 1080×1920 | `image_healing.html` | 图片 | 治愈系 |
| 1080×1920 | `image_neon.html` | 图片 | 霓虹风格 |
| 1080×1920 | `image_purple.html` | 图片 | 紫色主题 |
| 1080×1920 | `image_simple_black.html` | 图片 | 极简黑 |
| 1080×1920 | `image_simple_line_drawing.html` | 图片 | 简笔画 |
| 1080×1920 | `image_fashion_vintage.html` | 图片 | 复古时尚 |
| 1080×1920 | `image_health_preservation.html` | 图片 | 养生主题 |
| 1080×1920 | `image_life_insights.html` | 图片 | 人生感悟 |
| 1080×1920 | `image_life_insights_light.html` | 图片 | 人生感悟·浅色 |
| 1080×1920 | `image_long_text.html` | 图片 | 长文本优化 |
| 1080×1920 | `image_psychology_card.html` | 图片 | 心理学卡片 |
| 1080×1920 | `image_satirical_cartoon.html` | 图片 | 讽刺漫画 |
| 1080×1920 | `image_excerpt.html` | 图片 | 摘录风格 |
| 1080×1920 | `static_default.html` | 静态 | ⚡ 纯文字（无需AI生图） |
| 1080×1920 | `static_excerpt.html` | 静态 | 静态摘录 |
| 1080×1920 | `video_default.html` | 视频 | AI视频背景 |
| 1080×1920 | `video_healing.html` | 视频 | 治愈系视频 |
| 1080×1920 | `asset_default.html` | 素材 | 自定义素材模板 |
| 1080×1080 | `image_minimal_framed.html` | 图片 | 方形极简边框 |
| 1920×1080 | `image_film.html` | 图片 | 电影感横屏 |
| 1920×1080 | `image_full.html` | 图片 | 全屏横屏 |
| 1920×1080 | `image_book.html` | 图片 | 书籍横屏 |
| 1920×1080 | `image_ultrawide_minimal.html` | 图片 | 超宽极简 |
| 1920×1080 | `image_wide_darktech.html` | 图片 | 暗黑科技风 |

---

## 七、API 路由结构

FastAPI 应用（`api/app.py`）提供如下 REST API：

| 路由前缀 | 模块 | 主要端点 |
|----------|------|----------|
| `/health` | `routers/health.py` | GET 健康检查 |
| `/llm` | `routers/llm.py` | LLM 调用接口 |
| `/tts` | `routers/tts.py` | 语音合成接口 |
| `/image` | `routers/image.py` | 图片生成接口 |
| `/video` | `routers/video.py` | 视频生成接口 |
| `/content` | `routers/content.py` | 内容生成（文案等） |
| `/frame` | `routers/frame.py` | 分镜处理 |
| `/files` | `routers/files.py` | 文件管理 |
| `/resources` | `routers/resources.py` | 资源管理 |
| `/tasks` | `routers/tasks.py` | 任务管理 |

---

## 八、关键架构决策与设计模式

### 8.1 设计模式

| 模式 | 应用位置 | 说明 |
|------|----------|------|
| **Template Method** | `LinearVideoPipeline` | 定义 8 步视频生成骨架，子类覆写具体步骤 |
| **Registry** | `PipelineUI` 注册表 | 装饰器 `@register_pipeline_ui` 自动注册流水线 UI |
| **Facade** | `PixelleVideoCore` | 统一对外接口，封装所有子服务 |
| **Strategy** | TTS 模式切换 | local → Edge-TTS，comfyui → 云端 TTS |
| **Observer** | `ProgressEvent` + callback | 流水线执行过程中的进度通知 |

### 8.2 技术亮点

- **工作流原子化**: 基于 ComfyUI JSON 工作流，每个能力（生图/视频/TTS）是独立的 JSON 文件，用户可自由替换
- **双部署模式**: selfhost（本地 ComfyUI）和 runninghub（云端 API）无缝切换
- **RunningHub 并行**: asyncio.Semaphore 并发控制，可配置 1-10，大幅加速视频生成
- **模板类型检测**: 自动识别 static/image/video 模板类型，static 模板跳过所有 AI 生成，零成本出片
- **Edge TTS 锁定版本**: 修复 TTS 服务不稳定问题，使用固定版本的 edge-tts
- **任务隔离**: 每个视频任务有独立的 task_id 和目录，支持历史回溯

---

## 九、产品定位与竞品简析

### 9.1 产品定位

**一句话描述**: Pixelle-Video 是一个开源的 AI 全自动短视频引擎，输入一个主题即可一键生成带配音、配图、BGM 的完整视频。

**目标用户**: 短视频创作者、自媒体运营者、需要批量生产视频内容的用户，AI 开发者。

**核心差异点**:
1. 完全开源 + 可私有化部署
2. 基于 ComfyUI 的原子化能力组合，灵活替换任意环节
3. 支持完全免费方案（Ollama + 本地 ComfyUI）
4. 多流水线架构（标准/素材/数字人/图生视频/动作迁移）

### 9.2 主要竞品

| 竞品 | 类型 | 优势 | Pixelle-Video 差异 |
|------|------|------|-------------------|
| MoneyPrinterTurbo | 开源 | 成熟度、社区规模 | Pixelle 有更灵活的 ComfyUI 架构、多流水线 |
| NarratoAI | 开源 | 影视解说专用优化 | Pixelle 覆盖更多内容类型 |
| 剪映 (CapCut) | 商业 | 用户基数、模板生态 | Pixelle 开源可控、AI 深度集成 |
| HeyGen | 商业 | 数字人质量极高 | Pixelle 开源免费、端到端视频生成 |

---

*本文档基于 Pixelle-Video 源码 v1.x 分析生成，覆盖配置文件、核心流水线、Web UI、API 接口及模板体系。*
