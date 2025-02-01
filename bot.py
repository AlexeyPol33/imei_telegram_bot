import json
import jwt
import base64
from io import BytesIO
from datetime import datetime, timedelta
from aiohttp import ClientSession
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, \
CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from abc import ABC, abstractmethod
from settings import TELEGRAM_BOT_TOKEN, IMEI_API, SECRET_KEY


commands = []


def generate_jwt(user_id):
    return jwt.encode(
        payload={
            'sub': str(user_id),
            'exp': datetime.now() + timedelta(minutes=20)},
        key=SECRET_KEY,
        algorithm='HS256')


class BotCore(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, token):
        self.application = ApplicationBuilder().token(token).build()
        [self.application.add_handler(c) for c in commands]

    def run(self):
        self.application.run_polling()


class RegisterCommand:

    def __init__(self, handler: CommandHandler, command: str = None) -> None:
        self.command = command
        self.handler = handler

    def __call__(self, obj):

        if self.command is None:
            try:
                self.command = obj.filter
            except Exception:
                commands.append(self.handler(obj.execute))
                return obj
        commands.append(self.handler(self.command, obj.execute))
        return obj


class Command(ABC):
    @staticmethod
    @abstractmethod
    async def execute(update: Update, context: ContextTypes) -> None: ...


@RegisterCommand(CommandHandler, 'start')
class Start(Command):

    @staticmethod
    async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE):

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=' '.join(('Every mobile phone, GSM modem or device with built-in',
                           'phone/modem has a unique 15-digit IMEI number. Based on',
                           'this number you can check some information about the device,',
                           'such as brand or model. Enter the IMEI number in the chat,',
                           'after the /IMEI command.')))


@RegisterCommand(CommandHandler, 'IMEI')
class IMEI(Command):

    @staticmethod
    async def get_imei(imei: str):

        if len(imei) != 15:
            raise ValueError(f'IMEI is {len(imei)} characters long (imei must be 15 characters long)')
        if not imei.isdigit():
            raise ValueError("imei must consist of digits")
        return imei

    @staticmethod
    async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE):

        user_id = update.effective_user.id
        try:
            imei = await IMEI.get_imei(context.args[0])
        except ValueError as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=str(e.args[0]))
            return
        except IndexError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='No value after /IMEI.'
            )
            return

        async with ClientSession() as session:

            headers = {'Authorization': f'Bearer {generate_jwt(user_id)}'}
            data = json.dumps({"imei": imei})
            async with session.post(f'{IMEI_API}/api/check-imei', headers=headers, data=data) as resp:
                resp_status = resp.status
                if resp_status != 200:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=await resp.text())

                resp_data = await resp.json()
        image = resp_data.pop('image', None)
        if image:
            image = base64.b64decode(image)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=BytesIO(image))
        if resp_status == 200:
            for key, value in resp_data.items():
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'{key} - {value}')


if __name__ == '__main__':
    BotCore(TELEGRAM_BOT_TOKEN).run()
