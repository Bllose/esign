from bllose.config.Config import bConfig
from bllose.helper.TransTimeFormatter import timeFormatting
import logging
import bllose.okx.Account_api as Account
import bllose.okx.Funding_api as Funding
import bllose.okx.Market_api as Market
import bllose.okx.Public_api as Public
import bllose.okx.Trade_api as Trade
import bllose.okx.status_api as Status
import bllose.okx.subAccount_api as SubAccount
import bllose.okx.TradingData_api as TradingData
import bllose.okx.Broker_api as Broker
import bllose.okx.Convert_api as Convert
import bllose.okx.FDBroker_api as FDBroker
import bllose.okx.Rfq_api as Rfq
import bllose.okx.TradingBot_api as TradingBot
import bllose.okx.Finance_api as Finance
import bllose.okx.Copytrading_api as Copytrading
import bllose.okx.Recurring_api as Recurring
import bllose.okx.SprdApi_api as Sprd

class blloseHttpOKE():
    @bConfig()
    def __init__(self, config):

        self.api_key = config['okx.Bllose.apiKey']
        self.secret_key = config['okx.Bllose.secretKey']
        self.passphrase = config['okx.Bllose.passphrase']
        self.flag = config['okx.Bllose.flag']

        self.accountAPI = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        # 交易数据查询
        self.tradingDataAPI = TradingData.TradingDataAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.fundingAPI = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.convertAPI = Convert.ConvertAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.marketAPI = Market.MarketAPI(self.api_key, self.secret_key, self.passphrase, True, self.flag)
        self.publicAPI = Public.PublicAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.tradeAPI = Trade.TradeAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.sprdAPI = Sprd.SprdAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        # 子账户API subAccount
        self.subAccountAPI = SubAccount.SubAccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.brokerAPI = Broker.BrokerAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.fdBrokerAPI = FDBroker.FDBrokerAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        self.rfqAPI = Rfq.RfqAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        # 网格交易
        self.tradingBot = TradingBot.TradingBotAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        # 金融产品 Finance API
        self.finance = Finance.FinanceAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        # 跟单
        self.copytrading = Copytrading.CopytradingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        # 定投
        self.recurring = Recurring.RecurringAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        # 系统状态API(仅适用于实盘) system status
        self.status = Status.StatusAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

    def get_account_instruments(self, instType:str, instId:str = '') -> list:
        """
        <h3>获取当前账户可交易产品的信息列表</h3>
        Args:
            instType(str): 产品类型
                - SPOT: 币币
                - MARGIN: 币币杠杆
                - SWAP: 永续合约
                - FUTURES: 交割合约
                - OPTION: 期权
            instId(str): 产品ID
                - BTC-USDT
        Returns:
            instrument_list(list): 账户信息
                - instId(str): 产品ID
                - baseCcy(str): 交易货币币种 
                - quoteCcy(str): 交易货币币种
                - listTime(str): 上线时间
                - expTime(str): 产品下线时间
        """
        result = self.accountAPI.get_account_instruments(instType = instType, uly = '', instFamily = '', instId = instId)
        if result['code'] == '0':
            return result['data']
        else:
            logging.warning(f'获取账号信息失败，返回报文:{result}')
            return []

    # @timeFormatting()    
    def get_account(self, ccy:str) -> dict:
        """
        <h3>查看账户余额</h3>
        <p>获取交易账户中资金余额信息。</p>
        Args:
            ccy(str): 币种，比如BTC，多币种查询（20个），逗号分割
        Returns:
            accountInfo(dict): 账户信息
                - uTime(int/str): 查询时间
                - totalEq(str): 账户余额（权益/美金）
                - details(list): 详情
                    > ccy(str): 币种
                    > eq(str):  余额（权益/当前币种)
                    > cashBal(str): 余额
                    > uTime(str): 余额币种更新时间
                    > disEq(str): 余额（币种折算美金）
                    > availBal(str): 可用余额（当前币种）
                    > frozenBal(str): 币种占用金额（已挂单等）
                    > ordFrozen(str): 挂单冻结数(现货模式/现货和合约模式/跨币种保证金模式)
                    > accAvgPx(str): 现货累计成本价 单位 USD
                    > totalPnl(str): 现货累计收益，单位 USD
                    > spotUpl(str): 现货未实现收益，单位 USD
                    > spotUplRatio(str): 现货未实现收益率
        """
        result = self.accountAPI.get_account(ccy=ccy)
        return result
    
    def get_support_coin(self) -> list:
        """
        <h1>获取所支持的币种类型列表</h1>
        Returns:
            coin_list(list): 支持的币种列表。币种简称PS:BTC;ETH;XCH...
        """
        response = self.tradingDataAPI.get_support_coin()
        if response['code'] == '0':
            return response['data']['contract']
        
    def get_taker_volume(self, ccy='BTC', instType='SPOT', 
                         begin:str = '', end:str = '', period:str = '') -> list:
        """
        <h1>获取主动买入/卖出情况</h1>
        <p>获取taker主动买入和卖出的交易量</p>
        Args:
            ccy(str): 币种
            instType(str): 产品类型 SP: SPOT 币币
            begin(str): 开始时间，Unix时间戳的毫秒数格式，如 1597026383085
            end(str): 结束时间，Unix时间戳的毫秒数格式，如 1597026383011
            period(str): 时间粒度，默认值5m。支持[5m/1H/1D]
        Returns:
            list(list): 交易记录列表
            - ts(str): 数据产生时间
            - sellVol(str): 卖出量
            - buyVol(str): 买入量
        """
        response = self.tradingDataAPI.get_taker_volume(
            ccy=ccy, instType=instType)
        if response['code'] == '0':
            return response['data']
        
    def get_taker_volume_contract(self, instId = 'BTC-USDT', period = '', 
                                  unit='', end='', begin='', limit = '10'):
        """
        ```
        from datetime import datetime, timedelta
        current_time = datetime.now()
        ten_minutes_age = current_time - timedelta(minutes=10)
        timestamp_millisecond_begin = int(ten_minutes_age.timestamp() * 1000)

        timestamp_millisecond_now = int(current_time.timestamp() * 1000)
        print(blloseHttpOKE().get_taker_volume_contract(
            begin=timestamp_millisecond_begin, end=timestamp_millisecond_now, 
            period='6H', unit=1))
        ```
        """
        response = self.tradingDataAPI.get_taker_volume_contract(instId, period, 
                                  unit, end, begin, limit)
        return response

if __name__ == '__main__':
    account_info = blloseHttpOKE().get_account(ccy='ETH')
    print(account_info)

