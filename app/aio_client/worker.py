from sqlalchemy.orm import sessionmaker
from config import timeout as timeout_
import aiohttp
import asyncio
import time
from types import SimpleNamespace
from app import db, app
from app.models import service
from .client import ping_service
import threading

stop_event = threading.Event()


def start_worker():
    try:
        # Creates new event loop in new thread
        loop = asyncio.new_event_loop()

        # Creates new task on new loop
        loop.create_task(update_services())

        # Schedule loop to run forever
        loop.run_forever()
    except Exception as e:
        print("Worker thread exception:", e)
        stop_event.set()


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


async def update_services():
    try:
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
                ping_service(client=client, s=s)
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
    except Exception as e:
        print("Worker thread exception:", e)
        stop_event.set()
