from paho.mqtt import client as mqtt

client = mqtt.Client(
    client_id="sub-luhan",
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

def on_message(client, userdata, msg):
    print(f"{msg.topic} -> {msg.payload.decode(errors='ignore')}")

client.on_message = on_message

client.connect("localhost", 1883, 60)

client.subscribe("testing", qos=0)   # subscribe ngay sau connect

client.loop_forever()
