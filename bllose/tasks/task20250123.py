from bllose.esign.Client import eqb_sign
from typing import Optional
import os
import requests



def download_file(url: str, save_path: Optional[str] = None) -> str:
    """
    使用requests从URL下载文件到本地
    
    Args:
        url: 下载链接
        save_path: 保存路径，如果不指定则使用URL中的文件名
        
    Returns:
        str: 保存文件的完整路径
        
    Raises:
        Exception: 下载过程中的各种异常
    """
    try:
        # 如果没有指定保存路径，从URL中获取文件名
        if not save_path:
            file_name = url.split('/')[-1]
            if not file_name:
                file_name = 'downloaded_file'
            save_path = file_name
            
        # 确保保存路径的目录存在
        save_dir = os.path.dirname(os.path.abspath(save_path))
        os.makedirs(save_dir, exist_ok=True)
        
        # 下载文件
        response = requests.get(url, timeout=(5, 30))
        response.raise_for_status()
        
        # 写入文件
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return os.path.abspath(save_path)
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"下载失败: {str(e)}")
    except Exception as e:
        raise Exception(f"保存文件失败: {str(e)}")



client = eqb_sign(env='pro')

file_path = r'd:/temp/task.txt'
save_path = r'd:/temp/saveContractFiles'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # strip() 去除行首行尾的空白字符（包括换行符）
            lineArray = line.strip().split(',')
            fileId = lineArray[0]
            name = lineArray[1]
            orderNo = lineArray[2]

            fileDownloadUrl = ''
            resultList = client.downloadContractByFlowId(fileId)
            for item in resultList:
                fileName = item['fileName']
                if '租赁' in fileName:
                    fileDownloadUrl = item['fileUrl']
                    break
            newFileName = f'{name}_{orderNo}.pdf'
            try:
                download_file(fileDownloadUrl, save_path +os.sep + newFileName)
            except Exception as e:
                print(f'下载失败: {str(e)}')
                print(f'文件ID: {fileId} {name} {orderNo}')
                continue

except Exception as e:
    raise Exception(f"读取文件失败: {str(e)}")
