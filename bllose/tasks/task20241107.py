import logging
from bllose.esign.Client import eqb_sign

client = eqb_sign(env='pro')

# 第一步： 将问题合同文件下载下来
# fileList = ['c460dfbc8ee548a48dc71ebf1ca88cc1', '7773c6eccd5a487f9683ca06b73f8a9d']
# for file in fileList:
#     fileName, downloadUrl = client.fetchFileByFileId(fileId = file)
#     print(f'Name:{fileName} -> url:{downloadUrl}')

# 第二步：将修改好的文件重新上传，并获得文件的fileId
# uploadFileList = [r'C:\Users\bllos\Desktop\2024年11月7日生僻字生产合同问题解决\GF240921114822112648_光伏电站屋顶租赁协议（B端无共签人）20240604.pdf', 
#                   r'C:\Users\bllos\Desktop\2024年11月7日生僻字生产合同问题解决\GF241016115633116953_光伏电站屋顶租赁协议（B端无共签人）20240604.pdf']
# import os    
# for absFilePath in uploadFileList:
#     file_md5_base64 = md5_base64_file(absFilePath)
#     file_name = os.path.basename(absFilePath)
#     file_size = os.path.getsize(absFilePath)

#     fileId, uploadUrl = client.fetchUpdateFileUrl(file_md5_base64, file_name, file_size)

#     code, reason = client.uploadFile(uploadUrl, file_md5_base64, absFilePath)

#     print(f'文件:{fileId}的上传结果 -> code:{code} reason:{reason}')

# 第三部：组装一步发起签约请求，并获取签约流水号
# 1、通过农户三要素获取农户的 accountId
# 2、通过项目公司的社会统一信用代码获取公章ID sealId
# 3、结合前面的fileId，组装请求报文
# fileList = [r'88378c912504402e8a45a6b78bdf5347', r'03d4859795334de89acc57a5362f44ab']
# for fileId in fileList:
#     if fileId == '88378c912504402e8a45a6b78bdf5347':
#         accountId = client.getAccountId('李颖', '120225199012115566', '13323470782')
#     elif fileId == '03d4859795334de89acc57a5362f44ab':
#         accountId = client.getAccountId('纪建伟', '120224198501281919', '15122299005')
#     sealId = '296b3645-3ac1-4d53-99a6-c00792679035'
#     request_template = r'{"docs":[{"fileId":"{fileId}","fileName":"光伏电站屋顶租赁协议（B端无共签人）.pdf"}],"flowInfo":{"autoArchive":true,"autoInitiate":true,"businessScene":"光伏电站屋顶租赁协议","flowConfigInfo":{"noticeDeveloperUrl":"https://callback1-pv.tcl.com/api/app/contract/unify/signed/callback/eqb","noticeType":"","redirectUrl":"","signPlatform":"1","willTypes":["FACE_TECENT_CLOUD_H5"]}},"signers":[{"platformSign":false,"signOrder":1,"signerAccount":{"signerAccountId":"{accountId}"},"signfields":[{"autoExecute":false,"fileId":"{fileId}","sealType":"0","signDateBean":{"posPage":5,"posX":134.12,"posY":81.95825},"posBean":{"posPage":"5","posX":224.12,"posY":183.63928},"signDateBeanType":2}]},{"platformSign":false,"signOrder":1,"signerAccount":{"signerAccountId":"{accountId}"},"signfields":[{"autoExecute":false,"fileId":"{fileId}","sealType":"0","posBean":{"posPage":"6","posX":198.88,"posY":446.43927}}]},{"platformSign":true,"signOrder":2,"signfields":[{"autoExecute":true,"actorIndentityType":"2","fileId":"{fileId}","posBean":{"posPage":"5","posX":214.12,"posY":137.79926},"sealId":"{sealId}"}]}]}'
#     requestContent = request_template.replace(r'{fileId}',fileId).replace(r'{accountId}', accountId).replace(r'{sealId}', sealId)
#     flowId = client.createFlowOneStep(requestContent)
#     print(f'通过文件{fileId}发起的签约流水号{flowId}')

# 第四步： 通过签约流水号获取签约地址
flowIdList = ['86178277820244868670d5299cf284c5', '34a1a240c18e4dad96ccc8056ba1231f']
for flowId in flowIdList:
    if flowId == '86178277820244868670d5299cf284c5':
        mobile = r'13323470782'
    elif flowId == '34a1a240c18e4dad96ccc8056ba1231f':
        mobile = r'15122299005'
    shortUrl = client.getH5Url(mobile, flowId)
    print(f'流水号{flowId}的签约地址为{shortUrl}')
