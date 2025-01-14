from bllose.esign.Client import eqb_sign
from bllose.esign.esign_enums.env_enum import EqbEnum
import sys
import ctypes
import logging
import requests
import base64
import json
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt


def template_function(env, templateId) -> str:
    """
    通过templateId 获取到编辑模版地址
    Args:
        env(str): 环境 pro|test
        templateId(str): 模版ID
    Returns:
        str: 如果成功就是一个http开头的url，如果失败就是空
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

def download_and_save_image(url, save_path):
    # 从网址下载文件
    response = requests.get(url)
    if response.status_code == 200:
        # 获取下载的内容
        base64_data = response.text
        try:
            # 对 base64 编码进行解码
            image_data = base64.b64decode(base64_data)
            # 将二进制数据转换为图片
            image = Image.open(BytesIO(image_data))
            # 保存图片
            image.save(save_path)
            print(f"Image saved to {save_path}")
        except Exception as e:
            print(f"Error occurred during decoding or saving image: {e}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def download_and_check_image(url):
    # 从网址下载文件
    response = requests.get(url)
    if response.status_code == 200:
        # 获取下载的内容
        base64_data = response.text
        try:
            # 对 base64 编码进行解码
            image_data = base64.b64decode(base64_data)
            # 将二进制数据转换为图片
            image = Image.open(BytesIO(image_data))
            plt.imshow(image)
            plt.axis('off')
            plt.show()
        except Exception as e:
            print(f"Error occurred during decoding or saving image: {e}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


def identity_detail(flowId:str, psnId:str = '', psnAccount:str = '', psnIDCardNum:str='', env: str = 'test') -> list:
    """
    Args:
        flowId(str): 签署流程编号
        psnId(str):
        psnAccount(str):
        psnIDCardNum(str):
    Returns:
        dict: 认证信息列表
    """
    client = eqb_sign(EqbEnum.of(env).value)
    data = client.person_info_v3(psnAccount=psnAccount, psnId=psnId, psnIDCardNum=psnIDCardNum)
    if len(data) < 1:
        return {}
    accountId = data['psnId']
    identity_list = client.identity_detail_v2(flowid=flowId, accountId=accountId)
    # for identity in identity_list:
    #     identityFlowId = identity['identityFlowId']
    #     identityType = identity['identityType']
    #     identityDetail = identity['identityDetail']
    #     identityBizType = identity['identityBizType']

    #     identityDetailJson = json.loads(identityDetail)
    #     facePhotoUrl = identityDetailJson['facePhotoUrl']
    #     download_and_check_image(url=facePhotoUrl)
    #     input("Press [enter] to continue.")
    return identity_list

def get_signer_details(client, flow_id, psn_id, org_id) -> list[dict]:
    identity_list = []
    if psn_id:
        identity_list.append({psn_id: client.identity_detail_v2(flowid=flow_id, accountId=psn_id)})
        if org_id:
            identity_list.append({psn_id: client.identity_detail_v2(flowid=flow_id, accountId=psn_id, orgId=org_id)})
    return identity_list

def sign_flow_identity_list(flowId: str, env: str = 'test') -> list:
    """
    通过签约流水，拿到签署人的刷脸信息
    """
    client = eqb_sign(EqbEnum.of(env).value)
    responseJson = client.getSignFlowDetail(signFlowId=flowId)
    data = responseJson['data']
    signers = data['signers']

    psn_ids = [signer.get('psnSigner', {}).get('psnId') for signer in signers if signer.get('psnSigner')]
    org_ids = [signer.get('orgSigner', {}).get('orgId') for signer in signers if signer.get('orgSigner')]
    
    identityDetailList = []
    for psn_id, org_id in zip(psn_ids, org_ids):
        identityDetailList.extend(get_signer_details(client, flowId, psn_id, org_id))
    return identityDetailList

# def psn_info_detail(psnId:str, env:str = 'test'):
#     """
#     通过用户id获取自然人详细信息
#     """
#     client = eqb_sign(EqbEnum.of(env).value)


if __name__ == '__main__':
    flowId = '5cc544dcbc9a492381ba1989412cd952'
    # identity_detail(flowId='5cc544dcbc9a492381ba1989412cd952', psnAccount='18970717838')
    signerIdList = sign_flow_identity_list(flowId=flowId)
    print(signerIdList)