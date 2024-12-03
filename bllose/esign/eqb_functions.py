from bllose.esign.Client import eqb_sign
from bllose.esign.esign_enums.env_enum import EqbEnum
import sys
import ctypes
import logging

def template_function(env, templateId) -> str:
    """
    通过templateId 获取到编辑模版地址
    Args:
        env(str): 环境 pro|test
        templateId(str): 模版ID
    Returns:
        shortUrl(str): 如果成功就是一个http开头的url，如果失败就是空
    """
    client = eqb_sign(EqbEnum.of(env).value)
    shortUrl = client.docTemplateEditUrl(templateId)
    post_handler(shortUrl=shortUrl)
    return shortUrl


def post_handler(shortUrl:str, savedPath:str = '') -> None:
    """
    后续处理，包括系统调用相关
    Args:
        shortUrl(str): 可以在页面上跳转的地址
        savedPath(str): 可以用于保存文件的本地路径
    """
    if shortUrl is not None or len(shortUrl) > 1:
        if sys.platform.startswith('win'):
            # 使用 ctypes 调用 ShellExecute
            shell32 = ctypes.windll.shell32
            result = shell32.ShellExecuteW(None, "open", shortUrl, '', None, 1)
            # result = shell32.ShellExecuteW(None, "open", fileDownloadUrl, f"/saveas /f:{self.download_path}", None, 1)
            if result <= 32:
                logging.error("Failed to open the download dialog. Error code: {}".format(result))



def set_title(title):
    """Set the terminal window title."""
    if sys.platform.startswith('win'):
        # 在 Windows 上使用 ctypes 设置控制台窗口标题
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:
        # 在其他平台上使用 ANSI 转义序列
        print(f"\033]0;{title}\007", end='', flush=True)