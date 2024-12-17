import json
from bllose.esign.Client import eqb_sign
import logging

def sealNotMatchBodyCheck(target:str, env:str='test'):
    """
    排查报错原因
    {"code":1435002,"message":"参数错误: 印章和签署主体不匹配"}
    """
    client = eqb_sign(env = env)
    
    targetJson = json.loads(target)
    signers: list = targetJson['signers']
    docs: list = targetJson['docs']
    docNames = {doc['fileId']:doc['fileName'] for doc in docs}

    sealInfoDict = {}
    index = 0
    for signer in signers:
        index += 1
        if 'orgSignerInfo' in signer:
            # 社会统一信用代码
            companyName = signer['orgSignerInfo']['orgName']
            orgIDCardNum = signer['orgSignerInfo']['orgInfo']['orgIDCardNum']
            if orgIDCardNum in sealInfoDict:
                seals = sealInfoDict[orgIDCardNum]['seals']
            else:
                response = client.getOrganizationInfo(orgIDCardNum)
                orgId = response['orgId']
                response = client.getSealsInfo(orgId)
                seals = response['seals']
                sealInfoDict["orgIDCardNum"] = {"companyName": companyName, "seals": seals}
            legalSealIdList = [seal['sealId'] for seal in seals]

            illegalSealIds = []
            signFields = signer['signFields']
            for signField in signFields:
                if 'normalSignFieldConfig' not in signField:
                    continue
                assignedSealId = signField['normalSignFieldConfig']['assignedSealId']
                if assignedSealId not in legalSealIdList:
                    fileId = signField['fileId']
                    illegalSealIds.append(docNames[fileId] + ' -> ' + assignedSealId)
            if len(illegalSealIds) > 0:
                print(companyName, '下使用的印章ID不合法', illegalSealIds)
        else:
            fieldIndex = 0
            for curSignfield in signer['signfields']:
                fieldIndex += 1
                sealId = curSignfield['sealId']
                if sealId is None or len(sealId) < 1:
                    logging.error(f'第{index}个signer下的第{fieldIndex}个signField没有签署公司相关信息')
                else:
                    logging.error(f'第{index}个signer下的第{fieldIndex}个signField没有签署公司基本信息，只有sealId:{sealId}')


if __name__ == '__main__':
    target = r'{"eventType":null,"eventExplain":null,"eventTip":null,"groupBy":null,"eventType_1":null,"eventExplain_1":null,"eventTip_1":null,"groupBy_1":null,"exceptionType":null,"check":null,"channel":3,"templateId":null,"contractFileObjectIdKey":"PC002_image","sceneCode":"PCI001","sendType":{"APP签约":"开始签约","短信签约":"发送短信"},"qhParams":null,"version":"v10","isSign":true,"controlSignNodes":null,"isReuse":null,"reuseValidDays":null,"isCosignerContract":null,"isOffline":null,"imageCode":"PC002_image","offlineControlStatesMap":null,"async":null,"signTasks":[{"sceneCode":"OBO001","imageCode":"OBO001_image","version":"v1"}],"isMergeCode":null,"itemLocationOnPage":null,"objectNo":"GF241214143630002323","signMethod":"1","pageCurrentOrderStatus":"待预审提交"}'
    sealNotMatchBodyCheck(target)