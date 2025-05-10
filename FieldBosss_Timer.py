import discord
import os
import sys
from datetime import datetime, timedelta
import pytz

# Lấy token và channel từ biến môi trường
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

# 🕒 Danh sách boss (field + raid)
boss_cycle_schedule = {
    # Field Boss
    "Bluemen II": {"start": "2025-05-08 00:30", "cycle_hours": 12},
    "Betalanse II": {"start": "2025-05-08 02:30", "cycle_hours": 12},
    "Cryo II": {"start": "2025-05-08 04:30", "cycle_hours": 12},
    "Sporelex II": {"start": "2025-05-08 06:30", "cycle_hours": 12},
    "Toxspore II": {"start": "2025-05-08 08:30", "cycle_hours": 12},
    "Bristol II": {"start": "2025-05-08 10:30", "cycle_hours": 12},
    "Veilian II": {"start": "2025-05-08 12:30", "cycle_hours": 12},
    "Arque II": {"start": "2025-05-08 14:30", "cycle_hours": 12},
    "Rootrus II": {"start": "2025-05-08 16:30", "cycle_hours": 12},
    "Sapphire Blade II": {"start": "2025-05-08 06:30", "cycle_hours": 12},
    "Coralisk II": {"start": "2025-05-08 08:30", "cycle_hours": 12},
    "Breeze II": {"start": "2025-05-08 10:30", "cycle_hours": 12},
    "Rootrus I": {"start": "2025-05-08 16:40", "cycle_hours": 10},
    "Sapphire Blade I": {"start": "2025-05-11 5:45", "cycle_hours": 10},
    "Coralisk I": {"start": "2025-05-10 14:50", "cycle_hours": 12},

    # RAID Boss (gộp AM + PM, chu kỳ 12h)
    "Pierror Raid": {"start": "2025-05-08 07:00", "cycle_hours": 12, "type": "raid"},
}

# 🔁 Xử lý cảnh báo boss (field + raid)
async def check_cycle_boss(schedule, now, channel):
    warning_sent = False
    closest_boss = None
    min_diff = float('inf')

    for boss, info in schedule.items():
        try:
            start_dt = tz.localize(datetime.strptime(info["start"], "%Y-%m-%d %H:%M"))
            cycle = timedelta(hours=info["cycle_hours"])
            boss_type = info.get("type", "field")
            prefix = "RAID" if boss_type == "raid" else "Field Boss"

            # Tính số chu kỳ đã qua
            elapsed_cycles = max(0, int((now - start_dt).total_seconds() // cycle.total_seconds()))
            spawn_time = start_dt + elapsed_cycles * cycle
            if spawn_time + timedelta(minutes=5) < now:
                spawn_time += cycle

            warning_time = spawn_time - timedelta(minutes=5)

            if abs((now - warning_time).total_seconds()) <= 60:
                await channel.send(
                    f"⚠️ Boss **{prefix}** {boss} sẽ xuất hiện lúc {spawn_time.strftime('%H:%M')}! Chuẩn bị nào!"
                )
                print(f"✅ Đã gửi cảnh báo cho {prefix} {boss} (xuất hiện lúc {spawn_time.strftime('%H:%M')})")
                warning_sent = True
            else:
                diff = abs((now - warning_time).total_seconds())
                if diff < min_diff:
                    min_diff = diff
                    closest_boss = (boss, spawn_time, warning_time, prefix)

        except Exception as e:
            print(f"❌ Lỗi với boss {boss}: {e}")

    if not warning_sent and closest_boss:
        boss, spawn_time, warning_time, prefix = closest_boss
        print(f"ℹ️ {prefix} gần nhất: {boss} → spawn lúc {spawn_time.strftime('%H:%M')}, cảnh báo lúc: {warning_time.strftime('%H:%M')}")

    return warning_sent

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
