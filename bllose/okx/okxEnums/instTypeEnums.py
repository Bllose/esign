from enum import Enum

class instrumentType(Enum):
    SPOT = 'SPOT', '币币交易', '即期交易'
    MARGIN = 'MARGIN', '杠杆交易', '保证金交易'
    SWAP = 'SWAP', '永续合约', '一种衍生品，没有到期日，通常用于追踪某个标的资产的价格'
    FUTURES = 'FUTURES', '期货合约', '约定在未来某个特定时间以特定价格买入或卖出一定数量标的资产的协议'
    OPTION = 'OPTION', '期权', '给予持有者在特定时间内以特定价格买入（看涨期权）或卖出（看跌期权）某种资产的权利，但不是义务'

    def __init__(self, code, desc, msg):
        self._code = code
        self.desc = desc
        self.msg = msg

    @property
    def code(self):
        return self._code


if __name__ == '__main__':
    print(instrumentType.SPOT.code)
    print(instrumentType.SPOT.desc)
    print(instrumentType.SPOT.msg)
