
import paho.mqtt.client as mqtt
import psycopg2
from datetime import datetime, timedelta
import json
import threading
import time

class DataHandler:
    def __init__(self):
        # Conexión MQTT
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect("localhost", 1883, 60)
        self.mqtt_client.loop_start()
        
        # Conexión PostgreSQL
        self.pg_conn = psycopg2.connect(
            dbname="registers",
            user="postgres",
            password="postgres",
            host="localhost"
        )
        
        # Iniciar el monitor de timeouts
        self.timeout_thread = threading.Thread(target=self.check_timeouts)
        self.timeout_thread.daemon = True
        self.timeout_thread.start()

    def on_connect(self, client, userdata, flags, rc):
        self.mqtt_client.subscribe("detecciones/ack/#")

    def on_message(self, client, userdata, msg):
        if msg.topic.startswith("detecciones/ack/"):
            message_id = msg.topic.split('/')[-1]
            self.redis_client.delete(f"detection:{message_id}")

    def save_detection(self, detection_data):
        message_id = f"{datetime.now().timestamp()}"
        detection_data['message_id'] = message_id
        detection_data['timestamp_stored'] = datetime.now().isoformat()
        
        # Guardar en Redis
        self.redis_client.setex(
            f"detection:{message_id}",
            60,  # TTL de 60 segundos
            json.dumps(detection_data)
        )
        
        # Publicar en MQTT
        self.mqtt_client.publish(
            f"detecciones/datos/{message_id}",
            json.dumps(detection_data)
        )

    def save_to_postgresql(self, detection_data):
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO detections 
                (timestamp, total_personas, detecciones, message_id) 
                VALUES (%s, %s, %s, %s)
            """, (
                detection_data['timestamp'],
                detection_data['total_personas'],
                json.dumps(detection_data['detecciones']),
                detection_data['message_id']
            ))
        self.pg_conn.commit()

    def check_timeouts(self):
        while True:
            for key in self.redis_client.scan_iter("detection:*"):
                data = self.redis_client.get(key)
                if data:
                    detection_data = json.loads(data)
                    stored_time = datetime.fromisoformat(detection_data['timestamp_stored'])
                    if datetime.now() - stored_time > timedelta(minutes=1):
                        self.save_to_postgresql(detection_data)
                        self.redis_client.delete(key)
            time.sleep(10)