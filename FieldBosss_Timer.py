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
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(tz)
    channel = bot.get_channel(CHANNEL_ID)
    warning_sent = False

    for boss, times in boss_schedule.items():
        for time_str in times:
            # Tạo boss_time với múi giờ chuẩn
            boss_time_obj = datetime.strptime(time_str, "%H:%M").time()
            today = now.date()
            boss_datetime = tz.localize(datetime.combine(today, boss_time_obj))

            if boss_datetime < now:
                boss_datetime += timedelta(days=1)

            warning_time = boss_datetime - timedelta(minutes=5)

            # Cho phép lệch ±30 giây
            if abs((now - warning_time).total_seconds()) <= 30:
                await channel.send(
                    f"⚠️ Field Boss **{boss}** sẽ xuất hiện lúc {boss_datetime.strftime('%H:%M')}! Chuẩn bị nào!"
                )
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
