import os
from utils.lumcity import LumCity
from utils.core import logger
import datetime
import pandas as pd
from utils.telegram import Accounts
from aiohttp.client_exceptions import ContentTypeError
import asyncio


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    lumcity = LumCity(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    if await lumcity.login():
        logger.success(f"Thread {thread} | {account} | Login")
        while True:
            try:
                #data = await lumcity.get_data()
                miner_data = await lumcity.get_miner_data()
                miner_upgrades_data = await lumcity.get_upgrades_data()
                #storage = await lumcity.get_storage_data()

                #if not await lumcity.is_activated(data):
                #    wallet = await lumcity.create_wallet()
                #    logger.success(f"Thread {thread} | {account} | Create wallet: {wallet}")
                miner_balance = lumcity.get_miner_balance(miner_data)

                if miner_balance >= 0.001:
                    status, balance = await lumcity.collect()
                    if status == 201:
                        storage = float(await lumcity.get_storage_data())
                        logger.success(f"Thread {thread} | {account} | Collect GOLT! New balance: {storage}")
                    else:
                        logger.error(f"Thread {thread} | {account} | Can't collect GOLT! Response {status}")
                        continue
                else:
                    logger.info(f"Thread {thread} | {account} | Waiting for more GOLT to claim. remaining: {0.001 - miner_balance}")
                
                storage = float(await lumcity.get_storage_data())
                miner = lumcity.get_pickaxe_upgrade(miner_upgrades_data)
                pickaxe_price = float(miner.get("priceGolt"))

                if storage >= pickaxe_price:
                    status, storage = await lumcity.upgrade()
                    if status == 201:
                        logger.success(f"Thread {thread} | {account} | Upgraded miner! New balance: {storage}")
                    else:
                        logger.error(f"Thread {thread} | {account} | Can't upgrade! Response {status}: {storage}")
                else :
                    logger.info(f"Thread {thread} | {account} | Waiting for more GOLT to upgrade. remaining: {pickaxe_price - storage}")
                await asyncio.sleep(120)

            except ContentTypeError as e:
                logger.error(f"Thread {thread} | {account} | Error: {e}")
                await asyncio.sleep(120)

            #except Exception as e:
            #    print(e.args)
            #    logger.error(f"Thread {thread} | {account} | Error: {e}")
            #    await asyncio.sleep(5)

    else:
        await lumcity.logout()


async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(LumCity(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Registered', 'Phone number', 'Name', 'Balance', 'Referrals', 'Referral link', 'Wallet', 'Proxy (login:password@ip:port)']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")
