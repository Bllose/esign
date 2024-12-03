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
    target = r'{"docs":[{"fileId":"ce98cb3a43764645ade46f6c1ba932e7","fileName":"极光平台用户授权书20241118.pdf"},{"fileId":"bce1672f1b8543479b93002fb894ebb2","fileName":"光伏电站屋顶租赁协议（B端无共签人）20241128_release.pdf"}],"flowInfo":{"autoArchive":true,"autoInitiate":true,"businessScene":"极光平台用户授权书&光伏电站屋顶租赁协议","flowConfigInfo":{"noticeDeveloperUrl":"https://aurora-test5-callback.tclpv.com/api/app/contract/unify/signed/callback/eqb","noticeType":"","redirectUrl":"","signPlatform":"1","willTypes":["FACE_TECENT_CLOUD_H5"],"personAvailableAuthTypes":null,"imageCode":null}},"signers":[{"platformSign":false,"signOrder":1,"signerAccount":{"signerAccountId":"3cfedbf8346b4a5691661935577d20a4","authorizedAccountId":null,"noticeType":null},"signfields":[{"autoExecute":false,"actorIndentityType":null,"fileId":"ce98cb3a43764645ade46f6c1ba932e7","sealType":"0","signDateBean":{"addSignTime":null,"fontSize":null,"format":null,"posPage":3,"posX":320.0,"posY":191.19905},"signType":null,"posBean":{"posPage":"3","posX":420.0,"posY":235.118},"width":null,"sealId":null,"signDateBeanType":2}],"thirdOrderNo":null},{"platformSign":false,"signOrder":1,"signerAccount":{"signerAccountId":"3cfedbf8346b4a5691661935577d20a4","authorizedAccountId":null,"noticeType":null},"signfields":[{"autoExecute":false,"actorIndentityType":null,"fileId":"bce1672f1b8543479b93002fb894ebb2","sealType":"0","signDateBean":{"addSignTime":null,"fontSize":null,"format":null,"posPage":5,"posX":134.12,"posY":81.95825},"signType":null,"posBean":{"posPage":"5","posX":224.12,"posY":183.63928},"width":null,"sealId":null,"signDateBeanType":2}],"thirdOrderNo":null},{"platformSign":false,"signOrder":1,"signerAccount":{"signerAccountId":"3cfedbf8346b4a5691661935577d20a4","authorizedAccountId":null,"noticeType":null},"signfields":[{"autoExecute":false,"actorIndentityType":null,"fileId":"bce1672f1b8543479b93002fb894ebb2","sealType":"0","signDateBean":null,"signType":null,"posBean":{"posPage":"6","posX":198.88,"posY":446.43927},"width":null,"sealId":null,"signDateBeanType":null}],"thirdOrderNo":null},{"platformSign":true,"signOrder":2,"signerAccount":null,"signfields":[{"autoExecute":true,"actorIndentityType":"2","fileId":"bce1672f1b8543479b93002fb894ebb2","sealType":null,"signDateBean":null,"signType":null,"posBean":{"posPage":"5","posX":214.12,"posY":137.79926},"width":null,"sealId":"1588ba4e-f2dd-4183-a22b-a0aa10103800","signDateBeanType":null}],"thirdOrderNo":null}],"atts":null}'
    sealNotMatchBodyCheck(target)