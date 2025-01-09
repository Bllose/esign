from bllose.esign.Client import eqb_sign
from bllose.config.Config import bConfig

def make_flowid(zulin_fileId: str, gonghuo_fileId:str,
                personName: str, personId: str, personMobile: str,
                companyName: str, companyId: str, companySealId: str,
                tclSealId:str = "66cfa62a-8833-41c2-91fb-11d997abf77d", env: str = 'test') -> tuple:
    
    remarkContent = "2024年12月20日"
    tclCompanyName = "惠州TCL光伏科技有限公司"
    tclCompanyId = "91441303MA7FTL1J0D"

    if companyId == '91360313MAD299JU2J':
        remarkContent = "2024年12月27日"
    
    if tclSealId == '402e6c69-2c3e-4b44-888c-95cba7e3901d':
        tclCompanyName = 'TCL光伏科技（深圳）有限公司'
        tclCompanyId = '91440300MA5H9NX89R'

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
                    "remarkContent": remarkContent,
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
                    "positionX": 290,
                    "positionY": 380,
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
                "orgName": tclCompanyName,
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
                "orgIDCardNum": tclCompanyId
                }
            },
            "signFields": [
                {
                "normalSignFieldConfig": {
                    "signFieldPosition": {
                    "positionX": 380,
                    "positionY": 250,
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
    from bllose.helper.excelHelper import fetch_rows

    rows = fetch_rows(r'C:\Users\bllos\Desktop\太平石化合同重新签约生产解决\太平石化任务薄.xlsx')
    person = 'liang_chen'
    personName = config['person'][person]['name']
    personId = config['person'][person]['idCard']
    personMobile = config['person'][person]['mobile']
    for row in rows:
        batch_no = row[0]
        zulin_fileId = row[1]
        gonghuo_fileId = row[2]
        if zulin_fileId is None or len(zulin_fileId) < 1 or gonghuo_fileId is None or len(gonghuo_fileId) < 1:
            continue
        companyName = row[3]
        companyId = row[4]
        companySealId = row[5]
        tclSealId = row[6]
        tpsh007_id = row[7]
        tpsh008_id = row[8]

        signFlowId, shortUrl = make_flowid(zulin_fileId=zulin_fileId, gonghuo_fileId = gonghuo_fileId,
                                        personName=personName, personId=personId, personMobile=personMobile, 
                                            companyName=companyName, companyId=companyId, companySealId=companySealId,
                                            tclSealId=tclSealId, env='pro')
        print(f'{batch_no}:{companyName} -> {shortUrl}')
        print(f"update `xk-contract`.`sf_sign_flow` set third_flow_id = '{signFlowId}', sign_flow_phase = 'NEW', sign_url = '{shortUrl}' where id = '{tpsh007_id}';")
        print(f"update `xk-contract`.`sf_sign_flow` set third_flow_id = '{signFlowId}', sign_flow_phase = 'NEW', sign_url = '{shortUrl}' where id = '{tpsh008_id}';")


if __name__ == '__main__':
    task_entity()