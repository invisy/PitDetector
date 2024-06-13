import json
from datetime import datetime
from typing import List, Set
from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, MetaData, Table, Column, Float, String, Integer, DateTime
from starlette.websockets import WebSocket, WebSocketDisconnect
from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB


# SQLAlchemy setup
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
# Define the ProcessedAgentData table
processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)


# FastAPI models
class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float


class GpsData(BaseModel):
    latitude: float
    longitude: float


class AgentData(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime

@classmethod
@field_validator('timestamp', mode='before')
def check_timestamp(cls, value):
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError("Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).")


class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData


# Database model
class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime


# FastAPI app setup
app = FastAPI()
# WebSocket subscriptions
subscriptions: Set[WebSocket] = set()
# FastAPI WebSocket endpoint
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriptions.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions.remove(websocket)

# Function to send data to subscribed users
async def send_data_to_subscribers(data):
    for websocket in subscriptions:
        await websocket.send_json(json.dumps(data))


# FastAPI CRUD endpoints
@app.post("/processed_agent_data/")
async def create_processed_agent_data(data:List[ProcessedAgentData]):
    # Insert data to database
    # Send data to subscribers

@app.get("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int):
    # Get data by id

@app.get("/processed_agent_data/", response_model=list[ProcessedAgentDataInDB])
def list_processed_agent_data():
    query = processed_agent_data.select()

    conn = engine.connect()
    results = conn.execute(query).fetchall()
    conn.close()
    return [ProcessedAgentDataInDB(**result) for result in results]

@app.put(
"/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    agent_data = data.agent_data

    processed_agent_data_db = ProcessedAgentDataInDB(
        id=processed_agent_data_id,
        road_state=agent_data.road_state,
        x=agent_data.accelerometer.x,
        y=agent_data.accelerometer.y,
        z=agent_data.accelerometer.z,
        latitude=agent_data.gps.latitude,
        longitude=agent_data.gps.longitude,
        timestamp=agent_data.timestamp
    )

    # Update data in the database
    query = (
        processed_agent_data.update()
        .where(processed_agent_data.c.id == processed_agent_data_id)
        .values(
            road_state=processed_agent_data_db.road_state,
            x=processed_agent_data_db.x,
            y=processed_agent_data_db.y,
            z=processed_agent_data_db.z,
            latitude=processed_agent_data_db.latitude,
            longitude=processed_agent_data_db.longitude,
            timestamp=processed_agent_data_db.timestamp
        )
    )
    conn = engine.connect()
    conn.execute(query)
    conn.close()

    # Return updated data
    return processed_agent_data_db

@app.delete("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def delete_processed_agent_data(processed_agent_data_id: int):
    # Delete by id
    query = processed_agent_data.delete().where(processed_agent_data.c.id == processed_agent_data_id)
    conn = engine.connect()
    conn.execute(query)
    conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)