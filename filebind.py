from pathlib import Path
from fastapi import HTTPException



def file_binder(workspace_id: str) -> list[str]:
    WORKSPACES = Path(__file__).resolve().parent / "workspaces"
    WORKSPACES.mkdir(exist_ok=True)
    if workspace_id is None:
        return []
    filebinded = WORKSPACES/ workspace_id
    input_dir = filebinded / "input"
    output_dir = filebinded / "output"
    if not(input_dir/"data.csv").is_file():
        if((input_dir/"data.csv").is_dir()):             #第一版目前不允许上传文件夹~
            raise HTTPException(status_code=404, detail="期待一个文件而非文件夹")
        
        else:
            raise HTTPException(status_code=404, detail="找不到目标文件")
    output_dir.mkdir(exist_ok=True)                #处理之后的输出环节
    return  [
        "--mount",
        f"type=bind,source={input_dir.resolve()},target=/workspace/input,readonly",
        "--mount",
        f"type=bind,source={output_dir.resolve()},target=/workspace/output",         #输出文件
    ]