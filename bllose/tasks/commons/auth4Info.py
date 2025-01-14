from bllose.tasks.commons.ReqJsons.authorization4InfoUse import buildContractReq, buildFileByTemplateReq
from bllose.esign.Client import eqb_sign
from bllose.config.Config import bConfig
import json


@bConfig()
def get_callback_url(config, env:str = 'test') -> str:
    return config['eqb'][env]['callbackUrl']


def establish_contract_file(companyName: str, templateId: str, mobile: str,  env: str = 'test') -> tuple:
    """
    信息使用授权书
    Authorization Letter for Information Use
    """
    client = eqb_sign(env=env)
    
    reqDict = buildFileByTemplateReq(companyName=companyName, templateId=templateId)
    fileId, _ = client.createByDocTemplate(json.dumps(reqDict))
    personInfoDict = client.person_info_v3(psnAccount=mobile)
    

    contractReqDict = buildContractReq(fileId=fileId, noticeUrl=get_callback_url(env=env), signerAccountId=personInfoDict['psnId'])
    flowId = client.createFlowOneStep(bodyRaw=json.dumps(contractReqDict))
    shortUrl = client.getExeUrl(accountId=personInfoDict['psnId'], thirdFlowId=flowId)

    return flowId, shortUrl, fileId

if __name__ == '__main__':
    print(establish_contract_file(companyName='测试项目公司', templateId='7b21aced81474be2a6d61ad42a44a87a', mobile='18129705502'))