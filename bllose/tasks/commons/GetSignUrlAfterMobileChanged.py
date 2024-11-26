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
    # 尝试使用三要素创建账户并返回账户ID，若存在则返回已经存在的账户ID
    accountId = client.getAccountId(name=name, idNumber=creditId, mobile=mobile)
    # 对目标账户ID更新用户三要素信息
    updatedData = client.updateAccountsByid(accountId=accountId, name=name, mobile=mobile)
    accountId = updatedData['accountId']
    # 通过最新的账户id结合签约流水号获取到签约地址
    shortUrl = client.getExeUrl(accountId=accountId, thirdFlowId=flowId)
    logging.info(flowId, mobile, name, accountId, ' -> ', shortUrl)
    return shortUrl

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    originList = ['胡树高,511525198504300915,19533118964,70eaa740d53146ce842944ae86ce4905,GF231226111243000343']
    for info in originList:
        infoArray = info.split(",")
        shortUrl = getTheNewSignUrl(infoArray[0], infoArray[2], infoArray[1], infoArray[3], env='pro')
        print(infoArray[4], ' -> ', shortUrl)