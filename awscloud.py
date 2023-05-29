
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import json
import ser
import time as t

ENDPOINT = "aguh95oh6a851-ats.iot.us-east-2.amazonaws.com"
CLIENT_ID = "ESP8266SUB"
PATH_TO_CERTIFICATE = "Devicecertificate.pem.crt"
PATH_TO_PRIVATE_KEY = "private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "AmazonRootCA1.pem"
MESSAGE = ser.dats
TOPIC = "esp8266/pub"
RANGE = 20
data=ser.dats

myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

myAWSIoTMQTTClient.connect()
def main():
    for i in range (RANGE):
        data = "{} [{}]".format(MESSAGE, i+1)
        message = {"Sensor data" : data}
        myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1) 
        print("Published: '" + json.dumps(message) + "' to the topic: " + "'esp8266/pub'")
        t.sleep(0.1)
        return "Published: '" + json.dumps(message) + "' to the topic: " + "'esp8266/pub'"
    

#-------------------------------  AWS ---------------------#
while True:
    main()
    t.sleep(3)
    

    