import json
from kafka import KafkaConsumer
from datetime import datetime, timezone
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

def start_consumer():
    print("Connecting to Cassandra Database...")
    # Connect to the Cassandra container running in Codespaces
    cluster = Cluster(['127.0.0.1'], port=9042)
    session = cluster.connect('snap_analytics')

    # Prepare the SQL-like insert statement
    insert_query = session.prepare("""
        INSERT INTO match_events 
        (match_id, timestamp, event_id, turn, event_type, player_id, event_data) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """)
    print("Successfully connected to Cassandra!")

    print("Connecting to Kafka Broker...")
    # Initialize the Kafka consumer
    consumer = KafkaConsumer(
        'marvel-snap-events',
        bootstrap_servers=['localhost:9092'],
        api_version=(3, 0, 0),
        auto_offset_reset='earliest', # Start reading from the oldest unread message
        group_id='cassandra-writer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print("Listening for Marvel Snap events... (Press Ctrl+C to stop)")

    try:
        for message in consumer:
            event = message.value
            
            # Convert the string timestamp back into a Python datetime object
            parsed_timestamp = datetime.fromisoformat(event['timestamp'])

            # Convert the nested event_data dictionary back to a string for storage
            event_data_str = json.dumps(event.get('event_data', {}))

            # Execute the insert into Cassandra
            session.execute(insert_query, (
                event['match_id'],
                parsed_timestamp,
                event['event_id'],
                event['turn'],
                event['event_type'],
                event.get('player_id', 'SYSTEM'),
                event_data_str
            ))

            print(f"Stored: {event['event_type']} from match {event['match_id'][:8]}")

    except KeyboardInterrupt:
        print("\nShutting down consumer safely...")
    finally:
        consumer.close()
        cluster.shutdown()

if __name__ == "__main__":
    start_consumer()