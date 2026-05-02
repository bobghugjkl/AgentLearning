# Day 24 复盘笔记 — 长期记忆

## 今天学了什么

### 1. 短期记忆 vs 长期记忆

```
MemorySaver（短期）：
会话1：记住"我叫润实" ✅
程序重启
会话2：忘了 ❌

长期记忆：
会话1：记住"我叫润实" → 存到数据库
程序重启
会话2：从数据库读出来 → 还记得 ✅
```

### 2. 应该存什么

```
✅ 值得存：
- 姓名、职业背景
- 兴趣爱好、目标计划
- 重要偏好

❌ 不需要存：
- 闲聊（"今天天气真好"）
- 临时性问题
- 无意义的寒暄
```

### 3. 自实现长期记忆（SQLite）

```python
class LongTermMemory:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        """创建记忆表"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def save(self, user_id: str, memory: str):
        """存入一条记忆"""
        self.conn.execute(
            "INSERT INTO memories (user_id, memory) VALUES (?, ?)",
            (user_id, memory)
        )
        self.conn.commit()
    
    def get_all(self, user_id: str) -> list:
        """取出用户的所有记忆"""
        cursor = self.conn.execute(
            "SELECT memory FROM memories WHERE user_id = ?",
            (user_id,)
        )
        return [row[0] for row in cursor.fetchall()]
```

### 4. 用 LLM 自动提取重要信息

```python
extract_prompt = ChatPromptTemplate.from_messages([
    ("system", """从用户的话里提取值得长期记住的关键信息。
只提取：姓名、职业背景、兴趣爱好、目标计划、重要偏好。
不要提取：闲聊、问题、临时性内容。
如果有值得记住的信息，用一句话总结。
如果没有，只输出"无"。"""),
    ("human", "{message}"),
])

extract_chain = extract_prompt | model | StrOutputParser()

def extract_and_save(ltm, user_id, message):
    extracted = extract_chain.invoke({"message": message})
    if extracted.strip() != "无":
        ltm.save(user_id, extracted)
```

### 5. 带长期记忆的对话

```python
def chat_with_memory(ltm, user_id, question):
    # 从数据库加载记忆
    memories = ltm.get_all(user_id)
    memory_text = "\n".join(f"- {m}" for m in memories)
    
    messages = [
        SystemMessage(content=f"""你是一个友善的助手。
关于这个用户，你记得以下信息：
{memory_text}

请根据这些信息个性化地回答。"""),
        HumanMessage(content=question),
    ]
    
    return model.invoke(messages).content
```

### 6. 长期记忆的三个难点

```
难点1：什么值得存？（提取策略）
  → 用 LLM 判断，但不够完美

难点2：存的信息怎么用？（召回策略）
  → 少量记忆全部加载；大量记忆用向量检索按需召回

难点3：记忆会过时怎么办？（更新策略）
  → 新信息覆盖旧信息（"我现在不喜欢A了"）
  → 定期清理过期记忆
```

### 7. 长期记忆实现方案对比

| 方案 | 优点 | 缺点 | 适合场景 |
|------|------|------|---------|
| SQLite | 简单，无依赖 | 不支持语义检索 | 小规模，记忆少 |
| Mem0 | 自动提取，语义检索 | 需要Embedding | 中等规模 |
| PostgreSQL | 生产级，支持并发 | 需要部署 | 大规模生产 |
| 向量库 | 语义检索，海量记忆 | 复杂 | 超大规模 |

---

## 面试考点

**Q：MemorySaver 和长期记忆有什么区别？**  
答：MemorySaver 存在内存里，程序重启就消失，只能记住当前会话。长期记忆存在数据库里，跨会话、跨程序重启都能保留，适合记住用户的个人信息、偏好、历史行为。

**Q：长期记忆应该存什么？怎么提取？**  
答：存有价值的关键信息：姓名、职业、兴趣、目标、偏好。不存闲聊和临时性内容。可以用 LLM 自动提取——设计 prompt 让模型判断哪些值得记住，输出"无"表示不需要存。

**Q：长期记忆怎么用在对话里？**  
答：每次对话开始时从数据库加载该用户的所有记忆，拼成文本塞进 system prompt，让模型"记住"用户的背景信息，实现个性化回答。记忆少可以全部加载，记忆多就用向量检索按问题相关性召回。

**Q：记忆过时怎么处理？**  
答：三种策略：新信息覆盖旧信息（检测到矛盾时更新）；定期清理低价值记忆；给记忆加时间戳，优先使用最新记忆。

---

## 今日文件结构
```
week4/day24/
├── 01_long_term_memory.py  ✅ Mem0尝试（DeepSeek不支持Embedding）
├── 02_sqlite_memory.py     ✅ SQLite实现长期记忆、LLM提取、跨会话测试
└── memories.db             ✅ 生成的记忆数据库文件
```

---

## 明天预告 — Day 25：LangSmith 追踪与评估
- 为什么需要可观测性
- LangSmith 追踪每次 LLM 调用
- 查看 token 消耗、延迟、错误
- 用 LangSmith 评估 RAG 和 Agent 质量