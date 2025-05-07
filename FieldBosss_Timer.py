import discord
import os
import sys
from datetime import datetime, timedelta
import pytz
import asyncio

# Lấy token và channel ID từ biến môi trường
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID_STR = os.getenv('DISCORD_CHANNEL_ID')

if not TOKEN or not CHANNEL_ID_STR:
    print("❌ Lỗi: Thiếu biến môi trường.")
    sys.exit(1)

CHANNEL_ID = int(CHANNEL_ID_STR)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# Lịch boss
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

async def check_boss():
    now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    channel = bot.get_channel(CHANNEL_ID)
    warning_sent = False

    for boss, times in boss_schedule.items():
        for time_str in times:
            boss_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day,
                tzinfo=pytz.timezone('Asia/Ho_Chi_Minh')
            )
            if boss_time < now:
                boss_time += timedelta(days=1)
            
            warning_time = boss_time - timedelta(minutes=5)

            if abs((now - warning_time).total_seconds()) <= 30:
                await channel.send(f"⚠️ Field Boss **{boss}** sẽ xuất hiện lúc {boss_time.strftime('%H:%M')}! Chuẩn bị nào!")
                print(f"Đã gửi cảnh báo cho {boss}")
                warning_sent = True

    if not warning_sent:
        print("✅ Không có boss nào cần cảnh báo lúc này.")

@bot.event
async def on_ready():
    print(f"🤖 Bot đã khởi động lúc {datetime.now()}")
    await check_boss()
    await bot.close()  # Tự thoát để tiết kiệm tài nguyên Railway

bot.run(TOKEN)
