from attr import define, field

@define
class CandleVo():

    # 开始时间，Unix时间戳的毫秒数格式
    ts: int = None

    # 结束时间，Unix时间戳的毫秒数格式
    cs: int = None

    # 开盘价格
    o: float = None

    # 最高价格
    h: float = None

    # 最低价格
    l: float = None

    # 收盘价格
    c: float = None

    # 交易量，以张为单位。
    # 如果是衍生品合约，数值为合约的张数。
    # 如果是币币/币币杠杆，数值为交易货币的数量。
    vol: float = None

    # 交易量，以币为单位
    # 如果是衍生品合约，数值为交易货币的数量。
    # 如果是币币/币币杠杆，数值为计价货币的数量。
    volCcy: float = None

    # 交易量，以计价货币为单位
    # 如 BTC-USDT和BTC-USDT-SWAP，单位均是USDT。
    # BTC-USD-SWAP单位是USD。
    volCcyQuote: float = None

    # K线状态
    # 0：K线未完结
    # 1：K线已完结
    confirm: str = None