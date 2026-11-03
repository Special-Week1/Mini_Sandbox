from fastapi import FastAPI,Path,Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import subprocess
import uuid

import fileupload


app = FastAPI()

class ExecuteRequest(BaseModel):           #定义传入类
    code: str = Field(min_length=1, max_length=16000)
    timeout_seconds: int= Field(..., ge=1, le=10)


def run_in_docker(code: str,
                  file_binder_args: list[str] | None =None,
                  timeout_seconds: int=2 ) -> dict:           #唤起docker并且在3.12-apline版本下执行  V1.1增加文件夹读入功能，为后续agent代码执行准备
#    file_binder_args = fileupload.file_binder(workspace_id)
    container_name = "Mini_Sandbox-"+uuid.uuid4().hex
    if file_binder_args is None:
        file_binder_args = []
    try:
        result = subprocess.run(
                [
                    "docker", "run",
                    "--name", container_name,
                    "--pull", "never",
                    "--rm",
                    "--network", "none",
                    "--memory", "128m",
                    "--cpus", "0.5",
                    "--pids-limit", "64",
                    *file_binder_args,
                    "python:3.12-alpine",
                    "python", "-u", "-c", code,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,  # 使用请求传来的时间
            )
        return{
            "status": "completed" if result.returncode == 0 else "failed",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "status":"timeout",
            "stdout":"",
            "stderr":"超时",
            "exit_code": None,
        }
    finally:
        try:                                                            #删除容器
            cleanup = subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if cleanup.returncode == 0:                     #如果删除成功
                print(f"Container {container_name} cleaned up successfully")
            else: print(f"Failed to clean up container {container_name}") #删除失败
        except Exception as e:
            print(f"Error occurred while cleaning up container {container_name}: {e}")



@app.post("/execute")                   #拉起fastapi网站
def execute(request: ExecuteRequest):
    code = request.code
    result=run_in_docker(code, None, request.timeout_seconds)   #调用docker执行函数
    return result

@app.post("/upload")                        #拉起文件上传
def upload(file: fileupload.UploadFile = fileupload.File(...),
           codex: str = Query(..., min_length=1, max_length=16000)):
    upload_result = fileupload.upload_file(file)
    result = run_in_docker(code=codex, file_binder_args=upload_result["file_binder_args"], timeout_seconds=5)
    #print(upload_result["file_binder_args"])
    return result

"""@app.post("/bind_files")
def bind_files(request: ExecuteRequest):
   return run_in_docker(
        code=request.code,
        workspace_id=request.workspace_id,
        timeout_seconds=request.timeout_seconds,
    )"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
