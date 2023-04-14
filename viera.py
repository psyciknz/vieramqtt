import logging
from dotenv import load_dotenv
import os
import panasonic_viera            # pip install panasonic_viera, aiohttp
import paho.mqtt.client as paho   # pip install paho-mqtt
import socket 

load_dotenv()
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

    def __init__(self,  mqtt, tv):
        self.basetopic = mqtt["basetopic"]
        self.client = self.connectmqtt(mqtt)
        self.tv = tv
        self.mqtt = mqtt
    #def __init__(self,  mqtt):

    def connectmqtt(self,mqtt):
        
        client = paho.Client("vieramqtt-" + socket.gethostname(), clean_session=True)
        if not mqtt["user"] is None and not mqtt["user"] == '':
            client.username_pw_set(mqtt["user"], mqtt["password"])
        client.on_connect = self.mqtt_on_connect
        client.on_disconnect = self.mqtt_on_disconnect
        client.message_callback_add(mqtt["basetopic"] +"/+/alerts",self.mqtt_on_message)
        
        client.will_set(self.basetopic +"/$online",False,qos=0,retain=True)
        return client
    #def connectmqtt(mqtt):


    def mqtt_on_connect(client, userdata, flags, rc):
        if rc==0:
            _LOGGER.info("Connected to MQTT OK Returned code={0}".format(rc))
            client.connected_flag=True
            client.publish(self.basetopic +"/$online",True,qos=0,retain=True)
            client.publish(self.basetopic +"/$version",version,qos=0,retain=True)

            client.subscribe(basetopic +"/+/picture")
            client.subscribe(basetopic +"/+/alerts")

            connecttv(tv)

            #self.client.subscribe("CameraEventsPy/alerts")
            
        else:
            _LOGGER.info("Camera : {0}: Bad mqtt connection Returned code={1}".format("self.Name",rc) )
            self.client.connected_flag=False
        #if rc==0
    #def mqtt_on_connect(client, userdata, flags, rc):

    def mqtt_on_disconnect(self, client, userdata, rc):
        logging.info("disconnecting reason  "  +str(rc))
        self.client.connected_flag=False
    #def mqtt_on_disconnect(self, client, userdata, rc):

    def mqtt_on_message(self,client, userdata, msg):
        if msg.payload.decode("utf-8").lower() == 'on' or msg.payload.decode("utf-8").lower() == 'true':
            newState = True
        else:
            newState = False

        deviceName = msg.topic.split('/')[1]
        _LOGGER.info("Camera: {0}: Msg Received: Topic:{1} Payload:{2}".format(deviceName,msg.topic,msg.payload))
        for device in self.Devices:
            #channel = self.Devices[device].channelIsMine("Garage")
            if device.Name == deviceName:
                device.alerts = newState
                _LOGGER.info("Turning Alerts {0}".format( newState))
                self.client.publish(self.basetopic +"/" + device.Name + "/alerts/state",msg.payload,qos=0,retain=True)
    #def mqtt_on_message(self,client, userdata, msg):

    def connecttv(self, tv):
        if 'appid' not in tv:
            print("Need to get PIN code and authorise")
            # Get pinn
            self.rc = panasonic_viera.RemoteControl(host)
            rc.request_pin_code()
            client.subscribe(self.basetopic + "/ping")
            client.message_callback_add(mqtt["basetopic"] +"/pin",mqtt_on_pin_message)
            client.publish(self.basetopic + "/status","Post pin to " + self.basetopic + "/pin")
            # Interactively ask the user for the pin code
            #print("Asking for code")
            #pin = input("Enter code")
            # Authorize the pin code with the TV
            #print("Authorising")
            #rc.authorize_pin_code(pincode=pin)
            # Display credentials (application ID and encryption key)
            #print("sending result")
            #print(rc.app_id)
            #print( rc.enc_key)
        else:
            params = {}
            params["app_id"]= tv['appid']
            params["encryption_key"]= tv['enckey']

            self.rc = panasonic_viera.RemoteControl(host,**params)

        return rc
    #def connect(self, host=None,app_id=None,encryption=None):

    def mqtt_on_pin_message(self,client, userdata, msg):
        if msg.payload is not None:
            print(rc.app_id)
            print( rc.enc_key)
            client.publish(self.basetopic + "/status","Store TVAPPID env variable with value: '" + rc.app_id + "' and TVENCRYPTIONLEY with value: '" + rc.enc_key + "'")
            self.rc.authorize_pin_code(pincode=msg.payload)
    #def mqtt_on_pin_message(self,client, userdata, msg):

#class VieraMQTTHandler():

if __name__ == '__main__':
    _LOGGER.info("Loading config")
    mqtt = {}
    mqtt["host"] = os.environ.get('MQTTHOST')
    mqtt["port"] = os.environ.get('MQTTPORT')
    if 'MQTTBASETOPIC' in os.environ:
        mqtt["basetopic"] = os.environ.get('MQTTBASETOPIC')
    else:
        mqtt["basetopic"] = "viera"
    mqtt["user"] = os.environ.get('MQTTUSER')
    mqtt["password"] = os.environ.get('MQTTPASSWORD')
    tv = {}
    tv["host"] = os.environ.get("TVHOST")
    tv['appid'] = os.environ.get("TVAPPID")
    tv["enckey"] = os.environ.get("TVENCRYPTIONLEY")


    viera = VieraMQTTHandler(mqtt,tv)

    # Make the TV display a pairing pin code
    # We can now start communicating with our TV
    # Send EPG key
    #rc.send_key(panasonic_viera.Keys.home)
#if __name__ == '__main__':
