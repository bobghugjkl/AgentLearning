# Day 01 复盘笔记 — LLM API 基础

## 今天学了什么

### 1. OpenAI-compatible 协议
- DeepSeek、通义千问、Kimi 等国产模型全部兼容 OpenAI 协议
- 切换模型只需换 `base_url` 和 `api_key`，其他代码不动
- 统一用 `openai` 包调用，不需要每家装一个 SDK

### 2. messages 数组结构
| role | 是谁 | 作用 |
|------|------|------|
| `system` | 开发者 | 设定规则，用户看不见 |
| `user` | 用户 | 用户的输入 |
| `assistant` | 模型 | 模型的回复 |

### 3. LLM 没有记忆
- 模型每次请求都是"失忆"状态
- 多轮对话靠每次把完整 messages 历史带上实现
- 对话越长 → messages 越多 → token 消耗越大 → 成本越高

### 4. temperature 参数
| 值 | 效果 | 适合场景 |
|----|------|--------|
| `0.0` | 稳定，几乎每次一样 | 代码、翻译、数据分析 |
| `0.7` | 自然，有适度变化 | 日常对话、问答 |
| `1.5` | 随机，天马行空 | 创意写作、头脑风暴 |

### 5. python-dotenv
- API Key 存 `.env` 文件，不写在代码里
- `load_dotenv()` 必须在 `os.getenv()` 之前调用
- `.env` 加入 `.gitignore` 防止泄露到 GitHub

---

## 今天遇到的问题

### 问题 1：api_key 读到 None
**报错：** `api_key client option must be set`  
**原因：** `os.getenv("DEEP_SEEK_API_KEY")` 变量名写错，多了一个下划线  
**解决：** 改成 `os.getenv("DEEPSEEK_API_KEY")`

### 问题 2：model 名字写错
**原因：** `model="deepseek_chat"`（下划线）应该是 `deepseek-chat`（中划线）  
**解决：** 注意模型名用中划线，不是下划线

### 问题 3：无关 import 冲突
**原因：** `from pyexpat.errors import messages` 和自己定义的 `messages` 变量名冲突  
**解决：** 删掉无关的 import，保持代码干净

---

## 面试考点

**Q：LLM 有记忆吗？多轮对话怎么实现？**  
答：LLM 本身没有记忆，每次请求都是独立的。多轮对话靠每次把完整的 messages 历史数组带上实现。对话越长 token 消耗越大，这也是为什么后面需要学"记忆压缩"策略。

**Q：为什么国产模型可以用 openai 包调用？**  
答：DeepSeek、通义、Kimi 等都兼容 OpenAI 的 Chat Completion 协议，只需替换 base_url 和 api_key，其余代码完全通用。

**Q：temperature 参数的作用？生产环境一般设多少？**  
答：控制输出的随机程度。0 最稳定，越高越随机。生产环境翻译/代码用 0~0.3，日常对话用 0.5~0.7，创意写作可以到 1.0 以上。

**Q：system prompt 对 token 消耗有影响吗？**  
答：有，system prompt 也算输入 token。每次请求都要带上，所以 system prompt 越长，每次调用成本越高。生产环境要精简 system prompt。

---

## 今日文件结构
```
day01/
├── 01_basic_chat.py    ✅ API基础调用、messages结构、token消耗
├── 02_multi_turn.py    ✅ 多轮对话、messages历史维护
└── 03_temperature.py   ✅ temperature参数对比实验
```

---

## 明天预告 — Day 02：流式输出与 SSE
- `stream=True` 怎么用，逐字打印效果怎么实现
- 为什么生产环境必须上流式（用户体验 + 首 token 延迟）
- SSE 是什么协议，和 WebSocket 有什么区别
- 用 FastAPI 暴露一个流式接口