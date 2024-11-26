import os
import time
import logging
from bllose.esign.Client import eqb_sign
from bllose.esign.Client import md5_base64_file


def getEditUrl4AllFilesUnderTheRoot(root_path:str, env:str = 'test') -> list:
    """
    通过合同文件上传到e签宝，获取支持动态模版的html编辑页面
    1. 本地文件信息通知e签宝，获取上传地址
    2. 通过上传地址，真正将文件上传至e签宝
    3. 通过上传并转化为html的合同文件ID，获取对应的模版ID
    4. 通过模版ID获取编辑页面的地址

    Args:
        root_path(str): 需要处理的文件所在目录
        env(str): 处理环境，默认测试环境 test
    Return:
        editInfoList(list): 返回编辑地址列表
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
        for curFileName in files:
            abs_path = root + os.sep + curFileName
            file_name = os.path.basename(abs_path)
            contentMd5=md5_base64_file(abs_path)
            
            # 1. 本地文件信息通知e签宝，获取上传地址
            fileId, fileUploadUrl = client.fetchUpdateFileUrl(contentMd5=contentMd5,
                                    fileName=file_name,
                                    fileSize=os.path.getsize(abs_path),
                                    convertToHTML=True)
            logging.debug(f'文件ID:{fileId}, 上传地址:{fileUploadUrl}')
            if fileUploadUrl is not None:
                # 2. 通过上传地址，真正将文件上传至e签宝
                code, reason = client.uploadFile(fileUploadUrl, contentMd5, abs_path)
                logging.debug('返回编码:', code, ' 返回信息:', reason)
                fileStatus = 0

                while fileStatus != 2:
                    time.sleep(2)
                    # 确认文件已经处理完毕，如果没有完成则循环确认
                    fileName, fileDownloadUrl, fileStatus = client.fetchFileByFileId(fileId=fileId)
                
                # 3. 通过上传并转化为html的合同文件ID，获取对应的模版ID
                templateId, templateUrl = client.docTemplateCreateUrl(fileId=fileId, 
                                            docTemplateName=file_name, 
                                            docTemplateType=1)
                
                # 4. 通过模版ID获取编辑页面的地址
                editUrl = client.docTemplateEditUrl(templateId)
                logging.debug(f'文件 ->{fileName}<- 生成模版ID ->{templateId}<- 编辑地址 ->{editUrl}<-')
                resultList.append({'fileName': fileName, 'templateId': templateId, 'editUrl': editUrl})
    return resultList


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
    # templateIdList = ['8f61b4e4058248d69ceb319e6241cea6']
    # print(getEditUrlByTemplateId(templateIdList, env='test'))

    newFileDir = r'C:\Users\bllos\Desktop\[4823119319] 代理商申请TCL设计服务流程线上化 合同部分开发\doc'
    print(getEditUrl4AllFilesUnderTheRoot(newFileDir))