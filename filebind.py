from pathlib import Path
from fastapi import HTTPException



def file_binder(workspace_id: str) -> list[str]:
    WORKSPACES = Path(__file__).resolve().parent / "workspaces"
    WORKSPACES.mkdir(exist_ok=True)
    if workspace_id is None:
        return []
    filebinded = WORKSPACES/ workspace_id
    if not(filebinded/"data.csv").is_file():
        if((filebinded/"data.csv").is_dir()):             #第一版目前不允许上传文件夹~
            raise HTTPException(status_code=404, detail="期待一个文件而非文件夹")
        
        else:
            raise HTTPException(status_code=404, detail="找不到目标文件")
    return  [
        "--mount",
        f"type=bind,source={filebinded.resolve()},target=/workspace/input,readonly"
    ]