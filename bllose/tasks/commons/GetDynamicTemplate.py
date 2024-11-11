import os
import time
from bllose.esign.Client import eqb_sign
from bllose.esign.Client import md5_base64_file

"""
通过合同文件上传到e签宝，获取支持动态模版的html编辑页面
1. 本地文件信息通知e签宝，获取上传地址
2. 通过上传地址，真正将文件上传至e签宝
3. 通过上传并转化为html的合同文件ID，获取对应的模版ID
4. 通过模版ID获取编辑页面的地址
"""
client: eqb_sign = eqb_sign(env='test')
root_path = r'C:\Users\bllos\Desktop\[4975116715] 中信建设期二次放款系统对接——结算（含退货）模块'
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
        print(f'文件ID:{fileId}, 上传地址:{fileUploadUrl}')
        if fileUploadUrl is not None:
            # 2. 通过上传地址，真正将文件上传至e签宝
            code, reason = client.uploadFile(fileUploadUrl, contentMd5, abs_path)
            print('返回编码:', code, ' 返回信息:', reason)
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
            print(f'文件 ->{fileName}<- 生成模版ID ->{templateId}<- 编辑地址 ->{editUrl}<-')

print('DONE!')