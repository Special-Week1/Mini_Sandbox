from fastapi import  UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
from filebind import file_binder

WORKSPACES = Path(__file__).resolve().parent / "workspaces"
WORKSPACES.mkdir(exist_ok=True)

#创建上传函数
def upload_file(file: UploadFile = File(...)) ->dict:
    workspace_id = uuid.uuid4().hex

    input_id = WORKSPACES / workspace_id 
    input_id.mkdir(parents=True,exist_ok=True)
    target_path = input_id / "data.csv"
    try:
        with open(target_path, "wb") as savefile:
            total_size = 0
            
            while chunk :=  file.file.read(1024*1024):#限制上传量，这里采用每次1MB，五轮计算方式
                
                    total_size +=len(chunk)
                    

                    if total_size >= 5*1024*1024: #判定上传无效，多余部分舍弃
                        raise HTTPException(status_code=400, detail="文件太大啦不要超过5MB") #鬼知道报错代码是啥啊随便400喽
                    savefile.write(chunk)
    except Exception:
        target_path.unlink(missing_ok=True)
        input_id.rmdir()
        raise
    finally:
            file.file.close()

    file_binder_args = file_binder(workspace_id)
    return{
        "workspace_id": workspace_id,
        "file_name": "data.csv",
        "size": total_size,
        "file_binder_args": file_binder_args
    }#返回空间id,文件名以及文件大小


"""def file_binder(workspace_id: str) -> list[str]:
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
        f"type=bind,source={filebinded.resolve()},target=/workspace/input"
    ]
        """      
              
