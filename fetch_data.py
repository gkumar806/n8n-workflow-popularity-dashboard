import json
import time
import requests
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
from config import YOUTUBE_KEY, DISCOURSE_URL, COUNTRIES


def fetch_youtube_workflows(country):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": "n8n workflow",
        "maxResults": 50,
        "regionCode": country,
        "type": "video",
        "key": YOUTUBE_KEY
    }

    response = requests.get(url, params=params, timeout=10)

    # 🔍 DEBUG YouTube API
    print("\n--- YouTube API DEBUG ---")
    print("Country:", country)
    print("Status Code:", response.status_code)
    print("Response:", response.text[:500])  # first 500 chars
    print("------------------------\n")

    data = []

    if response.status_code != 200:
        return data

    for item in response.json().get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue

        data.append({
            "workflow": item["snippet"]["title"],
            "platform": "YouTube",
            "country": country,
            "popularity_metrics": {
                "views": 0,
                "likes": 0,
                "comments": 0
            },
            "url": f"https://youtube.com/watch?v={video_id}"
        })

    return data


def fetch_discourse_workflows(country):
    # ✅ FIXED: no double latest.json
    url = f"{DISCOURSE_URL}/latest.json"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        topics = resp.json().get("topic_list", {}).get("topics", [])
        data = []

        for t in topics:
            data.append({
                "workflow": t.get("title"),
                "platform": "Discourse",
                "country": country,
                "popularity_metrics": {
                    "views": t.get("views", 0),
                    "likes": t.get("like_count", 0),
                    "replies": t.get("posts_count", 0),
                    "contributors": t.get("last_poster_id", 1)
                },
                "url": f"{DISCOURSE_URL}/t/{t.get('id')}"
            })

        return data

    except Exception as e:
        print(f"❌ Discourse fetch failed: {e}")
        return []


def fetch_google_workflows(country):
    pytrends = TrendReq(hl="en-US", tz=360)
    keywords = [
        "n8n workflow",
        "n8n automation",
        "n8n tutorial",
        "n8n integration"
    ]

    data = []

    for kw in keywords:
        try:
            time.sleep(8)  # ⏳ VERY IMPORTANT

            pytrends.build_payload(
                [kw],
                timeframe="today 3-m",
                geo=country
            )

            interest = pytrends.interest_over_time()

            if interest.empty:
                continue

            data.append({
                "workflow": kw,
                "platform": "Google",
                "country": country,
                "popularity_metrics": {
                    "average_interest": int(interest[kw].mean()),
                    "latest_interest": int(interest[kw].iloc[-1])
                },
                "url": "https://trends.google.com"
            })

        except TooManyRequestsError:
            print(f"⚠️ Google Trends blocked (429) — skipping {kw}")
            break   # stop further requests for this run

        except Exception as e:
            print(f"❌ Google Trends error for {kw}: {e}")

    return data


def fetch_all_workflows():
    data = []
    for country in COUNTRIES:
        print(f"\n📍 Fetching data for {country}")
        data.extend(fetch_youtube_workflows(country))
        data.extend(fetch_discourse_workflows(country))
        data.extend(fetch_google_workflows(country))
    return data


def save_to_file(workflows, filename="workflows.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(workflows, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(workflows)} workflows to {filename}")


if __name__ == "__main__":
    print("🚀 Fetching all workflows...")
    workflows = fetch_all_workflows()
    save_to_file(workflows)
    print("🎉 Done! Now run api.py to serve the data.")
