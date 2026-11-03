from fastapi import Path,HTTPException
import re


WORKSPACES = Path(__file__).resolve().parent / "workspaces"
def get_output_dir(workspace_id:str)-> Path:
    output_dir = WORKSPACES / workspace_id / "output"
    if not output_dir.is_dir():
        raise HTTPException(status_code=404, detail="找不到输出目录")
    return output_dir.resolve()

def get_output_file(workspace_id:str, file_name:str) -> Path:  
    output_dir = get_output_dir(workspace_id)
    target = output_dir / file_name
    if not target.is_file():
        raise HTTPException(status_code=404, detail="找不到输出文件")
    if target.parent != output_dir:
        raise HTTPException(status_code=404, detail="文件路径不正确")
    
    return target

def get_file_list(workspace_id:str) -> list[dict]:
    output_dir = get_output_dir(workspace_id)
    file_list = []
    for path in sorted(output_dir.iterdir()):
        if not path.is_file():
            continue
        file_list.append(
            {
                "name": path.name,
                "size": path.stat().st_size,
            }
        )
    return file_list  