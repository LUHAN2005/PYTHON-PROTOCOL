
from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTTMessage

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = "LUHAN_SUB"
)

def on_message(client : mqtt.Client, userdata, msg : MQTTMessage):
    print(msg.topic, msg.payload.decode(errors = "ignore"), "qos =",msg.qos, "retain =",msg.retain)

def on_connect(client : mqtt.Client, userdata, flags, reason_code, properties):
    print("Connect:",reason_code)
    client.subscribe("test/#", qos=1)

def on_disconnect(client : mqtt.Client, userdata, flags, reason_code, properties):
    print("Disconnect:",reason_code)

client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.connect("localhost", 1883, 60)

client.loop_forever()