# Pixelle-Video 配置指南

## 📋 完整配置需求说明

### 📁 配置文件位置

主配置文件：[`config.yaml`](file:///d:/全自动的开始/LY-Pixelle-Video/config.yaml)  
配置模板：[`config.example.yaml`](file:///d:/全自动的开始/LY-Pixelle-Video/config.example.yaml)

---

## 🔑 必填配置项清单

### 1. LLM 配置（必须填写其一）

| 服务商 | 配置项 | 是否必填 | 获取地址 |
|--------|--------|----------|
| DeepSeek | llm.provider | ✅ | [https://platform.deepseek.com/ |
| | llm.api_key | ✅ | |
| | llm.base_url | ✅ | |
| | llm.model | ✅ | |
| 通义千问 | llm.provider | ✅ | [https://dashscope.console.aliyun.com/ |
| | llm.api_key | ✅ | |
| | llm.base_url | ✅ | |
| | llm.model | ✅ | |
| 豆包 | llm.provider | ✅ | [https://console.volcengine.com/ark/ |
| | llm.api_key | ✅ | |
| | llm.base_url | ✅ | |
| | llm.model | ✅ | |
| OpenAI | llm.provider | ✅ | [https://platform.openai.com/ |
| | llm.api_key | ✅ | |
| | llm.base_url | ✅ | |
| | llm.model | ✅ | |
| Ollama（本地） | llm.provider | ✅ | [https://ollama.com/ |
| | llm.api_key | ➖ | |
| | llm.base_url | ✅ | |
| | llm.model | ✅ | |

### 2. ComfyUI 配置（选择其一）

#### 方案 A：RunningHub（推荐，云端）

| 配置项 | 是否必填 | 说明 |
|--------|----------|------|
| comfyui.runninghub_api_key | ✅ | [https://platform.comfy.org/profile/api-keys |
| comfyui.image.default_workflow | ✅ | 使用 runninghub 开头的工作流 |
| comfyui.video.default_workflow | ✅ | |

#### 方案 B：本地 ComfyUI（自部署）

| 配置项 | 是否必填 | 说明 |
|--------|----------|------|
| comfyui.comfyui_url | ✅ | 本地 ComfyUI 地址，默认 http://127.0.0.1:8188 |
| comfyui.image.default_workflow | ✅ | 使用 selfhost 开头的工作流 |
| comfyui.video.default_workflow | ✅ | |

### 3. 模板配置

| 配置项 | 是否必填 | 说明 |
|--------|----------|------|
| template.default_template | ✅ | 默认视频模板 |

---

## 🎯 推荐配置组合

### 方案一：全云端（最简单）

| 组件 | 选择 | 原因 |
|------|------|
| LLM | DeepSeek | 性价比最高 |
| AI 生成 | RunningHub | 无需本地部署 |
| TTS | Edge TTS | 免费，无需 API |

**优点**：无需本地 ComfyUI，开箱即用

**配置示例**：
```yaml
llm:
  provider: "deepseek"
  api_key: "sk-xxxxxxxxxxxxxxxx"
  base_url: "https://api.deepseek.com"
  model: "deepseek-chat"

comfyui:
  runninghub_api_key: "csk-xxxxxxxxxxxxxxxx"
  image:
    default_workflow: runninghub/image_flux.json
  video:
    default_workflow: runninghub/video_wan2.1_fusionx.json
```

### 方案二：全本地（免费）

| 组件 | 选择 | 原因 |
|------|------|------|
| LLM | Ollama | 完全免费 |
| AI 生成 | 本地 ComfyUI | 完全免费 |
| TTS | Edge TTS | 免费，无需 API |

**优点**：完全免费，无 API 费用

**配置示例**：
```yaml
llm:
  provider: "ollama"
  api_key: "dummy"
  base_url: "http://localhost:11434/v1"
  model: "llama3.2"

comfyui:
  comfyui_url: "http://127.0.0.1:8188"
  image:
    default_workflow: selfhost/image_flux.json
  video:
    default_workflow: selfhost/video_wan2.1_fusionx.json
```

---

## 📦 绿色打包注意事项

### config.yaml 的处理

1. **开发阶段：`config.yaml` 在项目根目录使用
2. **打包阶段**：`config.yaml` 会被自动排除在包外（见 [`build_config.yaml`](file:///d:/全自动的开始/LY-Pixelle-Video/packaging/windows/config/build_config.yaml) exclude_patterns)
3. **用户使用**：最终用户需要自己创建 `config.yaml`

### 用户首次运行提示

绿色包首次运行时需要引导用户：
1. 复制 `config.example.yaml` 为 `config.yaml`
2. 填写必要的 API 密钥
3. 启动应用

---

## 🔧 快速配置步骤

### 第一步：选择 LLM

推荐 **DeepSeek**（新用户有免费额度）
1. 访问 https://platform.deepseek.com
2. 注册账号
3. 创建 API Key
4. 复制到 `config.yaml`

### 第二步：选择 AI 生成方案

推荐 **RunningHub**
1. 访问 https://platform.comfy.org
2. 注册账号
3. 创建 API Key
4. 复制到 `config.yaml`

### 第三步：测试配置完成

启动应用测试功能

---

## 📝 配置验证清单

- [ ] LLM provider 已填写
- [ ] LLM api_key 已填写
- [ ] LLM base_url 已填写
- [ ] LLM model 已填写
- [ ] RunningHub API Key 已填写（如果用云端）
- [ ] image default_workflow 已选择
- [ ] video default_workflow 已选择
- [ ] template default_template 已选择
