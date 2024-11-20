import json
from bllose.esign.Client import eqb_sign

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
    for signer in signers:
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


if __name__ == '__main__':
    target = r'{"signFlowConfig":{"autoFinish":true,"autoStart":true,"notifyUrl":"https://aurora-test1-callback.tclpv.com/api/app/contract/unify/signed/callback/eqb","signFlowTitle":"电费质押附件（建设期二期放款）、买卖附表附件一&二（建设期二期）、运维附表附件一（建设期二期）、租赁附表附件二（建设期二期放款）","noticeConfig":{"noticeTypes":"1"}},"signers":[{"signConfig":{"signOrder":1},"orgSignerInfo":{"orgName":"TCL光伏科技（深圳）有限公司","transactorInfo":{"psnAccount":"***","psnInfo":{"psnIDCardNum":"***","sendSMSFlag":true,"psnIDCardType":"CRED_PSN_CH_IDCARD","psnName":"***"}},"orgInfo":{"orgIDCardType":"CRED_ORG_USCC","orgIDCardNum":"91440300MA5H9NX89R"}},"signFields":[{"normalSignFieldConfig":{"signFieldPosition":{"positionX":184.88664,"positionY":327.9231,"positionPage":"1"},"autoSign":false,"signFieldStyle":1,"assignedSealId":"896501ce-5c75-455d-8bec-7a7e70b2e2e9"},"fileId":"d3e1fa248c5549378ac231122d711232"}],"signerType":1},{"signConfig":{"signOrder":1},"orgSignerInfo":{"orgName":"九江泰盈惠合新能源科技有限公司","transactorInfo":{"psnAccount":"***","psnInfo":{"psnIDCardNum":"***","sendSMSFlag":true,"psnIDCardType":"CRED_PSN_CH_IDCARD","psnName":"***"}},"orgInfo":{"orgIDCardType":"CRED_ORG_USCC","orgIDCardNum":"91360430MACL8M6Q2B"}},"signFields":[{"normalSignFieldConfig":{"signFieldPosition":{"positionX":346.38763,"positionY":483.792,"positionPage":"5"},"autoSign":false,"signFieldStyle":1,"assignedSealId":"b51b9a3d-1f6b-4212-9738-c25d1f2faed5"},"fileId":"9b4cda4935304141b8845d3b8970c251"}],"signerType":1},{"signConfig":{"signOrder":1},"orgSignerInfo":{"orgName":"TCL光伏科技（深圳）有限公司","transactorInfo":{"psnAccount":"***","psnInfo":{"psnIDCardNum":"***","sendSMSFlag":true,"psnIDCardType":"CRED_PSN_CH_IDCARD","psnName":"***"}},"orgInfo":{"orgIDCardType":"CRED_ORG_USCC","orgIDCardNum":"91440300MA5H9NX89R"}},"signFields":[{"normalSignFieldConfig":{"signFieldPosition":{"positionX":316.02643,"positionY":572.96716,"positionPage":"3"},"autoSign":false,"signFieldStyle":1,"assignedSealId":"896501ce-5c75-455d-8bec-7a7e70b2e2e9"},"fileId":"9b4cda4935304141b8845d3b8970c251"},{"normalSignFieldConfig":{"signFieldPosition":{"positionX":514,"positionY":426.09058,"positionPage":"5"},"autoSign":false,"signFieldStyle":1,"assignedSealId":"896501ce-5c75-455d-8bec-7a7e70b2e2e9"},"fileId":"9b4cda4935304141b8845d3b8970c251"}],"signerType":1},{"signConfig":{"signOrder":1},"orgSignerInfo":{"orgName":"九江泰盈惠合新能源科技有限公司","transactorInfo":{"psnAccount":"***","psnInfo":{"psnIDCardNum":"***","sendSMSFlag":true,"psnIDCardType":"CRED_PSN_CH_IDCARD","psnName":"***"}},"orgInfo":{"orgIDCardType":"CRED_ORG_USCC","orgIDCardNum":"91360430MACL8M6Q2B"}},"signFields":[{"normalSignFieldConfig":{"signFieldPosition":{"positionX":196.87656,"positionY":761,"positionPage":"2"},"autoSign":false,"signFieldStyle":1,"assignedSealId":"b51b9a3d-1f6b-4212-9738-c25d1f2faed5"},"fileId":"7ac5365592b54965bdad8412c85d22cf"}],"signerType":1},{"signConfig":{"signOrder":1},"orgSignerInfo":{"orgName":"TCL光伏科技（深圳）有限公司","transactorInfo":{"psnAccount":"***","psnInfo":{"psnIDCardNum":"***","sendSMSFlag":true,"psnIDCardType":"CRED_PSN_CH_IDCARD","psnName":"***"}},"orgInfo":{"orgIDCardType":"CRED_ORG_USCC","orgIDCardNum":"91440300MA5H9NX89R"}},"signFields":[{"normalSignFieldConfig":{"signFieldPosition":{"positionX":196.87656,"positionY":634.4155,"positionPage":"2"},"autoSign":false,"signFieldStyle":1,"assignedSealId":"2a208878-a1db-48c7-b18a-a96fa7ae6767"},"fileId":"7ac5365592b54965bdad8412c85d22cf"}],"signerType":1},{"signConfig":{"signOrder":1},"orgSignerInfo":{"orgName":"九江泰盈惠合新能源科技有限公司","transactorInfo":{"psnAccount":"***","psnInfo":{"psnIDCardNum":"***","sendSMSFlag":true,"psnIDCardType":"CRED_PSN_CH_IDCARD","psnName":"***"}},"orgInfo":{"orgIDCardType":"CRED_ORG_USCC","orgIDCardNum":"91360430MACL8M6Q2B"}},"signFields":[{"normalSignFieldConfig":{"signFieldPosition":{"positionX":200.29556,"positionY":606.6892,"positionPage":"6"},"autoSign":false,"signFieldStyle":1,"assignedSealId":"b51b9a3d-1f6b-4212-9738-c25d1f2faed5"},"fileId":"8dfcc1c7f1d148c2b4753f9c28fbf82f"}],"signerType":1}],"docs":[{"fileName":"电费质押附件（建设期二期放款）","fileId":"d3e1fa248c5549378ac231122d711232"},{"fileName":"买卖附表附件一&二（建设期二期）","fileId":"9b4cda4935304141b8845d3b8970c251"},{"fileName":"运维附表附件一（建设期二期）","fileId":"7ac5365592b54965bdad8412c85d22cf"},{"fileName":"租赁附表附件二（建设期二期放款）","fileId":"8dfcc1c7f1d148c2b4753f9c28fbf82f"}]}'
    sealNotMatchBodyCheck(target)