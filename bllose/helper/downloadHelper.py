import ctypes
import os

def download_file(url, save_path):
    # 确保保存路径存在
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 获取文件名
    file_name = os.path.basename(url)
    full_save_path = os.path.join(save_path, file_name)

    # 使用 ctypes 调用 ShellExecute
    shell32 = ctypes.windll.shell32
    result = shell32.ShellExecuteW(None, "open", url, f"/saveas /f:{full_save_path}", None, 1)

    if result <= 32:
        raise Exception("Failed to open the download dialog. Error code: {}".format(result))

# 示例使用
url = "https://esignoss.esign.cn/1111563774/91eb927c-7359-43ef-8120-5af9fff8a965/%E8%BF%90%E7%BB%B4%E9%99%84%E8%A1%A8%E9%99%84%E4%BB%B6%E4%B8%80%EF%BC%88%E5%BB%BA%E8%AE%BE%E6%9C%9F%E4%BA%8C%E6%9C%9F%EF%BC%89?Expires=1732895088&OSSAccessKeyId=LTAI4G23YViiKnxTC28ygQzF&Signature=vBYW3FnQJAr4jp1EHGrCfRObLcM%3D"
save_path = "C:\\Downloads"

try:
    download_file(url, save_path)
    print(f"Download dialog opened for {url} and will save to {save_path}")
except Exception as e:
    print(f"Error: {e}")