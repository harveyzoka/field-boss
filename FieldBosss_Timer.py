import discord
import os
import sys
from datetime import datetime, timedelta
import pytz
import asyncio

# Lấy token và kênh từ biến môi trường
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID_STR = os.getenv('DISCORD_CHANNEL_ID')

if not TOKEN or not CHANNEL_ID_STR:
    print("❌ Thiếu biến môi trường.")
    sys.exit(1)

CHANNEL_ID = int(CHANNEL_ID_STR)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

tz = pytz.timezone('Asia/Ho_Chi_Minh')

# 🕒 Danh sách boss với thời gian spawn động
boss_cycle_schedule = {
    "Bluemen II": {
        "start": "2025-05-08 00:30",
        "cycle_hours": 12
    },
    "Betalanse II": {
        "start": "2025-05-08 02:30",
        "cycle_hours": 12
    },
    "Cryo II": {
        "start": "2025-05-08 04:30",
        "cycle_hours": 12
    },
    "Sporelex II": {
        "start": "2025-05-08 06:30",
        "cycle_hours": 12
    },
    "Toxspore II": {
        "start": "2025-05-08 08:30",
        "cycle_hours": 12
    },
    "Bristol II": {
        "start": "2025-05-08 10:30",
        "cycle_hours": 12
    },
    "Veilian II": {
        "start": "2025-05-08 12:30",
        "cycle_hours": 12
    },
    "Arque II": {
        "start": "2025-05-08 14:30",
        "cycle_hours": 12
    },
    "Rootrus II": {
        "start": "2025-05-08 16:30",
        "cycle_hours": 12
    },
    "Sapphire Blade II": {
        "start": "2025-05-08 06:30",
        "cycle_hours": 12
    },
    "Coralisk II": {
        "start": "2025-05-08 08:30",
        "cycle_hours": 12
    },
    "Breeze II": {
        "start": "2025-05-08 10:30",
        "cycle_hours": 12
    },
    "Rootrus I": {
        "start": "2025-05-08 16:40",
        "cycle_hours": 10
    },    "Sapphire Blade I": {
        "start": "2025-05-08 06:30",
        "cycle_hours": 12
    },
    "Coralisk I": {
        "start": "2025-05-08 08:30",
        "cycle_hours": 12
    }

}

# 🔁 Hàm xử lý boss theo chu kỳ (chuẩn, không lệch chu kỳ)
async def check_cycle_boss(schedule, now, channel):
    warning_sent = False

    for boss, info in schedule.items():
        try:
            start_dt = tz.localize(datetime.strptime(info["start"], "%Y-%m-%d %H:%M"))
            cycle = timedelta(hours=info["cycle_hours"])

            if now < start_dt:
                next_spawn = start_dt
            else:
                # Tính số chu kỳ đã qua kể từ thời điểm bắt đầu
                elapsed_cycles = int((now - start_dt).total_seconds() // cycle.total_seconds())
                spawn_time = start_dt + elapsed_cycles * cycle

                # Nếu cảnh báo của chu kỳ hiện tại đã qua, chuyển sang chu kỳ tiếp theo
                if spawn_time + timedelta(minutes=5) < now:
                    spawn_time += cycle

                next_spawn = spawn_time

            warning_time = next_spawn - timedelta(minutes=5)

            # So sánh trong khoảng ±60 giây quanh cảnh báo
            if abs((now - warning_time).total_seconds()) <= 60:
                await channel.send(
                    f"⚠️ Field Boss **{boss}** sẽ xuất hiện lúc {next_spawn.strftime('%H:%M')}! Chuẩn bị nào!"
                )
                print(f"✅ Đã gửi cảnh báo cho {boss} (xuất hiện lúc {next_spawn.strftime('%H:%M')})")
                warning_sent = True
            else:
                print(f"⏳ {boss} - Giờ spawn tiếp theo: {next_spawn.strftime('%H:%M')}, cảnh báo lúc: {warning_time.strftime('%H:%M')}, hiện tại: {now.strftime('%H:%M:%S')}")

        except Exception as e:
            print(f"❌ Lỗi với boss {boss}: {e}")

    return warning_sent

# 🟢 Khi bot online
@bot.event
async def on_ready():
    now = datetime.now(tz)
    channel = bot.get_channel(CHANNEL_ID)
    print(f"🤖 Bot đã khởi động lúc {now.strftime('%Y-%m-%d %H:%M:%S')}")

    sent = await check_cycle_boss(boss_cycle_schedule, now, channel)

    if not sent:
        print("✅ Không có boss nào cần cảnh báo lúc này.")

    await bot.close()

bot.run(TOKEN)
