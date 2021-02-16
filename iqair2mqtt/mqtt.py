import logging
import paho.mqtt.client as mqtt

from iqair2mqtt.errors import MQTTBrokerNotConnected

logger = logging.getLogger(__name__)


class MQTTPublisher:

    def __init__(self, hostname: str, login: str, password: str, topic: str):
        self._hostname = hostname
        self._topic = topic
        self._connected = False
        self._client = mqtt.Client(client_id='iqair2mqtt')
        # TODO certificates
        self._client.username_pw_set(login, password)
        self._client.on_connect = self._on_connect_callback
        self._client.on_disconnect = self._on_disconnect_callback

        logger.debug("Starting MQTT client loop")

    def connect(self):
        self._client.connect(self._hostname)
        self._client.loop_start()  # Add loop stop, on exit

    def _on_connect_callback(self, client, userdata, flags, rc):
        if rc == 0:
            logger.debug("Connected to MQTT broker on host %s", self._hostname)
            self._connected = True
        else:
            logger.warning(
                "Can't connect to MQTT broker on host %s, rc is %d",
                self._hostname,
                rc,
            )

    def _on_disconnect_callback(self, client, userdata, flags, rc):
        self._connected = False
        logger.info("Disconnected from MQTT broker on host %s", self._hostname)

    def publish(self, data: str):
        if not self._connected:
            # TODO consider change this to warning and store last N message, trying to send them again
            raise MQTTBrokerNotConnected()

        # TODO check that message was published
        self._client.publish(
            topic=self._topic,
            payload=data,
            qos=2,  # we are not limited for energy
        )
