# Mini Agent Sandbox

一个用 Python、FastAPI 和 Docker 实现的学习项目：通过 HTTP 接收 Python 代码，在独立容器中运行，收集输出并清理容器。

本阶段为 V2 文件输入版本。支持纯代码执行，也支持上传 CSV 后挂载到容器执行。输出文件下载和真实 Agent 接入尚未实现。

## 项目目标

围绕 Agent Runtime 基础设施方向建立可解释、可验证的实践经验，重点理解代码执行、文件传递、容器生命周期和资源隔离。当前 Python 服务用于先跑通完整流程，后续补充并发调度、状态持久化、日志和故障排查。

岗位准备还包括 Go / Rust / C / C++ 至少一门语言，以及 Linux、数据结构、算法、操作系统和网络基础；本项目是其中的实践部分。

## 当前执行流程

```text
POST /execute：JSON 代码 → FastAPI → Docker → stdout / stderr / exit_code

POST /upload：CSV 文件 + 查询参数 codex
    → 保存到 workspaces/<随机ID>/data.csv
    → 只读挂载至容器 /workspace/input
    → 执行代码 → 收集结果 → 删除容器
```

## 文件结构

```text
main.py          HTTP 接口、Docker 执行和容器回收
fileupload.py    上传文件保存、大小检查、工作空间创建
filebind.py      生成 Docker 只读挂载参数
requirements.txt Python 依赖
workspaces/      本地上传文件，不提交 Git
source_csv/      本地测试数据，不提交 Git
```

## 本地运行

需要 Python 3.10 及以上版本、已启动的 Docker，以及本地可用的 `docker` 命令。以下命令适用于 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker pull python:3.12-alpine
.\.venv\Scripts\python.exe main.py
```

打开 <http://127.0.0.1:8000/docs>。

执行器使用 `--pull never`，因此必须提前下载镜像。Docker daemon 需要能访问项目所在的磁盘路径。

### 纯代码执行

在 `/docs` 的 `POST /execute` 提交：

```json
{
  "code": "print(1 + 2)",
  "timeout_seconds": 10
}
```

成功返回示例：

```json
{
  "status": "completed",
  "stdout": "3\n",
  "stderr": "",
  "exit_code": 0
}
```

`timeout_seconds` 为必填整数，范围为 1～10 秒。

### 上传 CSV 并执行

在 `/docs` 的 `POST /upload` 选择一个 UTF-8 CSV 文件，在查询参数 `codex` 中填写：

```python
from pathlib import Path
print(Path('/workspace/input/data.csv').read_text(encoding='utf-8-sig'))
```

上传文件统一保存为 `data.csv`。`codex` 是查询参数，文件通过 multipart 请求体上传。当前上传接口固定等待 5 秒，并返回执行结果。

## 当前限制与待改进项

- Docker 配置了禁用网络、128 MiB 内存、0.5 CPU 和 64 个 PID 的限制；输入目录只读。当前未配置非 root 用户、只读容器根文件系统等进一步隔离措施。
- 超时包含 Docker 启动时间；首次启动较慢时，简单代码也可能超时。超时后会主动删除对应容器。
- 清理命令尚无独立超时；正常退出后容器可能已由 `--rm` 删除，此时额外清理可能输出失败提示。
- 当前文件大小条件为 `>= 5 MiB`，因此恰好 5 MiB 也被拒绝，响应状态为 400。
- 工作空间文件会保留在宿主机，尚无自动过期清理。
- `/upload` 尚未返回工作空间 ID，也没有输出目录挂载、文件下载、任务队列、认证和持久化。
- 当前适合本地可信代码实验；普通 Docker 容器不代表对任意恶意代码的完整安全隔离。

## 后续版本

1. V3 文件输出：可写输出目录、结果文件标识、下载接口。
2. Agent 调用：由客户端或 Agent 提交代码、读取结果并获取输出文件。
3. 任务管理：任务 ID、并发上限、排队、取消和状态持久化。
4. 运行与排障：结构化日志、耗时记录、失败实验、启动性能测量与清理恢复。
5. 按实际需要进一步学习 Go、Linux、Kubernetes 和更强的隔离机制。

## 本阶段验证记录

2026-11-03，Windows 本地 Docker 环境：

- 纯代码执行 `print(1+2)` 返回 `3`；第一次 5 秒等待曾超时，后续 10 秒和 5 秒重试均成功。
- 上传 CSV 后，容器读取 `/workspace/input/data.csv` 成功。
- 恰好 5 MiB 的上传被拒绝，记录为后续边界修正项。

依赖版本记录自当前开发环境；容器镜像使用 `python:3.12-alpine` 标签，尚未固定 digest。
