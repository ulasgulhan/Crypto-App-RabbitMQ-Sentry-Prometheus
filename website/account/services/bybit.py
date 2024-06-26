import asyncio
import aiohttp
from . import CryptoMarketPlace
from ..utilities import bybit_signature, decode
from asgiref.sync import sync_to_async
from pybit.unified_trading import HTTP


class Bybit(CryptoMarketPlace):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.domain = 'https://api.bybit.com'
        self.apikey = None
        self.secret_key= None
        self.session = HTTP(testnet=False)
    

    
    async def generate_headers(self, url=None, params=None, method=None):
        api_info = await sync_to_async(self.db_model.objects.get)(user=self.user, crypto_market=2)
        api_key = decode(api_info.api_key)
        time = self.session.get_server_time()
        message = str(time['time']) + api_key + str(5000) + str(params)

        headers = {
            'X-BAPI-TIMESTAMP': str(time['time']),
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-RECV-WINDOW': str(5000),
            'X-BAPI-SIGN': bybit_signature(decode(api_info.secret_key), message),
            'Content-Type': 'application/json'
        }

        return headers
    
    async def get_api_data(self):
        context = {}
        async with aiohttp.ClientSession() as session:

            api_endpoints = await self.get_api_endpoints(crypto_market=2, method='GET')

            tasks = []
            for endpoint in api_endpoints:
                tasks.append(self.fetcher(session, endpoint.auth_required, url=endpoint.endpoint_url, method=endpoint.method, params=endpoint.endpoint_params))

            results = await asyncio.gather(*tasks)

            for i, endpoint in enumerate(api_endpoints):
                context[endpoint.endpoint_name] = results[i]

        return context
    
    async def get_coin_data(self, symbol):
        context = {}
        async with aiohttp.ClientSession() as session:
                        
            api_endpoints = await self.get_api_endpoints(crypto_market=2, method='GET')

            
            for endpoint in api_endpoints:
                if endpoint.endpoint_name == 'bybit_coins':
                    context['coin'] = await self.fetcher(session, endpoint.auth_required, url=endpoint.endpoint_url, method=endpoint.method, params=endpoint.endpoint_params + f'&symbol={symbol}')  

              
        return context
    
    async def place_order(self, symbol, side, size, price):
        api_info = await sync_to_async(self.db_model.objects.get)(user=self.user, crypto_market=2)
        api_key = decode(api_info.api_key)
        secret_key = decode(api_info.secret_key)
        context = {}
        async with aiohttp.ClientSession() as session:

            session = HTTP(
                testnet=False,
                api_key=api_key,
                api_secret=secret_key,
            )
            api_endpoints = await self.get_api_endpoints(crypto_market=2, method='POST', endpoint_name='bybit_place_order')

            results = session.place_order(
                category="spot",
                symbol=str(symbol),
                side=str(side),
                orderType="Limit",
                qty=str(size),
                price=str(price),
            )

            for i, endpoint in enumerate(api_endpoints):
                context[endpoint.endpoint_name] = results

        return context
