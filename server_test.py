import paho.mqtt.client as mqtt

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    print("Received message: " + str(msg.payload))


client = mqtt.Client(client_id="gui")
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("172.20.10.6", 1883)
client.subscribe("sensor", qos=1)

client.loop_forever()