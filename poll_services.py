from mem import services, service, db, app
import aiohttp
import asyncio
import time
from models import log
from sqlalchemy.orm import sessionmaker


async def check_service(client: aiohttp.ClientSession, s: service) -> log:
    try:
        timeout = aiohttp.client.ClientTimeout(total=4)
        before = time.perf_counter()
        match s.ping_type:
            case 0:
                r = await client.head(
                    url=s.url,
                    ssl=True if s.public else False,
                    allow_redirects=True,
                    timeout=timeout,
                )
            case 1:
                r = await client.get(
                    url=s.url,
                    ssl=True if s.public else False,
                    allow_redirects=True,
                    timeout=timeout,
                )
            case _:
                raise Exception("UNKNOWN PING TYPE")
        after = time.perf_counter()
        s.set_error(None)
        s.set_online(r.status == 200)
        s.set_status(r.status)
        s.set_ping(int((after - before) * 1000))
    except aiohttp.ConnectionTimeoutError:
        s.set_error("Connection Timeout")
        s.set_online(False)
        s.set_status(None)
        s.set_ping(None)
    except Exception as e:
        print(type(e))
        s.set_error(str(e))
        s.set_online(False)
        s.set_status(None)
        s.set_ping(None)
    return log()


def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run_coroutine_threadsafe(update_services(loop=loop), loop=loop)
    loop.run_forever()


async def sleepTask():
    await asyncio.sleep(5)
    return log()


async def update_services(loop: asyncio.AbstractEventLoop):
    print("Starting service updates...")
    with app.app_context():
        WorkerSession = sessionmaker(bind=db.engine)
    client = aiohttp.ClientSession()
    while True:
        session = WorkerSession()
        tasks = [check_service(client=client, s=s) for s in services]
        tasks.append(sleepTask())
        logs = await asyncio.gather(*tasks)
        logs = logs[:-1]
        try:
            session.add_all(logs)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
