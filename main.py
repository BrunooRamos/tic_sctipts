from count_people import get_people_stream
from get_measure import get_random_measure
from connection_handler import (
    mqtt_connection, connect_to_iot_core, subscribe_to_topic, topic
)
import json

def main():
    # 1. Conectar a AWS IoT Core y suscribirse
    connect_to_iot_core()
    subscribe_to_topic()

    # 2. Procesar frames de la cámara y contar personas
    for people_count in get_people_stream():
        # 3. Obtener medición ficticia
        medida = get_random_measure()

        # 4. Unir la información en un solo mensaje
        mensaje = {
            "people": people_count,
            "humidity": medida["humidity"],
            "temperature": medida["temperature"],
            "co2": medida["co2"]
        }

        # 5. Publicar a MQTT
        mqtt_connection.publish(
            topic,
            json.dumps(mensaje),
            qos=1
        )
if __name__ == "__main__":
    main()