import schedule
import time
from fetch_data import fetch_all_workflows, save_to_file

def job():
    workflows = fetch_all_workflows()
    save_to_file(workflows)
    print("Workflows updated!")
schedule.every().day.at("02:00").do(job)
print("Scheduler running... Press Ctrl+C to stop")
while True:
    schedule.run_pending()
    time.sleep(60)
