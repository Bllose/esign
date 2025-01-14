from typing import Optional
import logging

def buildFileByTemplateReq(companyName:str, templateId: str) -> Optional[dict]:
    """
    通过合同模版与合同要素创建合同文件请求报文
    """
    return {
            "components": [{
                'componentKey': 'companyName1',
                'componentValue': companyName
                }
            ],
            "fileName": "极光平台用户授权书.pdf",
            "docTemplateId": templateId
            }

def buildContractReq(fileId: str, noticeUrl: str, signerAccountId: str) -> Optional[dict]:
    """
    e签宝一步发起签署请求报文

    Args:
        fileId(str): 文件id
        noticeUrl(str): 回调地址
        signerAccountId(str): 用户id
    Returns:
        dict: 请求报文
    """
    return {
                "docs": [
                    {
                    "fileId": fileId,
                    "fileName": "极光平台用户授权书.pdf"
                    }
                ],
                "flowInfo": {
                    "autoArchive": True,
                    "autoInitiate": True,
                    "businessScene": "极光平台用户授权书",
                    "flowConfigInfo": {
                    "noticeDeveloperUrl": noticeUrl,
                    "noticeType": "",
                    "redirectUrl": "",
                    "signPlatform": "1",
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
                            "posPage": 3,
                            "posX": 420.0,
                            "posY": 173.0
                        },
                        "posBean": {
                            "posPage": "3",
                            "posX": 460.0,
                            "posY": 218.0
                        },
                        "signDateBeanType": 2
                        }
                    ]
                    }
                ]
            }