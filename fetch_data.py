
import json
import time
import requests
from config import YOUTUBE_KEY, DISCOURSE_URL, COUNTRIES, GITHUB_TOKEN


# =========================
# 🎥 YOUTUBE (PAGINATION)
# =========================
def fetch_youtube_workflows(country):
    print(f"\n🎥 Fetching YouTube data for {country}")

    url = "https://www.googleapis.com/youtube/v3/search"
    all_data = []
    next_page_token = None

    for i in range(10):  # ~500 results
        params = {
            "part": "snippet",
            "q": "n8n workflow",
            "maxResults": 50,
            "regionCode": country,
            "type": "video",
            "key": YOUTUBE_KEY
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
              print("❌ YouTube API FAILED")
              print("Status Code:", response.status_code)
              print("Response:", response.text)
              break

            data = response.json()
            items = data.get("items", [])

            for item in items:
                video_id = item.get("id", {}).get("videoId")
                if not video_id:
                    continue

                all_data.append({
                    "workflow": item["snippet"]["title"],
                    "platform": "YouTube",
                    "country": country,
                    "popularity_metrics": {"views": 0},
                    "url": f"https://youtube.com/watch?v={video_id}"
                })

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

            time.sleep(1)

        except Exception as e:
            print(f"❌ YouTube ERROR: {e}")
            break

    print(f"✅ YouTube total: {len(all_data)}")
    return all_data


# =========================
# 💬 DISCOURSE (PAGINATION)
# =========================
def fetch_discourse_workflows(country):
    print(f"\n💬 Fetching Discourse data for {country}")

    all_data = []

    for page in range(10):  # ~300 results
        url = f"{DISCOURSE_URL}/latest.json?page={page}"

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()

            topics = resp.json().get("topic_list", {}).get("topics", [])

            for t in topics:
                all_data.append({
                    "workflow": t.get("title"),
                    "platform": "Discourse",
                    "country": country,
                    "popularity_metrics": {
                        "views": t.get("views", 0),
                        "replies": t.get("posts_count", 0)
                    },
                    "url": f"{DISCOURSE_URL}/t/{t.get('id')}"
                })

            time.sleep(1)

        except Exception as e:
            print(f"❌ Discourse ERROR: {e}")
            break

    print(f"✅ Discourse total: {len(all_data)}")
    return all_data


# =========================
# 🐙 GITHUB API
# =========================
def fetch_github_workflows(country):
    print(f"\n🐙 Fetching GitHub data for {country}")

    url = "https://api.github.com/search/repositories"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    all_data = []

    for page in range(1, 6):  # 5 pages × 50 = 250 repos
        params = {
            "q": "n8n workflow",
            "sort": "stars",
            "order": "desc",
            "per_page": 50,
            "page": page
        }

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)

            if resp.status_code != 200:
                print("❌ GitHub API FAILED:", resp.text)
                break

            repos = resp.json().get("items", [])

            for r in repos:
                all_data.append({
                    "workflow": r.get("name"),
                    "platform": "GitHub",
                    "country": country,
                    "popularity_metrics": {
                        "stars": r.get("stargazers_count", 0),
                        "forks": r.get("forks_count", 0)
                    },
                    "url": r.get("html_url")
                })

            time.sleep(1)

        except Exception as e:
            print(f"❌ GitHub ERROR: {e}")
            break

    print(f"✅ GitHub total: {len(all_data)}")
    return all_data


# =========================
# 🚀 FETCH ALL
# =========================
def fetch_all_workflows():
    data = []

    for country in COUNTRIES:
        print(f"\n📍 Fetching data for {country}")

        yt = fetch_youtube_workflows(country)
        dc = fetch_discourse_workflows(country)
        gh = fetch_github_workflows(country)

        print(f"\n📊 SUMMARY for {country}:")
        print(f"YouTube: {len(yt)}")
        print(f"Discourse: {len(dc)}")
        print(f"GitHub: {len(gh)}")

        data.extend(yt)
        data.extend(dc)
        data.extend(gh)

    return data


# =========================
# 💾 SAVE (DEDUPLICATION)
# =========================
def save_to_file(new_data, filename="workflows.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    except:
        old_data = []

    combined = old_data + new_data

    # 🔥 Remove duplicates using URL
    unique = {item["url"]: item for item in combined}
    final_data = list(unique.values())

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Total unique workflows: {len(final_data)}")


# =========================
# ▶️ MAIN
# =========================
if __name__ == "__main__":
    print("🚀 Fetching all workflows...")

    workflows = fetch_all_workflows()
    save_to_file(workflows)

    print("🎉 Done!")
