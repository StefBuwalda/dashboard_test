from mem import services, service, db, app
import httpx
import asyncio
import time
from models import log
from sqlalchemy.orm import sessionmaker


async def check_service(client: httpx.AsyncClient, s: service) -> log:
    try:
        before = time.perf_counter()
        match s.ping_type:
            case 0:
                r = await client.head(
                    url=s.url,
                    follow_redirects=True,
                    timeout=4,
                )
            case 1:
                r = await client.get(
                    url=s.url,
                    follow_redirects=True,
                    timeout=4,
                    headers={"Host": "plex.ihatemen.uk"},
                )
            case _:
                raise httpx.HTTPError("Unknown ping type")
        after = time.perf_counter()
        s.set_error(None)
        s.set_online(r.status_code == 200)
        s.set_status(r.status_code)
        s.set_ping(int((after - before) * 1000))
    except httpx.ConnectTimeout:
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
    async with (
        httpx.AsyncClient() as public_client,
        httpx.AsyncClient(verify=False) as local_client,
    ):
        while True:
            session = WorkerSession()
            tasks = [
                check_service(public_client if s.public else local_client, s)
                for s in services
            ]
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
