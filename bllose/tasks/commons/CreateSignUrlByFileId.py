import json
from attrs import asdict
from bllose.config.Config import bConfig
from bllose.helper.JsonHelper import deep_clean_null
from bllose.esign.Client import eqb_sign
from bllose.esign.sign_flow_vos.signFlowByFileVo import SignFlowByFile
from bllose.esign.sign_flow_vos.signFlowByFile.Docs import Docs
from bllose.esign.sign_flow_vos.signFlowByFile.Signers import Signers
from bllose.esign.sign_flow_vos.signFlowByFile.SignFlowConfig import SignFlowConfig, NoticeConfig
from bllose.esign.sign_flow_vos.signFlowByFile.signers.SignConfig import SignConfig
from bllose.esign.sign_flow_vos.signFlowByFile.signers.SignFields import SignField, NormalSignFieldConfig, SignFieldPosition
from bllose.esign.sign_flow_vos.signFlowByFile.signers.OrgSignerInfo import OrgSignerInfo, OrgInfo, PsnInfo, TransactorInfo

"""
通过已经生成号的文件ID
生成一个新的签署地址
"""
@bConfig()
def task(notice:bool = False, env:str = 'test', config:dict = {}) -> tuple:
    if env.lower() == 'pro':
        env = 'pro'
    else :
        env = 'test'

    client = eqb_sign(env=env)
    fileId = 'd3c8e7c4c26e49819060dfbb31fcbb63'

    signFlowByFile = SignFlowByFile()
    doc = Docs(fileId= fileId, fileName='租金表合同')

    signFlowConfig = SignFlowConfig(signFlowTitle = '租金表合同')
    signFlowConfig.autoFinish = True
    signFlowConfig.autoStart = True
    signFlowConfig.notifyUrl = config['eqb'][env]['callbackUrl']
    if notice == True:
        noticeConfig = NoticeConfig()
        noticeConfig.noticeTypes = '1'
        signFlowConfig.noticeConfig = noticeConfig

    signFlowByFile.docs = [doc]
    signFlowByFile.signFlowConfig = signFlowConfig


    signer = Signers(signerType = 1)
    signer.signConfig = SignConfig()
    if notice == True:
        noticeConfig = NoticeConfig()
        noticeConfig.noticeTypes = '1'
        signer.noticeConfig = noticeConfig

    # 公章
    signField = SignField(fileId = fileId)

    normalSignFieldConfig = NormalSignFieldConfig()
    normalSignFieldConfig.autoSign = False
    normalSignFieldConfig.signFieldStyle = 1
    normalSignFieldConfig.assignedSealId = 'c2bbcdc9-f033-4473-9518-f3a07919bc95'

    signFieldPosition = SignFieldPosition()
    signFieldPosition.positionX = 138.0
    signFieldPosition.positionY = 581.79596
    signFieldPosition.positionPage = 4

    normalSignFieldConfig.signFieldPosition = signFieldPosition
    signField.normalSignFieldConfig = normalSignFieldConfig

    # 法人章
    representSignField = SignField(fileId = fileId)

    reNormalSignFieldConfig = NormalSignFieldConfig()
    reNormalSignFieldConfig.autoSign = False
    reNormalSignFieldConfig.signFieldStyle = 1
    reNormalSignFieldConfig.assignedSealId = '368fc7de-264d-4ad3-8fb8-937c4cda04a5'

    reSignFieldPosition = SignFieldPosition()
    reSignFieldPosition.positionX = 272.0
    reSignFieldPosition.positionY = 536.96594
    reSignFieldPosition.positionPage = 4

    reNormalSignFieldConfig.signFieldPosition = reSignFieldPosition
    representSignField.normalSignFieldConfig = reNormalSignFieldConfig

    # 签约对象赋值印章配置
    signer.signFields = [signField, representSignField]

    # 经办人信息配置
    personInfo = config['person']['li_zi_wen']
    orgSignerInfo = OrgSignerInfo(orgName='宿松县泰盈惠合新能源科技有限公司')
    orgSignerInfo.orgInfo = OrgInfo(orgIDCardNum='91340826MA8QT11W49', orgIDCardType='CRED_ORG_USCC')
    transactorInfo = TransactorInfo(psnAccount=personInfo['mobile'])
    transactorInfo.psnInfo = PsnInfo(psnName=personInfo['name'], 
                                     psnIDCardType='CRED_PSN_CH_IDCARD', 
                                     snIDCardNum=personInfo['idCard'])
    orgSignerInfo.transactorInfo = transactorInfo
    signer.orgSignerInfo = orgSignerInfo

    signFlowByFile.signers = [signer]

    # 请求报文
    reqDict = asdict(signFlowByFile)
    reqJson = json.dumps(deep_clean_null(reqDict))

    signFlowId = client.createByFile(req=reqJson)
    signUrl = client.getH5Url(psnAccount=personInfo['mobile'], thirdFlowId=signFlowId)
    signSql = f"update `xk-contract`.`sf_sign_flow` set third_flow_id = '{signFlowId}', sign_url = '{signUrl}'  where id = ?;"
    return fileId, signFlowId, signUrl, signSql


if __name__ == '__main__':
    fileId, signFlowId, signUrl, signSql = task(env='pro')
    print(fileId, ': ', signFlowId, ' -> ', signUrl, ' -> ', signSql)