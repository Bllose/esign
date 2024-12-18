from bllose.esign.Client import eqb_sign
import logging
import json


def get_request(fileId:str, signerAccountId:str, sealId:str, env:str) -> dict:
    """
    无共签人租赁协议签约发起请求
    Args:
        fileId(str): 签约合同文件ID
        signerAccountId(str): 签约人id，农户id，出租人id
        sealId(str): 印章id(公章)
        env(str): e签宝的签署环境 test, pro
    Returns:
        request(dict): 发起签约请求报文
    """
    if env == 'pro':
        noticeDeveloperUrl = 'https://callback1-pv.tcl.com/api/app/contract/unify/signed/callback/eqb'
    else:
        noticeDeveloperUrl = 'https://aurora-test3-callback.tclpv.com/api/app/contract/unify/signed/callback/eqb'
    req = {
    "docs": [
        {
        "fileId": fileId,
        "fileName": "光伏电站屋顶租赁协议（B端无共签人）20241128_release.pdf"
        }
    ],
    "flowInfo": {
        "autoArchive": True,
        "autoInitiate": True,
        "businessScene": "极光平台用户授权书&光伏电站屋顶租赁协议",
        "flowConfigInfo": {
            "noticeDeveloperUrl": noticeDeveloperUrl,
            "redirectUrl": "",
            "signPlatform": "1",
            "noticeType": "",
            "willTypes": [
                "FACE_TECENT_CLOUD_H5"
            ]
        }
    },
    "signers": [
        {
        "platformSign": False,
        "signOrder": 1,
        "signerAccount": {
            "signerAccountId": signerAccountId
        },
        "signfields": [
            {
            "autoExecute": False,
            "fileId": fileId,
            "sealType": "0",
            "signDateBean": {
                "posPage": 5,
                "posX": 134.12,
                "posY": 81.95825
            },
            "posBean": {
                "posPage": "5",
                "posX": 194.12,
                "posY": 173.63928
            },
            "signDateBeanType": 2
            }
        ]
        },
        {
        "platformSign": False,
        "signOrder": 1,
        "signerAccount": {
            "signerAccountId": signerAccountId
        },
        "signfields": [
            {
            "autoExecute": False,
            "fileId": fileId,
            "sealType": "0",
            "posBean": {
                "posPage": "6",
                "posX": 158.88,
                "posY": 436.43927
            }
            }
        ]
        },
        {
        "platformSign": True,
        "signOrder": 2,
        "signfields": [
            {
            "autoExecute": True,
            "actorIndentityType": "2",
            "fileId": fileId,
            "posBean": {
                "posPage": "5",
                "posX": 214.12,
                "posY": 127.799255
            },
            "sealId": sealId
            }
        ]
        }
    ]
    }
    return req

def getAccountId(creditId:str, env:str='test') -> str:
    """
    获取自然人的e签宝 id号 v3接口
    Args:
        creditId(str): 身份证号码
        env(str): 调用环境
    Returns:
        psnId(str): e签宝ID
    """
    client = eqb_sign(env=env)
    result_v3 = client.person_info_v3(psnIDCardNum = creditId)
    return result_v3['psnId']

def getOfficialSeal(orgIdCard:str, env:str = 'test') -> str:
    """
    获取项目公司的公章id，e签宝的sealId
    Args:
        orgIdCard(str): 社会统一信用代码
    """
    client = eqb_sign(env=env)
    response_json = client.getOrganizationInfo(orgIdCard)
    orgId = response_json['orgId']
    seals_json = client.getSealsInfo(orgId=orgId)
    for seal in seals_json['seals']:
        alias = seal['alias']
        if alias == '公章':
            return seal['sealId']
    return None


def getSignUrl(orgIdCard:str, creditId:str, fileId:str, env:str = 'test') -> tuple:
    """
    通过文件创建一个签约合同
    Args:
        orgIdCard(str): 参与签约企业方的“社会统一信用代码”
        creditId(str): 参与签署的“农户，租户，自然人”的身份证号码
        fileId(str): 需要签署的合同文件id(e签宝 id)
        env(str): 签约环境
    Returns:
        result(tuple): 合同相关信息
            - signFlowId(str): 签约流水ID （e签宝 签约流水号）
            - fileId(str): 合同签署文件id
            - shortUrl(str): 签约短链接
    """
    seal = getOfficialSeal(orgIdCard=orgIdCard)
    if seal is None or len(seal) < 1:
        logging.error(f'社会统一信用代码{orgIdCard}无法从e签宝获取公章信息!')
        return '', '', ''
    
    psnId = getAccountId(creditId=creditId)
    if psnId is None or len(psnId) < 1:
        logging.error(f'身份证{creditId}无法从e签宝获取个人id!')
        return '', '', ''
     
    req = get_request(fileId=fileId, signerAccountId=psnId, sealId=seal, env=env)
    client = eqb_sign(env=env)
    bodyRaw = json.dumps(req)
    signFlowId = client.createFlowOneStep(bodyRaw=bodyRaw)
    if signFlowId is None or len(signFlowId) < 1:
        logging.error(f'创建签约流程失败 fileId:{fileId}')
        return '', '', ''

    shortUrl = client.getH5Url(thirdFlowId=signFlowId, psnId=psnId)
    return signFlowId, fileId, shortUrl

if __name__=='__main__':
    # 'c414a2d4-cf7a-4c19-bc13-818714c08fbb'
    seal = getOfficialSeal(orgIdCard='91360430MACL8M6Q2B')
    # print(seal)

    psnId = getAccountId(creditId='431026198801130018')
    # print(psnId)

    fileId = 'be0aafbccc88470ca8ccf043647e1f8a'
    req = get_request(fileId=fileId, signerAccountId=psnId, sealId=seal, env='test')
    # print(req)

    client = eqb_sign()
    bodyRaw = json.dumps(req)
    signFlowId = client.createFlowOneStep(bodyRaw=bodyRaw)

    shortUrl = client.getH5Url(thirdFlowId=signFlowId, psnId=psnId)
    print(signFlowId, fileId, shortUrl)
