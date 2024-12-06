from bllose.esign.Client import eqb_sign
import logging


def contract_maker(fileId, fileName, orgName, orgIDCardNum, psnName, psnMobileNo):
    """
    制作一个需要指定企业“公章”和“法人章”签署的合同
    1、要求提供一个经办人的“电话”和“姓名”
    2、经办人收到签约短信，开始签约
    3、经办人点击签约跳转企业注册
    4、经办人填写真实法人信息，注册企业
    5、跳回合同页面，经办人点击签约
    6、跳转法人章授权页面
    7、经办人交由法人进行人脸识别，完成法人章授权
    8、经办人完成合同签署
    """
    req = {
    "docs": [
        {
        "fileId": fileId,
        "fileName": fileName
        }
    ],
    "signFlowConfig": {
        "signFlowTitle": fileName,
        "autoStart": True,
        "autoFinish": True,
        "notifyUrl": "https://aurora-dev1-callback.tclpv.com/api/app/contract/unify/signed/callback/eqb"
    },
    "signers": [
        {
        "signConfig": {
            "signOrder": 1
        },
        "signerType": 1,
        "orgSignerInfo": {
            "orgName": orgName,
            "orgInfo": {
            "orgIDCardNum": orgIDCardNum,
            "orgIDCardType": "CRED_ORG_USCC"
            },
            "transactorInfo": {
            "psnAccount": psnMobileNo,
            "psnInfo": {
                "psnName": psnName,
                "psnIDCardType": "CRED_PSN_CH_IDCARD",
                "sendSMSFlag": True,
                "psnMobileNo": psnMobileNo
            }
            }
        },
        "signFields": [
            {
            "fileId": fileId,
            "normalSignFieldConfig": {
                "autoSign": False,
                "signFieldStyle": 1,
                "signFieldPosition": {
                "positionPage": "1",
                "positionX": 425.935,
                "positionY": 368.91202
                }
            },
            "signDateConfig": {
                "showSignDate": 1,
                "signDatePositionX": 280.5806,
                "signDatePositionY": 274.7216
            }
            }
        ]
        },
        {
        "signConfig": {
            "signOrder": 1
        },
        "signerType": 2,
        "orgSignerInfo": {
            "orgName": orgName,
            "orgInfo": {
            "orgIDCardNum": orgIDCardNum,
            "orgIDCardType": "CRED_ORG_USCC"
            },
            "transactorInfo": {
            "psnAccount": psnMobileNo,
            "psnInfo": {
                "psnName": psnName,
                "psnIDCardType": "CRED_PSN_CH_IDCARD",
                "sendSMSFlag": True,
                "psnMobileNo": psnMobileNo
            }
            }
        },
        "signFields": [
            {
            "fileId": fileId,
            "normalSignFieldConfig": {
                "autoSign": False,
                "signFieldStyle": 1,
                "signFieldPosition": {
                "positionPage": "1",
                "positionX": 199.329636,
                "positionY": 311.4937
                }
            },
            "signDateConfig": {
                "showSignDate": 1,
                "signDatePositionX": 115.122,
                "signDatePositionY": 241.80328
            }
            }
        ]
        }
    ],
    "attachments": []
    }

    client = eqb_sign()
    signFlowId = client.createByFile(req=req)
    shortUrl = client.getH5Url(psnAccount=psnMobileNo, thirdFlowId=signFlowId)
    info = f'流水号:{signFlowId}\r\n签约地址:{shortUrl}\r\n经办人:{psnName}; 电话:{psnMobileNo}'
    logging.info(info)
    return signFlowId, shortUrl, psnName, psnMobileNo

if __name__ == '__main__':
    fileId = 'e0fc196c9c74467da413a21151d7c75c'
    fileName = '户用光伏业务经销协议（2025版）'
    orgName = 'esigntest惠州TCL光伏科技有限公司PAAX'
    orgIDCardNum = '910000821154730023'
    psnName = '史一荣'
    psnMobileNo = '18820234326'

    signFlowId, shortUrl, psnName, psnMobileNo = contract_maker(fileId, fileName, orgName, orgIDCardNum, psnName, psnMobileNo)
    logging.warning('%s %s %s %s', signFlowId, shortUrl, psnName, psnMobileNo)