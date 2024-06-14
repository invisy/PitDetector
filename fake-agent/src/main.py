import threading

from paho.mqtt import client as mqtt_client
import time

from file_datasource import AgentFileDatasource, ParkingFileDatasource
from schema.aggregated_data_schema import AggregatedDataSchema
import config
from schema.parking_schema import ParkingSchema


def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print("Failed to connect {broker}:{port}, return code %d\n", rc)
            exit(rc) # Stop execution
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client


def publish(client, topic, datasource, schema, delay):
    datasource.startReading()
    while True:
        time.sleep(delay)
        data = datasource.read()
        msg = schema().dumps(data)
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            pass
            # print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")


def run():
    # Prepare mqtt client
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)
    # Prepare datasources
    agent_datasource = AgentFileDatasource("data/accelerometer.csv", "data/gps.csv")
    parking_datasource = ParkingFileDatasource("data/parking.csv")

    # Infinity publish data
    thread1 = threading.Thread(target=publish, args=(client, config.MQTT_AGENT_TOPIC, agent_datasource,
                                                     AggregatedDataSchema, config.DELAY))
    thread2 = threading.Thread(target=publish, args=(client, config.MQTT_PARKING_TOPIC, parking_datasource,
                                                     ParkingSchema, config.DELAY))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


if __name__ == '__main__':
    run()
