import argparse
import httpx
import json
from pathlib import Path
import os

from openai import OpenAI

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))      #加载.env配置文件


def generate_code(task: str) -> str:
    instructions = """
你负责根据用户需求编写处理单个 CSV 的 Python 脚本。

- 读取 /workspace/input/data.csv，使用 utf-8-sig 编码。
- 只使用 Python 标准库，例如 csv 和 pathlib。
- 将生成的文件写到 /workspace/output/。
- 用 print() 简短说明生成了什么文件。
- 只返回 Python 源码，不要附加解释或 Markdown 代码围栏。
"""
    with OpenAI(
        base_url=os.environ["CSV_AGENT_BASE_URL"],
        api_key=os.environ["CSV_AGENT_API_KEY"],
        timeout=60,
    ) as client:
        response = client.chat.completions.create(
            model=os.environ["CSV_AGENT_MODEL"],
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": task},
            ],
        )

    if not response.choices:
        raise RuntimeError("模型接口没有返回候选结果。")

    code = (response.choices[0].message.content or "").strip()
    lines = code.splitlines()
    if (
        len(lines) >= 2
        and lines[0].strip().lower() in ("```python", "```py", "```")
        and lines[-1].strip() == "```"
    ):
        code = "\n".join(lines[1:-1]).strip()   
    if not code:
        raise RuntimeError("模型没有返回 Python 代码。")

    return code























def run_with_file(csv_path:Path,code: str)->dict:        #向本地Localhost发送请求(模拟agent)
    with csv_path.open("rb") as csv_file:
        response = httpx.post(
            "http://localhost:8000/upload",
            files={"file": (csv_path.name, csv_file,"text/csv")},
            params={"codex": code},
            timeout=10,
        )
    return response.json()













def main():                                   #发送指令
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path",type=Path,help="本地上传的文件<csv>地址")
    args = parser.parse_args()
    task = input("你想怎么处理这份 CSV？").strip()
    if not task:
        raise SystemExit("请输入处理需求。")

    code = generate_code(task)  # 你接下来要实现的模型调用
    
    data = run_with_file(args.csv_path, code)
    print(json.dumps(data, indent=2))

    if data["result"]["status"] != "completed":
        raise RuntimeError(f"任务未成功完成，状态为: {data['result']['status']}")



if __name__ == "__main__":
    main()