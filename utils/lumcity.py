import random
import time
from datetime import datetime
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
import asyncio
from urllib.parse import unquote, quote, parse_qs
from data import config
import aiohttp
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector
import json


class LumCity:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY_TYPES['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY_TYPES['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def stats(self):
        await self.login()
        data = await self.get_data()

        registered = '✅' if data.get('activated') else '❌'
        balance = data.get('balance')
        wallet = data.get('walletAddress')

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace(f'{config.PROXY_TYPES["REQUESTS"]}://', "") if self.proxy is not None else '-'
        return [registered, phone_number, name, str(balance), wallet, proxy]

    async def upgrade(self):
        resp = await self.session.post('https://back.lumcity.app/miner-upgrades/buy', headers=self.session.headers, json = {"type":"pickaxe","tokenId":1})
        resp_json = await resp.json()
        print(resp_json)

        return resp.status, resp_json.get('pickaxeLevel') if resp_json.get("success") else await resp.text()

    async def collect(self):
        resp = await self.session.post('https://back.lumcity.app/miner/', json={})
        return resp.status, float((await resp.json()).get('storage')) if resp.status == 201 else await resp.text()

    @staticmethod
    def get_storage(data):
        #print(f"data storage: {data['storage']}")
        if data.get('storage') is None:
            return 0.0
        
        return float(data.get('storage'))

    @staticmethod
    def get_miner_balance(data):
        #print(f"data: {data}")
        if data.get('balance') is None:
            return 0.0
        
        return float(data.get("balance"))

    @staticmethod
    def get_pickaxe_upgrade(data):
        #print(f"data: {data}")
        if data.get('pickaxeUpgrade') is None:
            return 0.0
        
        return data["pickaxeUpgrade"]
        #return self.from_nano(data.get('balance'))

    async def get_data(self):
        resp = await self.session.get('https://back.lumcity.app/users/telegram', json={}, headers=self.session.headers)
        #print(f'get user data: {await resp.json()}')
        return (await resp.json()).get('info')

    async def get_miner_data(self):
        resp = await self.session.get('https://back.lumcity.app/miner/storage/balance/', json={}, headers=self.session.headers)
        #print(f'get balance data: {await resp.json()}')
        return await resp.json()

    async def get_storage_data(self):
        resp = await self.session.get('https://back.lumcity.app/balance/all', json={}, headers=self.session.headers)
        #print(f'get balance data: {await resp.json()}')
        data = await resp.json()
        if data.get("balances") is None or len(data.get("balances")) < 2:
            return 0.0
        
        return (await resp.json()).get("balances")[1].get("amount")

    async def get_upgrades_data(self):
        resp = await self.session.get('https://back.lumcity.app/miner-upgrades/all-upgrades', json={}, headers=self.session.headers)
        #print(f'get all upgrades: {await resp.json()}')
        return await resp.json()


    async def create_wallet(self):
        resp = await self.session.post('https://back.lumcity.app/users/set-address', json={})
        return (await resp.json()).get('address')

    @staticmethod
    async def is_activated(data):
        return data.get('is_active')

    async def logout(self):
        await self.session.close()

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        query = await self.get_tg_web_data()
        if query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None

        async def custom_quote(value):
            return ''.join(
                c if c.isalnum() or c in '-._~ ' else quote(c) if c != '"' else c for c in value)

        async def transform_input_string(input_string):
            parts = input_string.split('&')
            transformed_parts = []

            for part in parts:
                if part.startswith('user='):
                    key, value = part.split('=', 1)
                    encoded_value = await custom_quote(value)
                    transformed_parts.append(f'{key}={encoded_value}')
                else:
                    transformed_parts.append(part)

            transformed_string = '&'.join(transformed_parts)
            return transformed_string

        output_string = await transform_input_string(query)

        resp = await self.session.get(f"https://back.lumcity.app/jwt/token?" + output_string)
        resp_json = await resp.json()
        self.session.headers['Authorization'] = "Bearer " + resp_json.get("accessToken")
        return True

    async def get_tg_web_data(self):
        try:
            refs = ["WJ9YR9QB", "ZYMPE6LJ","HG47U3XF", "TX3CAKTB", "BY66VLAI", 'ZV3B4D4L', 'L79FT2J9']
            await self.client.connect()

            await asyncio.sleep(2)
            web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('LumCity_bot'),
                bot=await self.client.resolve_peer('LumCity_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://lumcity.app/app/'
            ))
            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            return query

        except:
            print(Exception)
