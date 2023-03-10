#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
import json
import logging
import os
import re

from dotenv import load_dotenv
from persiantools import digits
from persiantools.jdatetime import JalaliDate
from telegram import __version__ as TG_VER

from main import update_clients_info
from utils import convert_size

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(
        "برای دیدن باقی مانده حجم VPN خود میتوانید دستور /usage را به همراه UUID خود ارسال نمایید."
        "\n"
        "مثال:\n"
        "/usage f745f1-972c-4b4y3-cefa-569e0bfc1b16")


def get_usage_by_uuid(uuid: str):
    f = open('sample.json')
    data = json.load(f)
    info = data.get(uuid, None)
    return info


def create_msg_by_info(info: dict):
    enable = "فعال" if info['enable'] else "غیرفعال"
    email = info['email']
    up = get_amount(info, 'up')
    down = get_amount(info, 'down')
    total = get_amount(info, 'total')
    if info['expiryTime']:
        expiry_time = int(str(info['expiryTime'])[:-3])
        expiry_time = JalaliDate.fromtimestamp(expiry_time)
        expiry_time = expiry_time.strftime("%Y/%m/%d")
    else:
        expiry_time = "نامحدود"

    msg = f"""
    💡 وضعیت: {enable}
    📧 ایمیل: {email}
    🔼 آپلود↑: {up} 
    🔽 دانلود↓: {down} 
    🔄 مجموع حجم: {total} 
    📅 تاریخ انقضا: {expiry_time}
    """
    msg = digits.en_to_fa(msg)
    return msg


def get_amount(info, key):
    byte_amount = info[key]
    converted = convert_size(byte_amount)
    fa_converted = digits.en_to_fa(converted)
    return fa_converted.replace(".", "/")


async def usage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the user traffic usage."""
    message = update.message.text
    uuid = re.match("/usage (.*)", message).groups()[0]
    info = get_usage_by_uuid(uuid)
    if info:
        msg = create_msg_by_info(info)
    else:
        msg = "متاسفانه! هیچ کاربری با UUID درخواستی یافت نشد."
    await update.message.reply_text(msg)


def main() -> None:
    """Start the bot."""

    # Create the Application and pass it your bot's token.
    TOKEN = os.environ["BOT_TOKEN"]
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("usage", usage))

    application.job_queue.run_repeating(
        update_clients_info,
        interval=int(os.environ["UPDATE_INTERVAL"]),
        first=0.0
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
