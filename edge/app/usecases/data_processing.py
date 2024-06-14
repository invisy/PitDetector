from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    if agent_data.accelerometer.y > 3000:
        road_state = "bump"
    elif agent_data.accelerometer.y < -2000:
        road_state = "pothole"
    else:
        road_state = "smooth"

    return ProcessedAgentData(road_state=road_state, agent_data=agent_data)
