
import schedule
import time
from fetch_data import fetch_all_workflows, save_to_file


def job():
    print("\n🚀 Running scheduled job...")

    try:
        workflows = fetch_all_workflows()
        save_to_file(workflows)

        print("✅ Workflows updated successfully!")

    except Exception as e:
        print(f"❌ Scheduler error: {e}")


# 🔥 Run multiple times per day (faster growth)
schedule.every(6).hours.do(job)   # every 6 hours

# Optional: also run once immediately
job()

print("⏳ Scheduler running... Press Ctrl+C to stop")

while True:
    schedule.run_pending()
    time.sleep(60)

