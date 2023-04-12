import panasonic_viera            # pip install panasonic_viera, aiohttp
import paho.mqtt.client as paho   # pip install paho-mqtt

from dotenv import load_dotenv

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


def connecttv(self, host=None,app_id=None,encryption=None):
    if app_id is None:
        print("Need to get PIN code and authorise")
        # Get pinn
        #rc.request_pin_code()
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
        params["app_id"]= os.environ.get("APP_ID")
        params["encryption_key"]= os.environ.get("ENCRYPTION_KEY")

        rc = panasonic_viera.RemoteControl(host,**params)

    return rc
#def connect(self, host=None,app_id=None,encryption=None):

class VieraMQTTHandler():

    def __init__(self,  mqtt):
        self.basetopic = mqtt["basetopic"]
        self.client = self.connectmqtt((mqtt)
    #def __init__(self,  mqtt):

    def connectmqtt(mqtt):
        client = paho.Client("vieramqtt-" + socket.gethostname(), clean_session=True)
        if not mqtt["user"] is None and not mqtt["user"] == '':
            client.username_pw_set(mqtt["user"], mqtt["password"])
        client.on_connect = mqtt_on_connect
        client.on_disconnect = mqtt_on_disconnect
        client.message_callback_add(mqtt["basetopic"] +"/+/alerts",mqtt_on_message)
        
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

            #self.client.subscribe("CameraEventsPy/alerts")
            
        else:
            _LOGGER.info("Camera : {0}: Bad mqtt connection Returned code={1}".format("self.Name",rc) )
            self.client.connected_flag=False

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

if __name__ == '__main__':
    _LOGGER.info("Loading config")
    mqtt = {}
    mqtt["IP"] = cp.get("MQTT Broker","IP")
    mqtt["port"] = cp.get("MQTT Broker","port")
    mqtt["basetopic"] = cp.get("MQTT Broker","BaseTopic")
    mqtt["user"] = cp.get("MQTT Broker","user",fallback=None)
    mqtt["password"] = cp.get("MQTT Broker","password",fallback=None)
    mqtt["basetopic"] = "vieramqtt"

    viera = VieraMQTTHandler(mqtt)

# Make the TV display a pairing pin code
# We can now start communicating with our TV
# Send EPG key
rc.send_key(panasonic_viera.Keys.home)