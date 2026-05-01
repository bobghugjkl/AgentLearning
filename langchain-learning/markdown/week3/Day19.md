# Day 19 复盘笔记 — Reflexion 自反思 Agent

## 今天学了什么

### 1. 为什么需要 Reflexion

```
普通重试：失败 → 重试 → 失败 → 重试（机械重复，每次犯同样错误）

Reflexion：失败 → 反思原因 → 记录教训 → 带着教训重试（越试越聪明）
```

**核心思想：** 把失败经验转化成改进建议，存入记忆，让下一次尝试更好。就像学生订正作业——不是重新做一遍，而是先看哪里错了再做。

### 2. 三个核心组件

| 组件 | 作用 |
|------|------|
| Actor（执行者） | 尝试完成任务，带着历次反思改进 |
| Evaluator（评估者） | 判断结果是否合格 |
| Self-Reflection（反思者） | 分析失败原因，生成改进建议 |

**最关键的是反思者**——没有它就只是普通重试。

### 3. State 设计

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    task: str              # 原始任务
    attempts: List[str]    # 历次尝试的结果
    reflections: List[str] # 历次反思的内容（关键！）
    attempt_count: int     # 尝试次数
    passed: bool           # 是否通过评估
    max_attempts: int      # 最大尝试次数（防止无限循环）
```

### 4. Actor 节点（核心：带着教训重试）

```python
def actor_node(state: State):
    reflections = state["reflections"]
    
    if reflections:
        # 把历次反思都塞进 prompt！
        reflection_text = "\n".join([
            f"第{i+1}次失败教训：{r}" 
            for i, r in enumerate(reflections)
        ])
        prompt = f"""任务：{task}

你之前尝试过 {attempt_count} 次，以下是失败的教训：
{reflection_text}

请根据这些教训，改进后重新完成任务。"""
    else:
        prompt = f"请完成以下任务：{task}"
    
    return {
        "attempts": state["attempts"] + [result],
        "attempt_count": attempt_count + 1,
    }
```

### 5. 路由函数（三种结果）

```python
def should_continue(state: State) -> str:
    if state["passed"]:
        return "end"       # 通过评估 → 结束
    if state["attempt_count"] >= state["max_attempts"]:
        return "end"       # 超过最大次数 → 强制结束
    return "reflect"       # 没通过且还有机会 → 去反思
```

### 6. 图的流程

```
START
  ↓
actor（第1次尝试）
  ↓
evaluator（评估）
  ↓ 通过或超次数
END
  ↑
  ↓ 没通过且有机会
reflection（反思，把教训加入 reflections）
  ↓
actor（带着教训重试）← 回边
  ↓
evaluator...
```

### 7. Reflexion vs Plan-and-Execute 回边对比

```
Plan-and-Execute 回边：
executor → executor
（不带任何新信息，机械重复）

Reflexion 回边：
evaluator → reflection → actor
（带着反思教训，每次都比上次聪明）
```

### 8. 实验结果

```
第1次（失败）：语言偏宣传性，学术风格不足

反思内容：
"正式学术风格体现不够，语言偏宣传性，
 缺乏客观中立的学术论述语气"

第2次（通过）：
标题变成学术论文风格
语言客观中立，有分析性
```

**模型真的从反思中学到了东西！**

---

## 面试考点

**Q：Reflexion 是什么？核心思想是什么？**  
答：一种让 Agent 从失败中学习的机制。核心是三个组件：Actor执行任务、Evaluator评估结果、Reflection分析失败原因。反思内容会被存入记忆，塞进下一次的prompt，让每次尝试都比上次更好。

**Q：Reflexion 和普通重试有什么区别？**  
答：普通重试是机械重复，每次都可能犯同样的错误。Reflexion 在重试前先反思失败原因，把教训记录下来，下次带着这些教训重试，越试越聪明。

**Q：Reflexion 适合什么场景？**  
答：需要高质量输出的任务——代码生成（可以运行测试验证）、写作（有明确质量标准）、数学解题（可以验证答案）。不适合实时性要求高的场景，因为多次反思会增加延迟。

**Q：max_attempts 为什么重要？**  
答：防止无限循环。如果任务本身无法完成，或者评估标准过于苛刻，没有上限会导致 Agent 一直重试，消耗大量 token 和时间。

**Q：Reflexion 的 Evaluator 怎么设计？**  
答：取决于任务类型。代码任务最好直接运行代码看结果（客观）；写作任务可以用 LLM-as-Judge 评分；数学任务可以验证答案。评估标准要明确，太宽松触发不了反思，太严格可能永远通不过。

---

## 今日文件结构
```
week3/day19/
└── 01_reflexion.py  ✅ Actor+Evaluator+Reflection三节点，带教训重试
```

---

## 明天预告 — Day 20：多 Agent Supervisor 模式
- 为什么需要多个 Agent 协作
- Supervisor 模式：一个路由 Agent + 多个专家 Agent
- 用 langgraph-supervisor 实现
- 多 Agent 的优势和坑