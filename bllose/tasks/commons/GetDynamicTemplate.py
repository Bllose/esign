import os
import time
import logging
from bllose.esign.Client import eqb_sign
from bllose.esign.Client import md5_base64_file
from bllose.esign.esign_enums.env_enum import EqbEnum


def uploadOneFile(abs_path:str, env:str = 'test'):
    if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
        logging.error(f"文件[{abs_path}]不存在!")
        return "", ""
    client: eqb_sign = eqb_sign(env=env)
    
    contentMd5=md5_base64_file(abs_path)
    file_name = os.path.basename(abs_path)
            
    # 1. 本地文件信息通知e签宝，获取上传地址
    fileId, fileUploadUrl = client.fetchUpdateFileUrl(contentMd5=contentMd5,
                            fileName=file_name,
                            fileSize=os.path.getsize(abs_path))
    logging.debug(f'文件ID:{fileId}, 上传地址:{fileUploadUrl}')
    if fileUploadUrl is not None and len(fileUploadUrl) > 1:
        # 2. 通过上传地址，真正将文件上传至e签宝
        code, reason = client.uploadFile(fileUploadUrl, contentMd5, abs_path)
        logging.debug('返回编码:', code, ' 返回信息:', reason)
        fileStatus = 0

        counter = 0
        while fileStatus != 2 and counter < 5:
            time.sleep(2)
            # 确认文件已经处理完毕，如果没有完成则循环确认
            fileName, fileDownloadUrl, fileStatus = client.fetchFileByFileId(fileId=fileId)
            counter += 1
        
        return fileName, fileId


def getEditUrl4AllFilesUnderTheRoot(root_path:str, env:str = 'test', convertToHTML:bool = True) -> list:
    """
    通过合同文件上传到e签宝，获取支持动态模版的html编辑页面
    1. 本地文件信息通知e签宝，获取上传地址
    2. 通过上传地址，真正将文件上传至e签宝
    3. 通过上传并转化为html的合同文件ID，获取对应的模版ID
    4. 通过模版ID获取编辑页面的地址

    Args:
        root_path(str): 需要处理的文件所在目录
        env(str): 处理环境，默认测试环境 test
        convertToHTML(bool): 是否转化为html
    Return:
        list: 返回编辑地址列表
            - fileName(str): 文件名字
            - templateId(str): 模版ID
            - editUrl(str): 编辑地址 
    """
    if not os.path.exists(root_path):
        logging.error(f'路径不存在，请检查入参地址正确性! --> {root_path}')
        return []
    
    resultList = []
    client: eqb_sign = eqb_sign(env=env)
    for root, dirs, files in os.walk(root_path):
        dirs = []
        for curFileName in files:
            upload_the_file(root=root, curFileName=curFileName, client=client, convertToHTML=convertToHTML, resultList=resultList)
    return resultList


def upload_the_file(root:str, curFileName: str, client: eqb_sign, convertToHTML: bool, resultList: list = []) -> tuple:
    """
    上传单个文件
    Args:
        root(str): 文件所在目录
        curFileName(str): 当前所要上传文件名字
        client(eqb_sign): e签宝客户端
        convertToHTML(bool): 是否要转化为HTML。True：转化为html；False：不转化
        resultList(list): 收集上传结果，可不传
    Returns:
        tuple: 若存在则返回模版ID,文件ID
            - templateId(str): 模版ID，不存在则为空字符串
            - fileId(str): 文件ID，不存在则返回空字符串
    """
    abs_path = root + os.sep + curFileName
    file_name = os.path.basename(abs_path)
    if file_name.startswith('~'):
        # 临时文件，直接跳过
        return

    contentMd5=md5_base64_file(abs_path)
    
    # 1. 本地文件信息通知e签宝，获取上传地址
    fileId, fileUploadUrl = client.fetchUpdateFileUrl(contentMd5=contentMd5,
                            fileName=file_name,
                            fileSize=os.path.getsize(abs_path),
                            convertToHTML=convertToHTML)
    logging.debug(f'文件ID:{fileId}, 上传地址:{fileUploadUrl}')
    if fileUploadUrl is not None and len(fileUploadUrl) > 1:
        # 2. 通过上传地址，真正将文件上传至e签宝
        code, reason = client.uploadFile(fileUploadUrl, contentMd5, abs_path)
        logging.debug('返回编码:', code, ' 返回信息:', reason)
        fileStatus = 0

        while fileStatus != 2:
            time.sleep(2)
            # 确认文件已经处理完毕，如果没有完成则循环确认
            fileName, fileDownloadUrl, fileStatus = client.fetchFileByFileId(fileId=fileId)
        
        # 只有当
        # 3. 通过上传并转化为html的合同文件ID，获取对应的模版ID
        templateId, templateUrl = client.docTemplateCreateUrl(fileId=fileId, 
                                    docTemplateName=file_name, 
                                    docTemplateType=1)
        # 4. 通过模版ID获取编辑页面的地址
        editUrl = client.docTemplateEditUrl(templateId)
        logging.debug(f'文件 ->{fileName}<- 生成模版ID ->{templateId}<- 编辑地址 ->{editUrl}<-')
        resultList.append({'fileName': fileName, 'templateId': templateId, 'editUrl': editUrl, 'fileId': fileId})
        return templateId, fileId

    return '', ''

def uploadAndConvert2Html(abs_path: str, convertToHTML: bool = False, env: str = 'test'):
    """
    上传本地文件，并可以转化为HTML的模版
    Args:
        abs_path(str) : 上传文件的绝对路径
        convertToHTML(bool): 是否转化为HTML模版
        env(str): 环境
    """
    root = os.path.dirname(abs_path)
    fileName = os.path.basename(abs_path)
    client = eqb_sign(env=EqbEnum.of(env).value)
    templateId, fileId = upload_the_file(root=root, curFileName=fileName, client=client, convertToHTML=convertToHTML)
    return templateId, fileId


def getEditUrlByTemplateId(templateIdList:list, env:str = 'test') -> list:
    """
    通过templateId 获取最新的编辑地址 24小时有效

    Args:
        templateIdList(str): 模版ID列表
        env(str): e签宝环境，默认测试环境 test
    Returns:
        editUrlList(list): 编辑地址列表
            - templateId(str): 模版ID
            - editUrl(str): 编辑地址
    """
    if templateIdList is None or len(templateIdList) < 1:
        return []
    resultList = []
    client: eqb_sign = eqb_sign(env=env)
    for templateId in templateIdList:
        editUrl = client.docTemplateEditUrl(templateId)
        resultList.append({'templateId': templateId, 'editUrl': editUrl})
    
    return resultList

if __name__ == '__main__':
    # templateIdList = ['d616ffcddf8d4642ab17ed41fbf05e98',
    #                   '88dba2a4f4c540cbadf9196d555f5924',
    #                   'a8bedae030784de4aa58e955e65ba753',
    #                   'f601ec924e5c4e3ab5af86ce9e614061',
    #                   '8f61b4e4058248d69ceb319e6241cea6',
    #                   'eecc2d735fa04697bad4fb3aa9e46b87',
    #                   '4a4bbd60d8354b3cbedcd23ce7c9ef6d']
    # print(getEditUrlByTemplateId(templateIdList, env='test'))

    newFileDir = r'C:\Users\bllos\Desktop\20241218生僻字'
    # print(getEditUrl4AllFilesUnderTheRoot(root_path=newFileDir, convertToHTML=False))
    fileName = '光伏电站屋顶租赁协议（B端无共签人）20241128_release.pdf'
    print(uploadOneFile(newFileDir + os.sep + fileName))