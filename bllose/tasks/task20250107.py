from bllose.esign.Client import eqb_sign
from bllose.config.Config import bConfig

def make_flowid(zulin_fileId: str, gonghuo_fileId:str,
                personName: str, personId: str, personMobile: str,
                companyName: str, companyId: str, companySealId: str,
                tclSealId:str = "66cfa62a-8833-41c2-91fb-11d997abf77d", env: str = 'test') -> tuple:
    request = {
        "attachments": [],
        "signFlowConfig": {
            "autoFinish": True,
            "autoStart": True,
            "notifyUrl": "https://callback1-pv.tcl.com/api/app/contract/unify/signed/callback/eqb",
            "signFlowTitle": "起租-租赁合同-附件二"
        },
        "signers": [
            {
            "signConfig": {
                "signOrder": 1
            },
            "signFields": [
                {
                "signFieldType": 1,
                "remarkSignFieldConfig": {
                    "signFieldPosition": {
                    "positionX": 350,
                    "positionY": 393,
                    "positionPage": "3"
                    },
                    "autoSign": False,
                    "remarkContent": "2024年12月20日",
                    "movableSignField": True,
                    "inputType": 2
                },
                "fileId": zulin_fileId
                }
            ],
            "signerType": 0,
            "psnSignerInfo": {
                "psnAccount": personMobile,
                "psnInfo": {
                "psnName": personName,
                "psnIDCardNum": personId,
                "psnIDCardType": "CRED_PSN_CH_IDCARD"
                }
            }
            },
            {
            "signConfig": {
                "signOrder": 1
            },
            "orgSignerInfo": {
                "orgName": companyName,
                "transactorInfo": {
                "psnAccount": personMobile,
                "psnInfo": {
                    "sendSMSFlag": False,
                    "psnIDCardType": "CRED_PSN_CH_IDCARD",
                    "psnIDCardNum": personId,
                    "psnName": personName
                }
                },
                "orgInfo": {
                "orgIDCardType": "CRED_ORG_USCC",
                "orgIDCardNum": companyId
                }
            },
            "signFields": [
                {
                "normalSignFieldConfig": {
                    "signFieldPosition": {
                    "positionX": 380,
                    "positionY": 420.91202,
                    "positionPage": "3"
                    },
                    "autoSign": False,
                    "signFieldStyle": 1,
                    "assignedSealId": companySealId
                },
                "fileId": zulin_fileId
                },
                {
                "normalSignFieldConfig": {
                    "signFieldPosition": {
                    "positionX": 380,
                    "positionY": 250,
                    "positionPage": "1"
                    },
                    "autoSign": False,
                    "signFieldStyle": 1,
                    "assignedSealId": companySealId
                },
                "fileId": gonghuo_fileId
                }
            ],
            "signerType": 1
            },
            {
            "signConfig": {
                "signOrder": 1
            },
            "orgSignerInfo": {
                "orgName": "惠州TCL光伏科技有限公司",
                "transactorInfo": {
                "psnAccount": personMobile,
                "psnInfo": {
                    "sendSMSFlag": False,
                    "psnIDCardType": "CRED_PSN_CH_IDCARD",
                    "psnIDCardNum": personId,
                    "psnName": personName
                }
                },
                "orgInfo": {
                "orgIDCardType": "CRED_ORG_USCC",
                "orgIDCardNum": "91441303MA7FTL1J0D"
                }
            },
            "signFields": [
                {
                "normalSignFieldConfig": {
                    "signFieldPosition": {
                    "positionX": 290,
                    "positionY": 380,
                    "positionPage": "1"
                    },
                    "autoSign": False,
                    "signFieldStyle": 1,
                    "assignedSealId": tclSealId
                },
                "fileId": gonghuo_fileId
                }
            ],
            "signerType": 1
            }
        ],
        "docs": [
            {
            "fileName": "起租-租赁合同-附件二",
            "fileId": zulin_fileId
            },
            {
            "fileName": "起租-供货合同-附件二",
            "fileId": gonghuo_fileId
            }
        ]
        }

    client = eqb_sign(env=env)
    signFlowId = client.createByFile(req=request)
    shortUrl = client.getH5Url(signFlowId, psnAccount=personMobile)

    return signFlowId, shortUrl

@bConfig()
def task_entity(config):
    zulin_fileId = '830f9c3a6e5d4956b7c0eaf3ad28b574'
    gonghuo_fileId = '11353865f3db4e988e9d0dd20e4b5bc6'
    personName = config['person']['me']['name']
    personId = config['person']['me']['idCard']
    personMobile = config['person']['me']['mobile']
    companyName = '九江泰盈惠合新能源科技有限公司'
    companyId = '91360430MACL8M6Q2B'
    companySealId = 'b51b9a3d-1f6b-4212-9738-c25d1f2faed5'
    tclSealId = '66cfa62a-8833-41c2-91fb-11d997abf77d'
    signFlowId, shortUrl = make_flowid(zulin_fileId=zulin_fileId, gonghuo_fileId = gonghuo_fileId,
                                       personName=personName, personId=personId, personMobile=personMobile, 
                                        companyName=companyName, companyId=companyId, companySealId=companySealId,
                                        tclSealId=tclSealId)
    print(signFlowId, shortUrl)


if __name__ == '__main__':
    task_entity()