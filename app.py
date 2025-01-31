import os
import json
import asyncio
from aiohttp import web, ClientSession
from dotenv import load_dotenv


load_dotenv()
BASEURL = "https://api.imeicheck.net"
SERVICEID = 12

class CheckImeiView(web.View):

    async def get_deviceId(self):
        try:
            data = await self.request.json()
            deviceId = data['imei']
        except json.JSONDecodeError:
            return web.json_response(
                status=400,
                text="Invalid request format")
        except KeyError:
            return web.json_response(
                status=400,
                text="The request must contain the ‘imei’ parameter")
        if len(deviceId) != 15:
            return web.json_response(
                status=400,
                text= f"imei is {len(deviceId)} characters long(imei must be 15 characters long)")
        if not deviceId.isdigit():
            return web.json_response(
                status=400,
                text= f"imei must consist of digits")

        return deviceId

    async def post(self):

        deviceId = await self.get_deviceId()
        if isinstance(deviceId, str):
            pass
        else:
            return deviceId

        token = os.getenv('TOKEN')
        if not token:
            raise ValueError("Token not found in environment variables.")
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            "deviceId": deviceId,
            "serviceId": SERVICEID}
                
        async with ClientSession() as session:

            async with session.post(url=BASEURL + '/v1/checks', headers=headers,data=data) as resp:
                status = resp.status
                text = await resp.json()

        try:
            return web.json_response(text['properties'])
        except KeyError:
            return web.json_response(
                status=404,
                text="device not faund")



async def get_app():
    app = web.Application()
    app.add_routes(
        [
            web.post('/api/check-imei',CheckImeiView)
        ])
    
    return app

if __name__ == '__main__':
    app = asyncio.run(get_app())
    web.run_app(app)