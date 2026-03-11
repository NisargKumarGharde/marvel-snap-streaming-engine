import json
import time
import random
import uuid
from datetime import datetime, timezone
from kafka import KafkaProducer

# Mock Data Dictionaries
LOCATIONS = ["Wakanda", "Asgard", "Kamar-Taj", "Sanctum Sanctorum", "Baxter Building", "Death's Domain"]
CARDS = ["Loki", "Spider-Man", "Venom", "Shang-Chi", "Klaw", "Red Hulk", "Ultron", "Vision", "Captain Marvel", "Thor", "Doctor Stange", "Iron Fist"]
EVENTS = ["card_played", "location_revealed", "snapped", "retreated", "turn_ended"]

def generate_marvel_snap_event(match_id, player_1_id, player_2_id, turn):
    """Generates a single, randomized Marvel Snap event."""
    event_type = random.choice(EVENTS)

    # Base payload optimized for our future Cassandra schema
    event = {
        "event_id": str(uuid.uuid4()),
        "match_id": match_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "turn": turn,
        "event_type": event_type,
        "event_data": {}
    }

    # Populate dynamic data based on the specifict() event type
    if event_type == "card_played":
        event["player_id"] = random.choice([player_1_id, player_2_id])
        event["event_data"] = {
            "card_name": random.choice(CARDS),
            "location_index": random.randint(1, 3), # Left, Middle, or Right location
            "energy_cost": random.randint(1, 6)
        }

    elif event_type == "location_revealed":
        event["event_data"] = {
            "location_name": random.choice(LOCATIONS),
            "location_index": random.randint(1, 3)
        }

    elif event_type == "snapped":
        event["player_id"] = random.choice([player_1_id, player_2_id])
        event["event_data"] = {"cubes_lost": random.choice([2, 4, 8])}
    
    elif event_type == "retreated":
        event["player_id"] = random.choice([player_1_id, player_2_id])
        event["event_data"] = {"cubes_lost": random.choice([1, 2, 4])}

    return event

def stream_events():
    """Simulates a continuous stream of concurrent matches to Kafka."""
    print("Connecting to Kafka Broker...")

    # Initialize the Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        api_version=(3, 0, 0),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print("Starting Marvel Snap Event Stream... (Press Ctrl+C to stop)")
    active_matches = {str(uuid.uuid4()): (str(uuid.uuid4()), str(uuid.uuid4())) for _ in range(5)}
    
    try:
        while True:
            match_id, players = random.choice(list(active_matches.items()))
            turn = random.randint(1, 6)
            
            payload = generate_marvel_snap_event(match_id, players[0], players[1], turn)
            
            # Send the payload to the Kafka topic
            # We use match_id as the key to ensure events for the same match stay in order
            producer.send(
                topic='marvel-snap-events',
                key=match_id.encode('utf-8'),
                value=payload
            )
            
            print(f"Sent {payload['event_type']} for match {match_id[:8]}...")
            time.sleep(random.uniform(0.2, 0.8))
            
    except KeyboardInterrupt:
        print("\nFlushing remaining messages to Kafka...")
        producer.flush() # Ensure all messages are sent before shutting down
        print("Stream stopped safely.")

if __name__ == "__main__":
    stream_events()