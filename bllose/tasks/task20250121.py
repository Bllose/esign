from bllose.esign.Client import eqb_sign
from bllose.tasks.commons.GetDynamicTemplate import uploadOneFile
import urllib.request


def task_process(param: str, seal_id:str, recorderFile, env: str = 'test'):
    params = param.split(',')
    id = params[0]
    orderNo = params[1]
    oldFlowId = params[2]
    client = eqb_sign(env=env)

    response_json = client.downloadContractByFlowId(flowId=oldFlowId)
    if len(response_json) < 1:
        print(f'-- {param} 下载合同失败')
        return
    for response in response_json:
        fileName = response['fileName']
        if '租赁' in fileName:
            fileUrl = response['fileUrl']
            save_path = f'd:/temp/contractfiles/{response['fileId']}.pdf'
            urllib.request.urlretrieve(fileUrl, save_path)
    
    key_word = r'乙方（盖章）：'
    # abs_path = r'C:\Users\bllos\Downloads\光伏电站屋顶租赁协议（B端无共签人）20240604 (1).pdf'
    _, fileId = uploadOneFile(save_path, env=env)

    positionlist = client.keyword_position(fileId=fileId, keyword_list=[key_word])

    positions = positionlist['keywordPositions'][0]['positions']
    if positions is None or len(positions) < 1:
        print(f'-- {param} 文件找不到盖章位置')
        return ''

    req = {
    "docs": [
        {
        "fileId": fileId,
        "fileName": "光伏电站屋顶租赁协议"
        }
    ],
    "signFlowConfig": {
        "signFlowTitle": "光伏电站屋顶租赁协议",
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
        "signFields": [
            {
            "fileId": fileId,
            "normalSignFieldConfig": {
                "autoSign": True,
                "assignedSealId": seal_id,
                "signFieldStyle": 1,
                "signFieldPosition": {
                "positionPage": positions[0]['pageNum'],
                "positionX": positions[0]['coordinates'][0]['positionX'] + 300,
                "positionY": positions[0]['coordinates'][0]['positionY'] + 5
                }
            }
            }
        ]
        }
    ],
    "attachments": []
    }

    signFlowId = client.createByFile(req=req)
    # print(signFlowId)
    sql_update = f"update `xk-contract`.`sf_sign_flow` set third_flow_id='{signFlowId}', third_file_id = '{fileId}', sign_flow_phase='NEW' where id = {id};"
    recorderFile.write(sql_update + '\n')
    print(sql_update)

    return orderNo

# curl_http = r'http://localhost:30011/unify/signed/callback/eqb'
# curl_req = r'{"action":"SIGN_MISSON_COMPLETE","timestamp":1737425231096,"signFlowId":"'+ signFlowId + r'","signOrder":1,"operateTime":1737425230000,"signResult":2,"resultDescription":"签署完成","organization":{"orgId":"c763e5014ec248e18d2a35494cf85c09","orgName":"惠州TCL光伏科技有限公司"\}}'
# print(f"curl --location '{curl_http}'\\")
# print("--header 'Content-Type: application/json' \\")
# print(f"--data '{curl_req}'")


def process(creditId:str, origin_file_path:str, env='test'):
    """
    历史原因，一批租赁协议未能盖上项目公司印章，而是盖上了惠州TCL的章
    通过flowId将错误合同下载，然后在印章旁边补上指定项目公司的印章
    Args:
        creditId(str): 需要补充印章对应的项目公司社会信用代码
        origin_file_path(str): 保存着相关flowId的txt文档
    """

    client = eqb_sign(env=env)
    data = client.getOrganizationInfo(orgIdCard=creditId)
    orgId = data['orgId']

    sealId = None
    seals = client.fetchSealInfoByOrgId(orgId=orgId)
    for seal in seals:
        if seal['alias'] == '合同专用章':
            sealId = seal['sealId']
    if sealId is None:
        print(f'未获取到{creditId} 的合同专用章')
        return

    
    orderNoList = []
    try:
        with open(origin_file_path, 'r') as file, open(r'D:\temp\taskrecorder_gansuhemin.txt', 'w') as recorderFile:
            for line in file:
                param = line.strip()  # 使用 strip() 去除每行末尾的换行符
                orderNoList.append(task_process(param, recorderFile=recorderFile, seal_id=sealId, env=env))
    except FileNotFoundError as e:
        print(f"文件未找到，请检查文件路径是否正确。{e}")
    # param = r'145580451,GF240226100105000828,35e7e643d96c441ebf0558512ebd1053'
    print("=====================================================================")
    print("=====================================================================")
    print("\r\n")

    orderNoList = [str(item) for item in orderNoList if item]
    print(','.join(orderNoList))



if __name__ == '__main__':
    creditId = r'91621102MAE2EHGRX7'
    origin_file_path = r'D:\temp\originInfo.txt'
    process(creditId=creditId, origin_file_path=origin_file_path, env='pro')