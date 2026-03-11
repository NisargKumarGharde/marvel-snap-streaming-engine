# 🎮 Marvel Snap Real-Time Telemetry Pipeline
## 🏗️ Architecture Overview
This project is an end-to-end, high-throughput data engineering pipeline designed to ingest, process, and analyze live gaming telemetry from Marvel Snap. It demonstrates a modern distributed systems architecture capable of handling high-velocity event streams.

## 🛠️ The Tech Stack
Language: Python (FastAPI, Pandas)

Stream Processing: Apache Kafka (Official Docker Image)

NoSQL Database: Apache Cassandra (Distributed data persistence)

Containerization: Docker & Docker Compose

Analytics: Pandas (In-memory aggregation)

## 🚀 System Design
Telemetry Producer: A Python service that simulates concurrent match events (card plays, snaps, retreats) and streams them as JSON payloads into a Kafka broker.

Distributed Broker: Apache Kafka serves as the ingestion layer, decoupling the high-velocity game servers from the database to ensure zero data loss.

Backend Consumer: A persistent worker service that subscribes to Kafka topics and writes records into Apache Cassandra, using specific partition keys to optimize for time-series queries.

Analytics API: A FastAPI server that utilizes Pandas to extract raw data from Cassandra, performing real-time aggregations to calculate the "Meta" (most played cards) and player aggression (snap rates).

## 📂 Repository Structure
snap_producer.py: Simulates live gaming traffic.

snap_consumer.py: Bridges the gap between Kafka and Cassandra.

snap_analytics.py: Standalone script for deep analytical dives.

snap_api.py: The REST API serving live JSON metrics.

docker-compose.yml: Defines the infrastructure environment.

## 🚦 Getting Started
1. Spin up the infrastructure:

       docker-compose up -d

2. Initialize the Database:

   Once Cassandra is running, execute these commands in your terminal to set up the environment.

      i. Access the Cassandra Shell:

        docker exec -it snap-cassandra-db cqlsh

      ii. Create the Keyspace and Table:
          Copy and paste the following block into the cqlsh prompt:

       -- Create a keyspace for our analytics data
       CREATE KEYSPACE IF NOT EXISTS snap_analytics 
       WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

       -- Switch to the keyspace
       USE snap_analytics;

       -- Create the table designed for time-series gaming events
       -- match_id is the Partition Key to group data by specific games
       -- timestamp and event_id are Clustering Keys for chronological sorting
       CREATE TABLE IF NOT EXISTS match_events (
         match_id text,
         timestamp timestamp,
         event_id text,
         turn int,
         event_type text,
         player_id text,
         event_data text,
         PRIMARY KEY ((match_id), timestamp, event_id)
       ) WITH CLUSTERING ORDER BY (timestamp ASC);

      iii. Verify and Exit:

       DESCRIBE TABLE match_events;
       EXIT;

3. Start the pipeline:

       python snap_producer.py  # Terminal 1
       python snap_consumer.py  # Terminal 2
       uvicorn snap_api:app --reload --port 8001 # Terminal 3

4. Access the data:

   Visit http://localhost:8001/api/metrics to see the live JSON analytics.

## 💡 Engineering Decisions
### Why Cassandra? ### 
For a game with millions of concurrent events, we need a database that excels at write-heavy workloads. Cassandra’s masterless architecture and linear scalability make it superior to traditional SQL databases for this use case.

### Why Kafka? ### 
To prevent data loss during traffic spikes. Kafka acts as a shock absorber, allowing the database consumer to process events at its own pace without crashing the source systems.

### API Protocol: ###
Chose FastAPI for its asynchronous capabilities and automatic Swagger documentation (/docs), which simplifies the handoff to frontend engineering teams.
