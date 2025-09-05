from mem import db, app
import aiohttp
import asyncio
import time
from models import log, service
from sqlalchemy.orm import sessionmaker
from config import timeout as timeout_


async def ping(client: aiohttp.ClientSession, s: service) -> int:
    match s.ping_method:
        case 0:
            r = await client.head(
                url=s.url,
                ssl=True if s.public_access else False,
                allow_redirects=True,
            )
        case 1:
            r = await client.get(
                url=s.url,
                ssl=True if s.public_access else False,
                allow_redirects=True,
            )
        case _:
            raise Exception("UNKNOWN PING METHOD")
    return r.status


async def check_service(client: aiohttp.ClientSession, s: service) -> log:
    try:
        # TODO: Use aiohttp latency timing rather than timing it manually
        before = time.perf_counter()
        status = await ping(client=client, s=s)
        after = time.perf_counter()
        if status == 200:
            return log(service_id=s.id, ping=int((after - before) * 1000))
        else:
            return log(service_id=s.id, ping=None)
    except aiohttp.ConnectionTimeoutError:
        return log(service_id=s.id, ping=None)
    except Exception:
        return log(service_id=s.id, ping=None)


def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run_coroutine_threadsafe(update_services(loop=loop), loop=loop)
    loop.run_forever()


async def update_services(loop: asyncio.AbstractEventLoop):
    print("Starting service updates...")
    # Create new session
    with app.app_context():
        WorkerSession = sessionmaker(bind=db.engine)
    timeout = aiohttp.client.ClientTimeout(total=timeout_ / 1000)
    client = aiohttp.ClientSession(timeout=timeout, auto_decompress=False)
    while True:
        session = WorkerSession()
        sleeptask = asyncio.create_task(asyncio.sleep(timeout_ / 1000 + 1))
        tasks = [
            check_service(client=client, s=s)
            for s in session.query(service).all()
        ]
        logs = await asyncio.gather(*tasks)
        await sleeptask
        try:
            session.add_all(logs)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
