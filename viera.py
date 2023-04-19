import logging
from dotenv import load_dotenv
import os
import panasonic_viera            # pip install panasonic_viera, aiohttp
                                  #https://github.com/florianholzapfel/panasonic-viera
import paho.mqtt.client as paho   # pip install paho-mqtt
import socket 

load_dotenv()
version = '0.1'
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
_LOGGER.addHandler(ch)


class VieraMQTTHandler():

    def __init__(self,  mqtt):
        self.basetopic = mqtt["basetopic"]
        self.client = self.connectmqtt(mqtt)
        self.mqtt = mqtt
        self.keys = {i.name: i.value for i in panasonic_viera.Keys}
        self.rc = None
    #def __init__(self,  mqtt):

    def connectmqtt(self,mqtt):
        
        client = paho.Client("vieramqtt-" + socket.gethostname(), clean_session=True)
        if not mqtt["user"] is None and not mqtt["user"] == '':
            client.username_pw_set(mqtt["user"], mqtt["password"])
        client.on_connect = self.mqtt_on_connect
        client.on_disconnect = self.mqtt_on_disconnect
        client.message_callback_add(mqtt["basetopic"] +"/command/+",self.mqtt_on_message)
        
        _LOGGER.info("MQTT Connect: Connecting to {}:{}".format(mqtt['host'],mqtt['port']))
        client.connect(mqtt['host'],mqtt['port'])
        client.will_set(self.basetopic +"/$online",False,qos=0,retain=True)
        return client
    #def connectmqtt(mqtt):

    def mqttstart(self):
        if self.client is not None:
            self.client.loop_start()

    def mqttloop(self):
        self.client.loop_forever()

    def mqtt_on_connect(self,client, userdata, flags, rc):
        if rc==0:
            _LOGGER.info("Connected to MQTT OK Returned code={0}".format(rc))
            client.connected_flag=True
            client.publish(self.basetopic +"/$online",True,qos=0,retain=True)
            client.publish(self.basetopic +"/$version",version,qos=0,retain=True)

            # subscribe to basetopi/command/<keys>
            client.subscribe(self.basetopic +"/command/+")
            
            
        else:
            _LOGGER.info("MQTT Connect : {0}: Bad mqtt connection Returned code={1}".format("self.Name",rc) )
            self.client.connected_flag=False
        #if rc==0
    #def mqtt_on_connect(client, userdata, flags, rc):

    def mqtt_on_disconnect(self, client, userdata, rc):
        _LOGGER.info("MQTT disconnecting reason  "  +str(rc))
        self.client.connected_flag=False
    #def mqtt_on_disconnect(self, client, userdata, rc):

    def mqtt_on_message(self,client, userdata, msg):

        _LOGGER.info("MQTT Message: message on topic {} with payload {}".format(msg.topic,msg.payload))
        topic = msg.topic.split('/')
        #grab last topic
        key = topic[len(topic)-1]

        if key in self.keys:
            _LOGGER.info("MQTT Message: Sending {} to device".format(key))
            self.rc.send_key(getattr(panasonic_viera.Keys,key))
        elif (key == 'status'):
            _LOGGER.info("MQTT Status: Status message received")
            ret = self.rc.get_device_info()
            _LOGGER.info("MQTT Status: {}".format(str(ret)))
            self.client.publish(self.basetopic + "/status",str(ret))
        elif (key == 'keys'):
            _LOGGER.info("MQTT Keys: %s" %  ','.join(self.keys))
            self.client.publish(self.basetopic + "/status",','.join(self.keys))
        #if key in self.keys:

        _LOGGER.info("MQTT Message: Msg Received: Topic:{} Payload:{}".format(msg.topic,msg.payload))
        
    #def mqtt_on_message(self,client, userdata, msg):

    
    def connecttv(self, tv):
        if 'appid' not in tv or len(tv['appid']) == 0:
            print("Need to get PIN code and authorise")
            # Get pinn
            self.rc = panasonic_viera.RemoteControl(tv['host'])
            _LOGGER.info("ConnectTV: Seding request to auth tv")
            self.rc.request_pin_code()
            client.subscribe(self.basetopic + "/pin")
            client.message_callback_add(self.basetopic +"/pin",mqtt_on_pin_message)
            client.publish(self.basetopic + "/status","Post pin to " + self.basetopic + "/pin")
        else:
            params = {}
            params["app_id"]= tv['appid']
            params["encryption_key"]= tv['enckey']

            _LOGGER.info("Connecting to tv")
            self.rc = panasonic_viera.RemoteControl(host=tv['host'],app_id=tv['appid'],encryption_key=tv['enckey'])
            ret = self.rc.get_device_info()
            _LOGGER.info("MQTT Status: {}".format(str(ret)))
            self.client.publish(self.basetopic + "/status",str(ret))

        

    #def connect(self, host=None,app_id=None,encryption=None):

    def mqtt_on_pin_message(self,client, userdata, msg):
        if msg.payload is not None:
            print(rc.app_id)
            print( rc.enc_key)
            _LOGGER.info("MQTT PIN Message: Received PIN, store in TVAPPID variable  with value: '" + rc.app_id + "' and TVENCRYPTIONLEY with value: '" + rc.enc_key + "'")
            client.publish(self.basetopic + "/status","Store TVAPPID env variable with value: '" + rc.app_id + "' and TVENCRYPTIONLEY with value: '" + rc.enc_key + "'")
            self.rc.authorize_pin_code(pincode=msg.payload)
    #def mqtt_on_pin_message(self,client, userdata, msg):

#class VieraMQTTHandler():

if __name__ == '__main__':
    _LOGGER.info("Loading config")
    mqtt = {}
    mqtt["host"] = os.environ.get('MQTTHOST')
    if 'MQTTPORT' in os.environ:
        mqtt["port"] = int(os.environ.get('MQTTPORT'))
    else:
        mqtt["port"] = 1883
    if 'MQTTBASETOPIC' in os.environ:
        mqtt["basetopic"] = os.environ.get('MQTTBASETOPIC')
    else:
        mqtt["basetopic"] = "viera"
    mqtt["user"] = os.environ.get('MQTTUSER')
    mqtt["password"] = os.environ.get('MQTTPASSWORD')
    tv = {}
    tv["host"] = os.environ.get("TVHOST")
    tv['appid'] = os.environ.get("TVAPPID")
    tv["enckey"] = os.environ.get("TVENCRYPTIONKEY")

    
    viera = VieraMQTTHandler(mqtt)
    viera.mqttstart()
    viera.connecttv(tv)
    while True:
        try:
            viera.mqttloop()
        except:
            _LOGGER.debug("main Loop error")
            pass
    # Make the TV display a pairing pin code
    # We can now start communicating with our TV
    # Send EPG key
    #rc.send_key(panasonic_viera.Keys.home)
#if __name__ == '__main__':
