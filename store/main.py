import json
from typing import List, Set
from fastapi import FastAPI, HTTPException
from sqlalchemy import MetaData, Table, Column, Float, String, Integer, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from starlette.websockets import WebSocket, WebSocketDisconnect
from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
from domain.processed_agent_data import ProcessedAgentData
from domain.processed_agent_data_in_db import ProcessedAgentDataInDB


# SQLAlchemy setup
DATABASE_URL = (f"postgresql+asyncpg://"
                f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
async_engine = create_async_engine(DATABASE_URL)
async_db_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
metadata = MetaData()

# Define the ProcessedAgentData table
processed_agent_data_table = Table(
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
        data = [json.loads(item.json()) for item in data]
        await websocket.send_json(json.dumps(data))


# FastAPI CRUD endpoints
@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData], response_model=list[ProcessedAgentDataInDB]):
    data_to_insert = []

    for processed_agent_data in data:
        data_to_insert.append(
            {
                "road_state": processed_agent_data.road_state,
                "x": processed_agent_data.agent_data.accelerometer.x,
                "y": processed_agent_data.agent_data.accelerometer.y,
                "z": processed_agent_data.agent_data.accelerometer.z,
                "latitude": processed_agent_data.agent_data.gps.latitude,
                "longitude": processed_agent_data.agent_data.gps.longitude,
                "timestamp": processed_agent_data.agent_data.timestamp
            }
        )

    async with async_db_session.begin() as session:
        query = processed_agent_data_table.insert().returning(processed_agent_data_table)

        results = await session.execute(query, data_to_insert)
        result_data = results.mappings().all()
        if len(result_data) != len(data_to_insert):
            raise Exception("Error inserting data")

    result_models = [ProcessedAgentDataInDB(**result) for result in result_data]

    # Send data to subscribers
    await send_data_to_subscribers(result_models)

    return result_models


@app.get("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
async def read_processed_agent_data(processed_agent_data_id: int):
    async with async_db_session.begin() as session:
        query = processed_agent_data_table.select().where(processed_agent_data_table.c.id == processed_agent_data_id)
        result = await session.execute(query)
        data = result.mappings().first()

    if data is None:
        raise HTTPException(status_code=404, detail="Data not found")

    return ProcessedAgentDataInDB(**data)


@app.get("/processed_agent_data/", response_model=list[ProcessedAgentDataInDB])
async def list_processed_agent_data():
    async with async_db_session.begin() as session:
        query = processed_agent_data_table.select()
        results = await session.execute(query)
        data = results.mappings().all()

    return [ProcessedAgentDataInDB(**result) for result in data]


@app.put("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
async def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    agent_data = data.agent_data

    processed_agent_data_db = ProcessedAgentDataInDB(
        id=processed_agent_data_id,
        road_state=data.road_state,
        x=agent_data.accelerometer.x,
        y=agent_data.accelerometer.y,
        z=agent_data.accelerometer.z,
        latitude=agent_data.gps.latitude,
        longitude=agent_data.gps.longitude,
        timestamp=agent_data.timestamp
    )

    async with async_db_session.begin() as session:
        # Update data in the database
        query = (
            processed_agent_data_table.update()
            .where(processed_agent_data_table.c.id == processed_agent_data_id)
            .values(
                road_state=processed_agent_data_db.road_state,
                x=processed_agent_data_db.x,
                y=processed_agent_data_db.y,
                z=processed_agent_data_db.z,
                latitude=processed_agent_data_db.latitude,
                longitude=processed_agent_data_db.longitude,
                timestamp=processed_agent_data_db.timestamp
            )
            .returning(processed_agent_data_table.c.id)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(query)
        if result.fetchone() is None:
            raise HTTPException(402, "Error updating data")

    # Return updated data
    return processed_agent_data_db


@app.delete("/processed_agent_data/{processed_agent_data_id}", status_code=204)
async def delete_processed_agent_data(processed_agent_data_id: int):
    async with async_db_session.begin() as session:
        # Delete by id
        query = processed_agent_data_table.delete().where(
            processed_agent_data_table.c.id == processed_agent_data_id
        ).returning(processed_agent_data_table.c.id)

        result = await session.execute(query)

        if result.fetchone() is None:
            raise HTTPException(status_code=404, detail="Data not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
