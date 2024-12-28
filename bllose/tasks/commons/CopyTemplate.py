from bllose.esign.Client import eqb_sign
from bllose.tasks.commons.GetDynamicTemplate import upload_the_file
from bllose.helper.JsonHelper import deep_clean_null
from urllib.parse import parse_qs, urlparse
from urllib.request import urlretrieve
import os
import requests


def get_encryption(client: eqb_sign, templateId: str) -> str:
    """
    通过模版id获取到访问请求的秘钥
    - encryption
    - docTemplateId
    - appId
    - scene
    Args:
        client(eqb_sign): e签宝客户端对象
        templateId(str): 模版id
    Returns:
        encryption(str): 请求秘钥
    """
    _, longUrl = client.docTemplateEditUrlAll(templateId)
    return analy_url(longUrl=longUrl)

def analy_url(longUrl: str) -> str:
    parsed_url = urlparse(longUrl)
    query_params = parse_qs(parsed_url.query)
    if query_params is None or 'encryption' not in query_params:
        raise ValueError('获取请求秘钥失败')
    return query_params['encryption'][0]


def download_file_urllib(url, local_filename):
    urlretrieve(url, local_filename)
    return local_filename


def check_redirect(url):
    try:
        response = requests.head(url, allow_redirects=False)
        if 'location' in response.headers:
            return response.headers['location']
        else:
            return url  # 如果没有重定向，则返回原始URL
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise

def copy(origin_env:str, target_env:str, template_id:str) -> tuple:
    
    # 在源环境中下载模版文件
    # 并获取组件报文信息
    originClient = eqb_sign(env=origin_env)
    response_json = originClient.getDocTemplateDetails(template_id, get_encryption(originClient, template_id))
    downloadUrl = response_json['downloadUrl']
    fileName = 'd:/temp/' +response_json['templateName'] + '.html'
    local_filename = download_file_urllib(downloadUrl, fileName)
    root = os.path.dirname(local_filename)
    fileName = os.path.basename(local_filename)


    targetClient = eqb_sign(env=target_env)
    # 将文档上传到指定环境
    _, fileId = upload_the_file(root=root, curFileName=fileName, client=targetClient, convertToHTML=False)
    # 将上传后的文件做成模版，并获取编辑模版的地址
    templateIdNew, docTemplateCreateUrl = targetClient.docTemplateCreateUrl(fileId=fileId, docTemplateName=fileName, docTemplateType=1)
    # 从编辑地址跳转的长连接中获取到必要参数
    redirectedUrl = check_redirect(docTemplateCreateUrl)
    encryptionNew = analy_url(redirectedUrl)

    # 对目标环境中新建的模版更新组件信息
    requestBody = deep_clean_null({
        'templateFileId': fileId,
        'structComponents': [{**component, 'id': None} for component in response_json['structComponents']]
    })
    targetClient.updateDocTemplateComponents(templateId=templateIdNew, encryption=encryptionNew, requestBody=requestBody)
    return template_id, templateIdNew


if __name__ == '__main__':
    try:
        template_id, templateIdNew = copy('pro', 'test', '8dc8b8c5cfe24c088ab2ae7fbbecafc0')
    except ValueError:
        template_id, templateIdNew = copy('test', 'test', '8dc8b8c5cfe24c088ab2ae7fbbecafc0')
    print(template_id, templateIdNew)