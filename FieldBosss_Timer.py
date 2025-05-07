import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import pytz
import os
import sys


# Lấy token và channel ID từ biến môi trường
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID_STR = os.getenv('DISCORD_CHANNEL_ID')  # Thay bằng ID kênh Discord

if not TOKEN or not CHANNEL_ID_STR:
    print("❌ Lỗi: Thiếu biến môi trường. Kiểm tra DISCORD_BOT_TOKEN và DISCORD_CHANNEL_ID.")
    sys.exit(1)

CHANNEL_ID = int(CHANNEL_ID_STR)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Boss xuất hiện lúc các giờ cụ thể
boss_schedule = {
    "Bluemen": ["00:30", "12:30"],
    "Betalanse": ["02:30", "14:30"],
    "Cryo": ["04:30", "16:30"],
    "Sporelex": ["06:30", "18:30"],
    "Toxspore": ["08:30", "20:30"],
    "Bristol": ["10:30", "22:30"],
    "Veilian": ["00:30", "12:30"],
    "Arque": ["02:30", "14:30"],
    "Rootrus": ["04:30", "16:30"],
    "Sapphire Blade": ["06:30", "18:30"],
    "Coralisk": ["08:30", "20:30"],
    "Breeze": ["10:30", "22:30"]
}

notified_times = set()

@bot.event
async def on_ready():
    print(f'{bot.user} đã khởi động!')
    check_boss_times.start()

@bot.command()
async def hello(ctx):
    await ctx.send("Xin chào, tôi là Bot Của Little Fish!")

@tasks.loop(minutes=1)
async def check_boss_times():
    now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    channel = bot.get_channel(CHANNEL_ID)

    for boss, times in boss_schedule.items():
        for time_str in times:
            boss_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day,
                tzinfo=pytz.timezone('Asia/Ho_Chi_Minh')
            )

            # Nếu giờ boss hôm nay đã qua (ví dụ đang là 1AM mà boss là 00:30)
            if boss_time < now:
                boss_time += timedelta(days=1)

            warning_time = boss_time - timedelta(minutes=5)
            if now.strftime("%H:%M") == warning_time.strftime("%H:%M"):
                unique_key = (boss, boss_time.strftime("%Y-%m-%d %H:%M"))
                if unique_key not in notified_times:
                    await channel.send(f"⚠️ Field Boss **{boss}** sẽ xuất hiện lúc {boss_time.strftime('%H:%M')}! Chuẩn bị nào!")
                    notified_times.add(unique_key)

    # Reset danh sách đã báo mỗi ngày lúc 00:00
    if now.strftime("%H:%M") == "00:00":
        notified_times.clear()

bot.run(TOKEN)
