from bllose.esign.Client import eqb_sign
import logging


def getTheNewSignUrl(name:str, mobile:str, creditId:str, flowId:str, env:str = 'test') -> str:
    """
    通过签署人、经办人的个人信息三要素和合同流水号，获取最新的签约地址
    Args:
        name(str): 三要素：人名
        mobile(str): 三要素：电话
        credit(str): 三要素：身份证号码
        flowId(str): 合同流水号
    Returns:
        shortUrl(str): 签约地址
    """

    client = eqb_sign(env)
    accountId = client.getAccountId(name=name, idNumber=creditId, mobile=mobile)
    shortUrl = client.getExeUrl(accountId=accountId, thirdFlowId=flowId)
    logging.info(flowId, mobile, name, accountId, ' -> ', shortUrl)
    return shortUrl

if __name__ == '__main__':
    originList = []
    for info in originList:
        infoArray = info.split(",")
        shortUrl = getTheNewSignUrl(infoArray[0], infoArray[2], infoArray[1], infoArray[3], env='pro')
        print(infoArray[4], ' -> ', shortUrl)