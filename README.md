# vieramqtt

Simple service for connecting to the Panasonic Viera TV.

Utilises the https://github.com/florianholzapfel/panasonic-viera library.

I found that Pansonic TVs could not be connected to unless the service and tv were in the same network.  
Having a TV in a seperate network from home assistant resulted in a 403 error.  This MQTT service runs (via macvlan in the same network as the tv).

## Settings
All settings are via environment variables
```
MQTTHOST=<ip/name of mqtt server>
MQTTPORT=1883
MQTTBASETOPIC=viera
TVHOST=<Ip address of tv>
TVAPPID=<if known>
TVENCRYPTIONKEY=<if known>
```

### Initial connect.
I haven't tested this much, preferring to get on with accepting commands.
But on first connection it will post a message in the log, and to the `viera/status` to post the pin displayed on the screen to `viera/pin`
This should authorise the tv.
If accepted, the TVAPPID ane TVENCRYPTIONKEY will be posted to `viera/status`.
Save it....and good luck.   Having these two env variables is how I'm currently using it.

## MQTT State Topics

#### viera/status
Gives an over all status of the device.  Serial numbers and the like.  not all that intersting.

#### viera/status/power
Power on/off state of the tv.  Should be updated about every 20 seconds.

## MQTT Command Topics

#### viera/command/status
Requires a paylod, which is not used yet.
Request status of the TV - returns on `viera/status`

#### viera/command/power
Requires a paylod, which is not used yet.
Powers on/off the TV.  
Doesn't return a status (yet)

#### viera/command/keys
Sends to `viera/status` all the keys available.  Any of these can be posted to `viera/command/keyname` with a payload on anything 

## HA Configuration

Current Configuration is just a simple MQTT Switch:
```
############################################################
#Pansonic Veira
###########################################################
- platform: mqtt
  name: "Panasonic TV power"
  state_topic: "viera/status/power"
  command_topic: "viera/command/power"
  payload_on: "on"
  payload_off: "on"
  device_class: "switch"
```
This is for Home Assistant 2022.8.6 - I believe with a later version, the MQTT items change.

## TODO:
* Better payloads
* Build out commands/status from command executions
* See if incorporating into the panasonic_viera integration - with communication via mqtt rather than direct would be of interest
* More resilience.  Dont think the mqtt processing and handling is the cleanest
