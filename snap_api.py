from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
from cassandra.cluster import Cluster

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route 1: The Homepage
@app.get("/")
def read_root():
    return {"message": "Marvel Snap Streaming API is live! Visit /api/metrics or /docs"}

# Route 2: The Actual Data
@app.get("/api/metrics")
def get_live_metrics():
    cluster = Cluster(['127.0.0.1'], port=9042)
    session = cluster.connect('snap_analytics')
    
    rows = session.execute("SELECT match_id, event_type, event_data FROM match_events")
    
    data = []
    for row in rows:
        event_dict = json.loads(row.event_data) if row.event_data else {}
        data.append({
            'match_id': row.match_id,
            'event_type': row.event_type,
            **event_dict
        })
        
    df = pd.DataFrame(data)
    cluster.shutdown()
    
    if df.empty:
        return {"error": "No data found"}
        
    cards_df = df[df['event_type'] == 'card_played']
    top_cards = cards_df['card_name'].value_counts().head(3).to_dict() if not cards_df.empty and 'card_name' in cards_df.columns else {}
    
    snaps = len(df[df['event_type'] == 'snapped'])
    total_matches = int(df['match_id'].nunique())
    snap_rate = round(snaps / total_matches, 2) if total_matches > 0 else 0
    
    return {
        "total_matches": total_matches,
        "snap_rate": snap_rate,
        "top_cards": top_cards
    }