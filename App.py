from flask import Flask,render_template,request,Markup,redirect,url_for,make_response,jsonify,session
import pickle
import requests
import pickle
import numpy as np
import mysql.connector
import pandas as pd
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
from flask_session import Session
import json
import time as t
import ser
from werkzeug.security import check_password_hash, generate_password_hash
from twilio.rest import Client

ENDPOINT = "aguh95oh6a851-ats.iot.us-east-2.amazonaws.com"
CLIENT_ID = "ESP8266SUB"
PATH_TO_CERTIFICATE = "Devicecertificate.pem.crt"
PATH_TO_PRIVATE_KEY = "private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "AmazonRootCA1.pem"
TOPIC = "esp8266/pub"
RANGE = 20
MESSAGE = ser.dats
vals=ser.dats


N=int(vals['Nitrogen'])
P=int(vals['Phosphorous'])
K=int(vals['Potassium'])
PH=float(vals['Soil Ph'])
moist=float(vals['Soil Moisture(in Percentage)'])

#-------------------------------  AWS ---------------------#

track = int(100)
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#app.debug = True
Session(app)
from fertilizer import fertilizer_dic


myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)
myAWSIoTMQTTClient.connect()

def publish():
    for i in range (RANGE):
        data = "{} [{}]".format(MESSAGE, i+1)
        message = {"Sensor data" : data}
        myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1) 
        print("Published: '" + json.dumps(message) + "' to the topic: " + "'esp8266/pub'")
        t.sleep(0.1)
        return "Published: '" + json.dumps(message) + "' to the topic: " + "'esp8266/pub'"
publish()  
def refresh(client, userdata, message):
    global sensordata,maindata,N,P,K,PH,moist
    payload = message.payload.decode("utf-8")
    payload = json.loads(payload)
    sensordata=payload["Sensor data"] 
    N=int(vals['Nitrogen'].replace(' mg/kg',''))
    P=int(vals['Phosphorous'].replace(' mg/kg',''))
    K=int(vals['Potassium'].replace(' mg/kg',''))
    PH=float(vals['Soil Ph'])
    moist=float(vals['Soil Moisture(in Percentage)'])
    print(moist)
    print(type(moist))

#myAWSIoTMQTTClient.subscribe("esp8266/pub", 1,refresh)





db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Nidhi@179",
  database="mydb"
)


crop_recommendation_model_path = 'XGBoost.pkl'
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))

fertilizer_recommendation_model_path = 'Fertilizer_Pred_model.pkl'
with open(fertilizer_recommendation_model_path,'rb') as file:
    fdata=pickle.load(file)
model_loaded = fdata["model"]
le_crop=fdata["le_crop"]
le_f=fdata["le_fertilizer"]

def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key ="9d7cde1f6d07ec55650544be1631307e"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
   
    
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
   
 
    if x["cod"] != "404":
        y = x["main"]
       
        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        
        return temperature, humidity 
    else:
        return None

@app.route('/ret',methods=["GET", "POST"])
def ret():
    dat = {}
    if request.method == 'POST':
        pk = request.get_data().decode('utf-8')
        pk = str(pk)
        pk = pk.replace("&", " ")
        pk = pk.replace("%40", "@")
        pk = pk.replace("=", " ")
        pk = list(pk.split(" "))
        it = iter(pk)
        pk = dict(zip(it, it))
        print(pk)
        if pk.get('e').startswith('@') :
            mycursor = db.cursor()
            no = pk.get('e')
            no = no.replace("@","")
            print(no)
            mycursor.execute("SELECT pass FROM mydb.Farmer WHERE Phone = %s", (no,))
            da = mycursor.fetchone()
            test = generate_password_hash(pk.get('p'))
            if  test and check_password_hash(da[0], pk.get('p')):
                mycursor.execute("SELECT deviceID FROM mydb.Farmer WHERE Phone = %s", (no,))
                da1 = mycursor.fetchone()
                session["name"] = da1[0]
                print(session['name'])
                #return render_template('test.html')
                return jsonify(int(2))
            else :
                return jsonify(int(8))
        else :
            mycursor = db.cursor()
            mycursor.execute("SELECT b_pass FROM mydb.Broker WHERE Email = %s", (pk.get('e'),))
            da = mycursor.fetchone()
            test = generate_password_hash(pk.get('p'))
            if  test and check_password_hash(da[0], pk.get('p')):
                session["name"] = pk.get('e')
                print(session['name'])
                #return render_template('user.html', data=session["name"])
                return jsonify(int(3))
            else :
                return jsonify(int(8))


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout',methods=["GET", "POST"])
def logout():
    print(session['name'])
    session['name'] = None
    return render_template("login.html")

@app.route('/details')
def details():
    dat = {}
    if request.method == 'POST':
        pk = request.get_data().decode('utf-8')
        pk = str(pk)
        pk = pk.replace("&", " ")
        pk = pk.replace("%40", "@")
        pk = pk.replace("=", " ")
        pk = list(pk.split(" "))
        it = iter(pk)
        pk = dict(zip(it, it))
        print(pk)

        if pk.get('id') == 'i' :
            state = pk.get('s')
            city = pk.get('c')
            tog = city+", "+state
            mycursor = db.cursor()
            mycursor.execute("SELECT Fname,Lname,Phone,Address,crops FROM mydb.Farmer WHERE Address = %s AND crops LIKE %s", (tog,pk.get('c'),))
            n1 = mycursor.fetchall()
            return render_template("broker.html", data = n1)
        
@app.route('/user')
def user():
    id = session['name']
    mycursor = db.cursor()
    mycursor.execute("SELECT Fname, Lname, Phone, Address, deviceID, crops FROM mydb.Farmer WHERE deviceID = %s",(id,))
    info2 = mycursor.fetchall()
    return render_template("index.html",data=session['name'], info=list(info2))

@app.route('/Insert',methods=["GET", "POST"])
def d():
    global pointer
    global track
    dat = {}
    if request.method == 'POST':
        pk = request.get_data().decode('utf-8')
        pk = str(pk)
        pk = pk.replace("&", " ")
        pk = pk.replace("%40", "@")
        pk = pk.replace("=", " ")
        pk = list(pk.split(" "))
        it = iter(pk)
        pk = dict(zip(it, it))
        print(pk)

        if pk.get('id') == 'u' :
            mycursor = db.cursor()
            print(pk)
            add = pk.get('address')
            add = add.replace("+", " ")
            add = add.replace("%2C",",")

            crop = pk.get('crop')
            crop = crop.replace("+", " ")
            crop = crop.replace("%2C",",")

            sql = "INSERT INTO mydb.farmer (deviceID, Fname, Lname, pass, crops, Address, Phone) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (pk.get('did'),pk.get('Fname'), pk.get('Lname'), generate_password_hash(pk.get('pass')),crop,add,pk.get('pno'))
            mycursor.execute(sql, val)
            db.commit()

            print(mycursor.rowcount, "record inserted.")

            return redirect(url_for('login'))
        
        else :
            global track
            mycursor = db.cursor()
            add = pk.get('l')
            add = add.replace("+", " ")
            add = add.replace("%2C",",")

            name = pk.get('n')
            name = name.replace("+", " ")
            name = name.replace("%2C",",")
            sql = "INSERT INTO mydb.Broker (bid, bName, loc, Email, Phone, b_pass) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (track, name, add,pk.get('e'),pk.get('p'), generate_password_hash(pk.get('pass')))
            mycursor.execute(sql, val)
            db.commit()
            track = track + 1
            print(mycursor.rowcount, "record inserted.")
            return redirect(url_for('login'))



@app.route('/')
def main():
    publish()
    return render_template("main.html")

@app.route('/fertilize')
def fertilize():
    publish()
    return render_template("fertilizer.html",N=N,P=P,K=K,PH=PH,moist=moist)

@app.route('/crops')
def crops():
    publish()
    return render_template("crop.html",N=N,P=P,K=K,PH=PH)

@app.route('/cropd')
def cropd():
    return render_template("disease.html")

# @app.route('/user')
# def user():
#     return render_template("userb.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/broker')
def broker():
    global connection
    connection=False
    mycursor = db.cursor()
    mycursor.execute("SELECT Fname, Lname, Phone,Address,crops FROM mydb.Farmer")
    upevents = mycursor.fetchall()
    email = session['name']
    mycursor.execute("SELECT bName, Email, Phone, loc FROM mydb.Broker WHERE Email = %s",(email,))
    info1 = mycursor.fetchall()
    return render_template("broker.html",data=session['name'],info=list(info1),upevents=upevents)

@app.route('/farmerconnect')
def farmerconnect():
    return render_template('broker-connect.html')

@app.route("/connect", methods=['POST'])
def connect():
    account_sid = 'AC7c32eff9831fb32212e90e9edf544ca8'
    auth_token = '99a6cb48c770c39087cf1118b29c2c29'
    global connection
    connection=True
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                              from_='+15856562025',
                              body ='We are interested in buying  your crops, let us connect',
                              to ='+919769045889'
                          )
    if message:
        return render_template('broker-connect.html')
        #return redirect(url_for('farmerconnect',connection=connection))
   


#---------------------------------- CROP RECOMMENDATION ---------------------#

@ app.route('/crop-predict', methods=['GET','POST'])
def crop_prediction():
    title = 'Crop Recommendation'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])/10
        rainfall = 90

        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop-result.html', prediction=final_prediction, title=title)

        else:
            return redirect(url_for("try_route"))
        
@app.route("/try_route")
def try_route():
    return render_template("try-again.html")

#---------------------------------- FERTILIZER RECOMMENDATION ---------------------#
@ app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    title = 'Fertilizer Suggestion'

    crop_name = str(request.form['cropname'])
    N = int(request.form['Nitrogen'])
    P = int(request.form['Phosphorous'])
    K = int(request.form['Pottasium'])
    temperature=28
    humidity=50
    moisture=int(float(request.form['soilm']))
    

    

    df = pd.read_csv('Data/Fertilizer Prediction.csv')
    dataframe = pd.read_csv('Data/Fertilizer.csv')
    nr = dataframe[dataframe['Crop'] == crop_name]['N'].iloc[0]
    pr = dataframe[dataframe['Crop'] == crop_name]['P'].iloc[0]
    kr = dataframe[dataframe['Crop'] == crop_name]['K'].iloc[0]

    n = nr - N
    p = pr - P
    k = kr - K
    temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    max_value = temp[max(temp.keys())]
    if max_value == "N":
        if n < 0:
            key = 'NHigh'
        else:
            key = "Nlow"
    elif max_value == "P":
        if p < 0:
            key = 'PHigh'
        else:
            key = "Plow"
    else:
        if k < 0:
            key = 'KHigh'
        else:
            key = "Klow"

    response = Markup(str(fertilizer_dic[key]))
    crop_name=crop_name.capitalize()
    data = np.array([[temperature,humidity,moisture,crop_name,N,P,K]])
    data[:,3]=le_crop.transform(data[:,3])
    b = np.array(data, dtype=int)
    prediction = model_loaded.predict(b)
    prediction=le_f.inverse_transform(prediction)
    return render_template('fertilize-result.html', recommendation=response, title=title,prediction=prediction[0])

#-------------------------------  AWS ---------------------#
@app.route('/data',methods=["GET", "POST"])
def data():
    global maindata
    response = make_response(json.dumps(maindata))
    response.content_type = 'application/json'
    return response

if __name__ == '__main__':
	app.run(debug=False)

