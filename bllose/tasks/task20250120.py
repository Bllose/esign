from bllose.esign.Client import eqb_sign
from openpyxl import load_workbook

client = eqb_sign(env='pro')

workbook = load_workbook('d:/temp/contract_check.xlsx')
sheet = workbook['Sheet2']
for row in sheet.iter_rows(min_row=2, values_only=False):
    # 获取 A 列和 B 列的值
    orderNo = row[0].value
    flowId = row[1].value
    response_json = client.getSignFlowDetail(signFlowId=flowId)

    signers = response_json['data']['signers']
    for signer in signers:
        signerType = signer['signerType']
        if signerType == 1:
            signFields = signer['signFields']
            for signField in signFields:
                normalSignFieldConfig = signField['normalSignFieldConfig']
                sealId = normalSignFieldConfig['sealId']
                sealOwnerId = normalSignFieldConfig['sealOwnerId']
                row[2].value = sealOwnerId
                row[3].value = sealId
                print(f'{orderNo}\t{flowId}\t{sealId}\t{sealOwnerId}')
workbook.save('output.xlsx')


    