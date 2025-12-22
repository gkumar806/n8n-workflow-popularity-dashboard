import json
import requests
from pytrends.request import TrendReq
from config import YOUTUBE_KEY,DISCOURSE_URL,COUNTRIES
def fetch_youtube_workflows(country):
    url="https://www.googleapis.com/youtube/v3/search"
    params = {
        "part":"snippet",
        "q":"n8n workflow",
        "maxResults":50,
        "regionCode":country,
        "type":"video",
        "key":YOUTUBE_KEY
    }
    response = requests.get(url, params=params)
    data=[]
    for item in response.json().get("items",[]):
        video_id=item["id"].get("videoId")
        if not video_id:
            continue
        data.append({
            "workflow":item["snippet"]["title"],
            "platform":"YouTube",
            "country":country,
            "popularity_metrics":{
                "views":0,    
                "likes":0,
                "comments":0
            },
            "url":f"https://youtube.com/watch?v={video_id}"
        })
    return data


def fetch_discourse_workflows(country):
    url=f"{DISCOURSE_URL}/latest.json"
    try:
        resp=requests.get(url)
        topics=resp.json().get("topic_list",{}).get("topics",[])
        data=[]
        for t in topics:
            data.append({
                "workflow":t.get("title"),
                "platform":"Discourse",
                "country":country,
                "popularity_metrics":{
                    "views":t.get("views",0),
                    "likes":t.get("like_count",0),
                    "replies":t.get("posts_count",0),
                    "contributors":t.get("last_poster_id",1)
                },
              "url": f"{DISCOURSE_URL}/t/{t.get('id')}"
            })
        return data
    except Exception as e:
        print(f"Discourse fetch failed: {e}")
        return []



def fetch_google_workflows(country):
    pytrends=TrendReq()
    keywords=["n8n workflow","n8n automation","n8n tutorial","n8n integration"]
    data=[]

    for kw in keywords:
        try:
            pytrends.build_payload([kw],timeframe="today 3-m",geo=country)
            interest=pytrends.interest_over_time()
            if not interest.empty:
                avg=int(interest[kw].mean())
                latest=int(interest[kw].iloc[-1])
            else:
                avg=latest=0
            data.append({
                "workflow":kw,
                "platform":"Google",
                "country":country,
                "popularity_metrics":{
                    "average_interest":avg,
                    "latest_interest":latest
                },
                "url":"https://trends.google.com"
            })
        except Exception as e:
            print(f"Google Trends fetch failed for {kw}:{e}")
            continue
    return data



def fetch_all_workflows():
    data=[]
    for country in COUNTRIES:
        data.extend(fetch_youtube_workflows(country))
        data.extend(fetch_discourse_workflows(country))
        data.extend(fetch_google_workflows(country))
    return data



def save_to_file(workflows,filename="workflows.json"):
    with open(filename,"w",encoding="utf-8") as f:
        json.dump(workflows,f,indent=2,ensure_ascii=False)
    print(f"Saved {len(workflows)} workflows to {filename}")



if __name__ == "__main__":
    print("Fetching all workflows...")
    workflows = fetch_all_workflows()
    save_to_file(workflows)
    print("Done! Now run api.py to serve the data.")
