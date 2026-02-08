
from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTTMessage 

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = "LUHAN_sub"
)

def on_message(client : mqtt.Client, userdata, msg : MQTTMessage):
    print(msg.topic, "qos=", msg.qos, "retain=", msg.retain, "payload=", msg.payload.decode(errors="ignore"))


def on_connect(client : mqtt.Client, userdata, flags, reason_code, properties):
    print("Connect:",reason_code)
    client.subscribe("test/#", qos=1)



client.on_message = on_message
client.on_connect = on_connect

client.connect("localhost", 1883, 60)

client.loop_forever()
