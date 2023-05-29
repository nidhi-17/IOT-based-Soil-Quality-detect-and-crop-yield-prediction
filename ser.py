import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

portlist = []


dict={'Nitrogen':[],'Phosphorous':[],'Potassium':[],'Soil Moisture(in Percentage)':[],'Soil Ph':[]}

for onePort in ports:
    portlist.append(str(onePort))
    print(str(onePort))

val = 3

for x in range(0,len(portlist)):
    if portlist[x].startswith("COM" + str(val)):
        portVar = "COM" + str(val)
        print(portlist[x])

serialInst.baudrate = 9600
serialInst.port = portVar
serialInst.open()

m=10
n=10
while True:
    if serialInst.in_waiting:
        packet = serialInst.readline()
        x=packet.decode('utf')
        data_list = x.split('\033')
        
        for v in data_list:
            a=v.split(":")
            #print(a)
            
            #b=a[1].replace("\r\n","")
            if 'Nitrogen' in v:
                b=a[1].replace("\r\n","")
                if m>=0:
                    dict['Nitrogen'].append(b)
                    m=m-1
                else:
                    break
            elif 'Phosphorous' in v:
                b=a[1].replace("\r\n","")
                if m>=0:
                    dict['Phosphorous'].append(b)
                    m=m-1
                else:
                    break
            elif 'Potassium' in v:
                b=a[1].replace("\r\n","")
                # print(a[1])
                if m>=0:
                    dict['Potassium'].append(b)
                    m=m-1
                else:
                    break
            
            elif 'Soil Ph' in v:
                b=a[1].replace("\r\n","")
                # print(a[1])
                if m>=0:
                    dict['Soil Ph'].append(b)
                    m=m-1
                else:
                    break
            
            elif 'Soil Moisture(in Percentage)' in v:
                #b = v.split(":")
                b=a[1].replace("\r\n","")
                if n>=0:
                    dict['Soil Moisture(in Percentage)'].append(b)
                    n=n-1
                else:
                    break

        
        if m<0 and n<0:
            print("dict",dict)
            break
        

    
dats = []
var1 = dict['Nitrogen'][0]
var2 = dict['Phosphorous'][0]
var3= dict['Potassium'][0]
var4= dict['Soil Moisture(in Percentage)'][0]
var5= dict['Soil Ph'][0]

dats={"Nitrogen":var1,"Phosphorous":var2,"Potassium":var3,"Soil Moisture(in Percentage)":var4,"Soil Ph":var5}
print(dats)
