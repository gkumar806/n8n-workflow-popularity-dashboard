from fastapi import FastAPI,Query,HTTPException
from fastapi.responses import JSONResponse
import json
import uvicorn
app = FastAPI(title="n8n Workflow Popularity API",version="1.0")

try:
    with open("workflows.json", "r") as f:
        all_workflows=json.load(f)
except:
    all_workflows=[]
@app.get("/workflows")
def get_workflows(platform:str=None,country:str=None,limit:int=50):
    if not all_workflows:
        return {"error": "No data available. Run fetch_data.py first"}
    
    filtered=all_workflows
    if platform:
        filtered=[w for w in filtered if w["platform"].lower()==platform.lower()]
    if country:
        filtered=[w for w in filtered if w["country"].upper() == country.upper()]
    for w in filtered:
        metrics=w["popularity_metrics"]
        if "views" in metrics:
            w["score"]=metrics["views"]
        elif "replies" in metrics:
            w["score"]=metrics["replies"]
        elif "average_interest" in metrics:
            w["score"]=metrics["average_interest"]
        else:
            w["score"]=0
    
    filtered.sort(key=lambda x:x["score"],reverse=True)
    for w in filtered:
        w.pop("score",None)
    
    return {"count":len(filtered[:limit]),"workflows":filtered[:limit]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
