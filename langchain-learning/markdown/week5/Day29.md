# Day 29 复盘笔记 — 生产部署概念（Docker/Nginx/CI-CD）

## 今天学了什么

### 1. Docker

**解决什么问题：** 环境不兼容——"在我电脑上能跑"问题

```
没有 Docker：
你电脑：Python 3.12、torch 2.3、Windows
服务器：Python 3.9、torch 2.0、Linux
结果：跑不起来！

有 Docker：
把程序 + 所有环境打包在一起
无论在哪台机器运行 → 环境完全一样
```

**三个核心概念：**
```
Dockerfile → 菜谱（描述怎么构建环境）
Image      → 做好的菜（可以分享给别人）
Container  → 上桌的那盘菜（真正在运行的实例）

关系：Dockerfile → build → Image → run → Container
```

**Dockerfile 示例：**
```dockerfile
FROM python:3.12-slim          # 基础镜像（地基）
WORKDIR /app                   # 设置工作目录
COPY requirements.txt .        # 先复制依赖文件（利用缓存）
RUN pip install -r requirements.txt  # 安装依赖
COPY . .                       # 复制代码
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**为什么先 COPY requirements.txt 再 COPY 代码？**
Docker 有层缓存——requirements.txt 不变就不重新安装依赖，每次改代码重新构建很快。

**核心命令：**
```bash
pip freeze > requirements.txt        # 生成依赖文件
docker build . -t myapp              # 构建镜像
docker run -p 8000:8000 myapp        # 启动容器
docker ps                            # 查看运行中的容器
docker stop container_id             # 停止容器
```

---

### 2. Nginx

**uvicorn 的弱点：**
```
性能差  → 处理静态文件慢
安全弱  → 直接暴露公网容易被攻击
单点    → 一台服务器只能跑一个实例
```

**Nginx 的三个作用：**
```
1. 反向代理  → 隐藏后端，统一入口，过滤恶意请求
2. 负载均衡  → 分发请求给多个 uvicorn 实例
3. 静态文件  → 直接处理图片/CSS，不经过 Python（快10倍）
```

**架构：**
```
用户请求
    ↓
Nginx（反向代理）
    ↓         ↓         ↓
uvicorn1  uvicorn2  uvicorn3
```

**Nginx 配置示例：**
```nginx
server {
    listen 80;
    
    location / {
        proxy_pass http://127.0.0.1:8000;  # 转发给 uvicorn
    }
    
    location /static/ {
        root /app/static;  # 静态文件直接处理
    }
}
```

**比喻：**
```
Nginx = 前台接待员（统一接收请求，分发给后台）
uvicorn = 后台工作人员（真正处理业务）
```

**负载均衡 vs Supervisor：**
```
Supervisor（Agent）：LLM 理解语义，智能分配任务
负载均衡（Nginx）：按规则机械分配，不理解内容
  - 轮询：依次分发给每个实例
  - 最少连接：给最闲的实例
  - IP哈希：同一用户永远去同一实例
```

---

### 3. CI/CD

**手动部署流程（痛苦）：**
```
改完代码 → git push → ssh登服务器 → git pull → 
pip install → 重启uvicorn → 手动测试
每次都要做，容易出错
```

**CI/CD 自动化：**
```
CI（持续集成）：git push → 自动跑测试 → 测试通过才合并
CD（持续部署）：代码合并 → 自动构建 → 自动部署 → 自动重启
```

**GitHub Actions 配置：**
```yaml
name: 自动部署
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: 运行测试
        run: python -m pytest tests/
      - name: 构建镜像
        run: docker build -t brake-agent .
      - name: 部署
        run: ssh user@server "docker restart brake-agent"
```

**CI/CD 的核心价值：**
```
先跑测试再部署 → 有 bug 的代码永远到不了用户那里
你只需要 git push，剩下全自动
保护生产环境稳定性
```

---

## 三个工具的分工

```
Docker  → 解决"跑得起来"的问题（环境一致性）
Nginx   → 解决"跑得好"的问题（性能/安全/扩展）
CI/CD   → 解决"更新方便"的问题（自动化部署）
```

---

## 面试考点

**Q：Docker 解决什么问题？**  
答：环境不兼容问题。把程序和它依赖的所有环境打包成镜像，无论在哪台机器运行环境都完全一样，彻底解决"在我电脑上能跑"的问题。

**Q：为什么生产环境要用 Nginx？**  
答：三个原因：反向代理（隐藏后端、过滤恶意请求）、负载均衡（分发请求给多个实例）、静态文件处理（比Python快10倍）。uvicorn 直接暴露公网安全性差、性能有瓶颈。

**Q：CI/CD 是什么？有什么好处？**  
答：持续集成/持续部署，自动化部署流水线。git push 后自动跑测试，测试通过才自动构建和部署，有bug的代码永远到不了生产环境。减少人工操作失误，保护生产稳定性。

**Q：Dockerfile 里为什么先 COPY requirements.txt 再 COPY 代码？**  
答：利用 Docker 的层缓存机制。requirements.txt 不变就不重新安装依赖，每次改代码重新构建时直接用缓存，大幅加快构建速度。

---

## 今日文件结构
```
week5/day29/
└── （今天只讲概念，无代码文件）
```

---

## 明天预告 — Day 30：监控告警 + 生产最佳实践
- 应用监控：如何发现线上问题
- 结构化日志：方便排查问题
- 健康检查接口
- 生产环境最佳实践清单