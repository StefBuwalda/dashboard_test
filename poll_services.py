from mem import db, app
import aiohttp
import asyncio
import time
from models import log, service
from sqlalchemy.orm import sessionmaker


async def check_service(client: aiohttp.ClientSession, s: service) -> log:
    try:
        timeout = aiohttp.client.ClientTimeout(total=4)
        before = time.perf_counter()
        match s.ping_method:
            case 0:
                r = await client.head(
                    url=s.url,
                    ssl=True if s.public_access else False,
                    allow_redirects=True,
                    timeout=timeout,
                )
            case 1:
                r = await client.get(
                    url=s.url,
                    ssl=True if s.public_access else False,
                    allow_redirects=True,
                    timeout=timeout,
                )
            case _:
                raise Exception("UNKNOWN PING TYPE")
        after = time.perf_counter()
        if r.status == 200:
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
    with app.app_context():
        WorkerSession = sessionmaker(bind=db.engine)
    client = aiohttp.ClientSession()
    while True:
        session = WorkerSession()
        sleeptask = asyncio.create_task(asyncio.sleep(5))
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
