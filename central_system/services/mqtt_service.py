import paho.mqtt.client as mqtt
import json
import logging
import threading
import time
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MQTTService:
    """
    MQTT Service for communicating with the Faculty Desk Unit.
    """
    
    def __init__(self):
        # MQTT settings
        self.broker_host = os.environ.get('MQTT_BROKER_HOST', 'localhost')
        self.broker_port = int(os.environ.get('MQTT_BROKER_PORT', 1883))
        self.client_id = "central_system"
        self.username = os.environ.get('MQTT_USERNAME', None)
        self.password = os.environ.get('MQTT_PASSWORD', None)
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=self.client_id)
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        # Topic handlers
        self.topic_handlers = {}
        
        # Connection management
        self.is_connected = False
        self.reconnect_delay = 5  # seconds
        self.reconnect_thread = None
        self.stop_reconnect = False

    def connect(self):
        """
        Connect to the MQTT broker.
        """
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            self.schedule_reconnect()

    def disconnect(self):
        """
        Disconnect from the MQTT broker.
        """
        logger.info("Disconnecting from MQTT broker")
        self.stop_reconnect = True
        self.client.loop_stop()
        if self.is_connected:
            self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when connected to the MQTT broker.
        """
        if rc == 0:
            self.is_connected = True
            logger.info("Connected to MQTT broker")
            # Subscribe to topics
            for topic in self.topic_handlers.keys():
                self.client.subscribe(topic)
                logger.info(f"Subscribed to {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code {rc}")
            self.schedule_reconnect()

    def on_disconnect(self, client, userdata, rc):
        """
        Callback when disconnected from the MQTT broker.
        """
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker with code {rc}")
            self.schedule_reconnect()
        else:
            logger.info("Disconnected from MQTT broker")

    def on_message(self, client, userdata, msg):
        """
        Callback when message is received.
        """
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            logger.debug(f"Received message on topic {topic}: {payload}")
            
            # Process message with registered handler
            if topic in self.topic_handlers:
                data = json.loads(payload)
                for handler in self.topic_handlers[topic]:
                    try:
                        handler(topic, data)
                    except Exception as e:
                        logger.error(f"Error in message handler for topic {topic}: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {str(e)}")

    def register_topic_handler(self, topic, handler):
        """
        Register a handler for a specific topic.
        
        Args:
            topic (str): MQTT topic to subscribe to
            handler (callable): Function to call when a message is received on this topic
        """
        if topic not in self.topic_handlers:
            self.topic_handlers[topic] = []
            # If already connected, subscribe to the topic
            if self.is_connected:
                self.client.subscribe(topic)
                logger.info(f"Subscribed to {topic}")
        
        self.topic_handlers[topic].append(handler)
        logger.info(f"Registered handler for topic {topic}")

    def publish(self, topic, data):
        """
        Publish a message to a topic.
        
        Args:
            topic (str): MQTT topic to publish to
            data (dict): Data to publish (will be converted to JSON)
        """
        try:
            payload = json.dumps(data)
            self.client.publish(topic, payload)
            logger.debug(f"Published message to {topic}: {payload}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message to {topic}: {str(e)}")
            return False

    def schedule_reconnect(self):
        """
        Schedule a reconnection attempt.
        """
        if self.reconnect_thread is not None and self.reconnect_thread.is_alive():
            return
        
        self.stop_reconnect = False
        self.reconnect_thread = threading.Thread(target=self._reconnect_worker)
        self.reconnect_thread.daemon = True
        self.reconnect_thread.start()

    def _reconnect_worker(self):
        """
        Worker thread for reconnecting to the MQTT broker.
        """
        while not self.stop_reconnect and not self.is_connected:
            logger.info(f"Attempting to reconnect to MQTT broker in {self.reconnect_delay} seconds")
            time.sleep(self.reconnect_delay)
            try:
                self.client.reconnect()
            except Exception as e:
                logger.error(f"Failed to reconnect to MQTT broker: {str(e)}")

# Singleton instance
mqtt_service = None

def get_mqtt_service():
    """
    Get the singleton MQTT service instance.
    """
    global mqtt_service
    if mqtt_service is None:
        mqtt_service = MQTTService()
    return mqtt_service 