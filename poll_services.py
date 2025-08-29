from mem import services, service
import httpx
import urllib3
import asyncio

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def check_service(client: httpx.AsyncClient, s: service):
    try:
        r = await client.head(
            url=s.url,
            follow_redirects=True,
            timeout=1,
        )
        s.set_error(None)
        s.set_online(r.status_code == 200)
        s.set_status(r.status_code)
    except httpx.HTTPError as e:
        s.set_error(str(e))
        s.set_online(False)
        s.set_status(None)


def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run_coroutine_threadsafe(update_services(loop=loop), loop=loop)
    loop.run_forever()


async def update_services(loop: asyncio.AbstractEventLoop):
    print("Starting service updates...")
    async with httpx.AsyncClient() as public_client, httpx.AsyncClient(
        verify=False
    ) as local_client:
        while True:
            tasks = [
                check_service(public_client if s.public else local_client, s)
                for s in services
            ]
            await asyncio.gather(*tasks)
            await asyncio.sleep(2)
