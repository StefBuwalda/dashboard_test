import aiohttp
from app.models import service, log
from types import SimpleNamespace
from typing import Optional


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


async def ping_service(client: aiohttp.ClientSession, s: service) -> log:
    try:
        ctx = SimpleNamespace()
        status = await ping(client=client, s=s, ctx=ctx)

        if status == 200:
            return log(service_id=s.id, ping=int(ctx.duration_ms))
        else:
            return log(service_id=s.id, ping=None)
    except aiohttp.ConnectionTimeoutError:
        return log(service_id=s.id, ping=None, timeout=True)
    except Exception as e:
        print(e)
        return log(service_id=s.id, ping=None)
