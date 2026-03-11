import pandas as pd
import json
from cassandra.cluster import Cluster

def run_analytics():
    print("Connecting to Cassandra to fetch live telemetry...")
    cluster = Cluster(['127.0.0.1'], port=9042)
    session = cluster.connect('snap_analytics')

    # Pull the massive dataset into memory
    print("Extracting data...")
    query = "SELECT match_id, event_type, event_data FROM match_events"
    rows = session.execute(query)

    # Transform the raw rows and nested JSON into a flat, structured format
    data = []
    for row in rows:
        event_dict = json.loads(row.event_data) if row.event_data else {}
        data.append({
            'match_id': row.match_id,
            'event_type': row.event_type,
            **event_dict  # Unpack the JSON properties into distinct columns
        })

    # Load into a Pandas DataFrame for heavy analytical processing
    df = pd.DataFrame(data)

    if df.empty:
        print("No data found! Make sure your producer and producer are running.")
        cluster.shutdown()
        return

    print("\n" + "="*30)
    print("  MARVEL SNAP LIVE METRICS  ")
    print("="*30)

    # Metric 1: The current meta (Most Played Cards)
    cards_df = df[df['event_type'] == 'card_played']
    if not cards_df.empty and 'card_name' in cards_df.columns:
        top_cards = cards_df['card_name'].value_counts().head(3)
        print("\n🔥 Top 3 Most Played Cards:")
        print(top_cards.to_string())

    # Metric 2: Player Aggression (Total Snaps vs Matches)
    snaps = len(df[df['event_type'] == 'snapped'])
    total_matches = df['match_id'].nunique()
    if total_matches > 0:
        print(f"\n🎲 Average Snaps per Match: {snaps / total_matches:.2f}")

    # Metric 3: Most Dangerous Location (Where most retreats happen)
    # This requires looking at matches that ended in a retreat and seeing which locations were active
    print("\nTotal Unique Matches Analyzed:", total_matches)
    print("="*30 + "\n")

    cluster.shutdown()

if __name__ == "__main__":
    run_analytics()