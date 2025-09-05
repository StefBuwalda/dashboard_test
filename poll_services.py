from mem import db, app
import aiohttp
import asyncio
import time
from models import log, service
from sqlalchemy.orm import sessionmaker
from config import timeout as timeout_
from typing import Optional
from types import SimpleNamespace


async def ping(
    client: aiohttp.ClientSession,
    s: service,
    ctx: Optional[SimpleNamespace] = None,
) -> int:
    ctx = ctx or SimpleNamespace()
    match s.ping_method:
        case 0:
            r = await client.head(
                url=s.url,
                ssl=True if s.public_access else False,
                allow_redirects=True,
                trace_request_ctx=ctx,  # type: ignore
            )
        case 1:
            r = await client.get(
                url=s.url,
                ssl=True if s.public_access else False,
                allow_redirects=True,
                trace_request_ctx=ctx,  # type: ignore
            )
        case _:
            raise Exception("UNKNOWN PING METHOD")
    return r.status


async def check_service(client: aiohttp.ClientSession, s: service) -> log:
    try:
        ctx = SimpleNamespace()
        status = await ping(client=client, s=s, ctx=ctx)
        print(status)
        print(vars(ctx))
        if status == 200:
            print("test")
            print(ctx.duration_ms)
            return log(service_id=s.id, ping=int(ctx.duration_ms))
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


def setup_client() -> aiohttp.ClientSession:
    timeout = aiohttp.client.ClientTimeout(total=timeout_ / 1000)
    # Each request will get its own context
    trace_config = aiohttp.TraceConfig()

    async def on_start(
        session: aiohttp.ClientSession,
        context: SimpleNamespace,
        params: aiohttp.TraceRequestStartParams,
    ):
        ctx = context.trace_request_ctx
        ctx.start = time.perf_counter()  # store per-request

    async def on_end(
        session: aiohttp.ClientSession,
        context: SimpleNamespace,
        params: aiohttp.TraceRequestEndParams,
    ):
        ctx = context.trace_request_ctx
        ctx.end = time.perf_counter()
        ctx.duration_ms = int((ctx.end - ctx.start) * 1000)

    trace_config.on_request_start.append(on_start)
    trace_config.on_request_end.append(on_end)
    client = aiohttp.ClientSession(
        timeout=timeout, auto_decompress=False, trace_configs=[trace_config]
    )
    return client


async def update_services(loop: asyncio.AbstractEventLoop):
    print("Starting service updates...")
    # Create new session
    with app.app_context():
        WorkerSession = sessionmaker(bind=db.engine)

    client = setup_client()

    # Actual update loop
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
