import os
import jwt
import json
import asyncio
import asyncpg
from aiohttp import web, ClientSession
from dotenv import load_dotenv
from settings import IMEI_CHECK_URL, SERVICEID, SECRET_KEY,\
DB_USER, DB_PASSWORD, DB_NAME, DB_HOST
from aiohttp_jwt import JWTMiddleware, check_permissions


class CheckImeiView(web.View):

    async def get_deviceId(self):

        try:
            data = await self.request.json()
            deviceId = str(data['imei'])
        except json.JSONDecodeError:
            return web.json_response(
                status=400,
                text="Invalid request format")
        except KeyError:
            return web.json_response(
                status=400,
                text='The request must contain the "imei" parameter')

        if len(deviceId) != 15:
            return web.json_response(
                status=400,
                text= f"imei is {len(deviceId)} characters long(imei must be 15 characters long)")

        if not deviceId.isdigit():
            return web.json_response(
                status=400,
                text= f"imei must consist of digits")

        return deviceId

    async def verify_access(self) -> bool:
        pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST
        )
        async with pool.acquire() as con:
            try:
                result = await con.fetchrow('SELECT * FROM users WHERE telegram_id = $1', self.request['user'])
                return bool(result)
            except Exception:
                return False

    @check_permissions()
    async def post(self):
        if not self.verify_access:
            return web.json_response(
                status=403,
                text='access denied'
                )
        deviceId = await self.get_deviceId()
        if not isinstance(deviceId, str):
            return deviceId

        token = os.getenv('TOKEN')
        if not token:
            raise ValueError("Token not found in environment variables.")
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            "deviceId": deviceId,
            "serviceId": SERVICEID}
                
        async with ClientSession() as session:

            async with session.post(url=IMEI_CHECK_URL + '/v1/checks', headers=headers,data=data) as resp:
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
    app.middlewares.append(
        JWTMiddleware(
            secret_or_pub_key=SECRET_KEY,
            request_property='user',
            algorithms=['HS256']
    ))
    app.add_routes(
        [
            web.post('/api/check-imei',CheckImeiView)
        ])

if __name__ == '__main__':
    app = asyncio.run(get_app())
    web.run_app(app)