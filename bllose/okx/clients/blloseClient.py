from bllose.config.Config import class_config
from bllose.config.Config import bConfig
import asyncio
from websocket_example import subscribe_without_login

class blloseOKE():
    @bConfig()
    def __init__(self, config):
        self.api_key = config['okx.Bllose.apiKey']
        self.secret_key = config['okx.Bllose.secretKey']
        self.passphrase = config['okx.Bllose.passphrase']
        self.flag = config['okx.Bllose.flag']

    async def spread_depth_data(self, channels):
        if self.flag == 0:
            url = "wss://ws.okx.com:8443/ws/v5/business"
        else:
            url = "wss://wspap.okx.com:8443/ws/v5/business"
        # AWS实盘地址
        # wss://wsaws.okx.com:8443/ws/v5/business

        await subscribe_without_login(url, channels)

async def main():
    channels = [{"channel":"sprd-bbo-tbt","sprdId":"BTC-USDT_BTC-USDT-SWAP"},
                {"channel":"sprd-books-l2-tbt","sprdId":"BTC-USDT_BTC-USDT-SWAP"},
                {"channel":"sprd-books5","sprdId":"BTC-USDT_BTC-USDT-SWAP"}]

    tasks = [
        blloseOKE().spread_depth_data(channels)
    ]

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())

    bllose = blloseOKE()
    