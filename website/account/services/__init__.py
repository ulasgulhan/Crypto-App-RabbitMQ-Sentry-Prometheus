from ..models import APIEndpoints, CryptoMarketAPICredentials
from asgiref.sync import sync_to_async
import json



# yapılacaklar servis api endpointleri dbye kaydedilsin dbdn gelsin auth header required false true gelsin



class CryptoMarketPlace():
    def __init__(self):
        self.timestamp = None
        self.db_model = CryptoMarketAPICredentials
        self.domain = None
        self.api_model = APIEndpoints
        

    def generate_headers(self, url=None, params=None, method=None):
        return None
    

    @sync_to_async
    def get_api_endpoints(self, crypto_market, method=None, endpoint_name=None):
        if endpoint_name:
            return list(APIEndpoints.objects.filter(crypto_market=crypto_market, method=method, endpoint_name=endpoint_name))
        else:
            return list(APIEndpoints.objects.filter(crypto_market=crypto_market, method=method))



    
    async def fetcher(self, session, auth_header_required=False, url=None, method=None, params=None):
        if params:
            if auth_header_required and method == 'POST':
                headers = await self.generate_headers(url=url, params=params, method=method)
            elif auth_header_required:
                headers = await self.generate_headers(params=params, method=method)
            else:
                headers = None
            
            if method == 'POST':
                async with session.request(method, self.domain + url, headers=headers, json=params) as response:
                    return await response.json()
            else:
                async with session.request(method, self.domain + url + '?' + params, headers=headers) as response:
                    return await response.json()
        else:
            if auth_header_required:
                headers = await self.generate_headers(url=url, method=method)
            else:
                headers = None
            async with session.request(method, self.domain + url, headers=headers) as response:
                return await response.json()
    


