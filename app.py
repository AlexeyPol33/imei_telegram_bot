import os
import jwt
import json
import asyncio
import psycopg2
import base64
from psycopg2 import sql
from io import BytesIO
from aiohttp import web, ClientSession
from functools import wraps
from dotenv import load_dotenv
from settings import IMEI_CHECK_URL, SERVICEID, SECRET_KEY,\
DB_USER, DB_PASSWORD, DB_NAME, DB_HOST


@web.middleware
async def jwt_middleware(request, handler):
    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return web.json_response({"error": "Missing or invalid token"}, status=401)

    token = auth_header.split("Bearer ")[1]

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request["user"] = decoded_token
    except jwt.ExpiredSignatureError:
        return web.json_response({"error": "Token expired"}, status=401)
    except jwt.InvalidTokenError:
        return web.json_response({"error": "Invalid token"}, status=401)

    return await handler(request)


def require_auth(handler):
    @wraps(handler)
    async def wrapped(obj, *args, **kwargs):
        request = obj.request
        if "user" not in request:
            return web.json_response(status=401,text='Unauthorized')
        connection = psycopg2.connect(
            dbname="whitelist",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        telegram_id = request['user']['sub']
        query = sql.SQL("SELECT * FROM users WHERE telegram_id = %s")
        cursor.execute(query, (telegram_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            return await handler(obj, *args, **kwargs)
        else:
            return web.json_response(status=403,text='Access denial')
    return wrapped

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

    @require_auth
    async def post(self):
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
            async with session.get(url=text['properties']['image']) as img:
                   text['properties']['image'] = base64.b64encode(BytesIO(await img.read()).getvalue()).decode('utf-8')
        try:
            return web.json_response(text['properties'])
        except KeyError:
            return web.json_response(
                status=404,
                text="device not faund")


async def get_app():
    app = web.Application()
    app.middlewares.append(jwt_middleware)
    app.add_routes(
        [
            web.post('/api/check-imei',CheckImeiView)
        ])
    return app

if __name__ == '__main__':
    app = asyncio.run(get_app())
    web.run_app(app)