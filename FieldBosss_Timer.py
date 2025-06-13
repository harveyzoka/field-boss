import os
import sys
import requests
from datetime import datetime, timedelta
import pytz

# Lấy webhook URL từ biến môi trường
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
print(WEBHOOK_URL)

if not WEBHOOK_URL:
    print("❌ Thiếu DISCORD_WEBHOOK_URL trong biến môi trường.")
    sys.exit(1)

tz = pytz.timezone('Asia/Ho_Chi_Minh')

# 🕒 Danh sách boss (field + raid)
boss_cycle_schedule = {
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
    "Betalanse I": {"start": "2025-05-21 17:05", "cycle_hours": 2},
    "Blumen I": {"start": "2025-06-13 12:00", "cycle_hours": 2},
    "Cryo I": {"start": "2025-06-13 14:10", "cycle_hours": 4},
    "Sporelex I": {"start": "2025-06-13 11:15", "cycle_hours": 4},
    "Toxspore I": {"start": "2025-06-13 14:20", "cycle_hours": 6},
    "Bristol I": {"start": "2025-06-13 15:25", "cycle_hours": 6},
    "Veilian I": {"start": "2025-06-14 6:30", "cycle_hours": 8},
    "Arque I": {"start": "2025-06-13 15:35", "cycle_hours": 8},
    "Breeze I": {"start": "2025-06-13 15:55", "cycle_hours": 12},
    "Pierror Raid": {"start": "2025-05-08 07:00", "cycle_hours": 12, "type": "raid"},
}

def send_alert(boss, spawn_time, prefix):
    content = f"⚠️ Boss **{prefix}** {boss} sẽ xuất hiện lúc {spawn_time.strftime('%H:%M')}! Chuẩn bị nào!"
    data = {"content": content}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print(f"✅ Đã gửi webhook: {content}")
    else:
        print(f"❌ Lỗi webhook: {response.status_code} {response.text}")

def check_cycle_boss(schedule, now):
    warning_sent = False
    closest_boss = None
    min_diff = float('inf')

    for boss, info in schedule.items():
        try:
            start_dt = tz.localize(datetime.strptime(info["start"], "%Y-%m-%d %H:%M"))
            cycle = timedelta(hours=info["cycle_hours"])
            boss_type = info.get("type", "field")
            prefix = "RAID" if boss_type == "raid" else "Field Boss"

            elapsed_cycles = max(0, int((now - start_dt).total_seconds() // cycle.total_seconds()))
            spawn_time = start_dt + elapsed_cycles * cycle
            if spawn_time + timedelta(minutes=5) < now:
                spawn_time += cycle

            warning_time = spawn_time - timedelta(minutes=5)

            if abs((now - warning_time).total_seconds()) <= 80:
                send_alert(boss, spawn_time, prefix)
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

if __name__ == "__main__":
    now = datetime.now(tz)
    print(f"🤖 Bắt đầu kiểm tra boss lúc {now.strftime('%Y-%m-%d %H:%M:%S')}")
    check_cycle_boss(boss_cycle_schedule, now)
