
##############################################################################
#                       Carro WIFI
#  
#  Copyright 2022 Yosel de Jesus Balibrea Lastre <yosel.balibrea@reduc.edu.cu>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
##################################################################################


import network
import machine
#import html

FREQ = 500

mot_p1 = machine.PWM(machine.Pin(13), freq=FREQ)
mot_p2 = machine.PWM(machine.Pin(12), freq=FREQ)
#fb_dir = machine.Pin(12, machine.Pin.OUT)    #Adelante o Atras
mot_p1.duty(0)
mot_p2.duty(0)


direc = machine.PWM(machine.Pin(14), freq=50)
direc.duty(60)
direc.deinit()

GPIO_NUM = 2 # Builtin led

AP = 0

if AP == 0:
    # Wi-Fi configuration
    STA_SSID = "PiAp"
    STA_PSK = "12345678"

    # Disable AP interface
    ap_if = network.WLAN(network.AP_IF)
    if ap_if.active():
        ap_if.active(False)

    # Connect to Wi-Fi if not connected
    sta_if = network.WLAN(network.STA_IF)
    if not ap_if.active():
        sta_if.active(True)
    if not sta_if.isconnected():
        sta_if.connect(STA_SSID, STA_PSK)
    # Wait for connecting to Wi-Fi
    while not sta_if.isconnected():
        pass

    # Show IP address
    print("Server started @ ", sta_if.ifconfig()[0])
else:
    STA_SSID = "Carro"
    STA_PSK = "micropython"
    
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.active():
        sta_if.active(False)

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)

    if not ap_if.active():
        ap_if.active(True)
        
    print("AP:" + str(ap_if.active()))

    ap_if.config(essid=STA_SSID, authmode=network.AUTH_WPA_WPA2_PSK, password=STA_PSK)

    # Wait for connecting to Wi-Fi
    while not ap_if.isconnected():
        pass
    
    # Show IP address
    print("Server started @ ", ap_if.ifconfig()[0])

#Alowed connections
MAX_CON = 2

# Angulos max y min para el servo
XMAX = 135
XMIN = 45

#Duty cycle motor PWM range (0-1023) 
YMAX = 700
YMIN = -700

car_st = 0

def map_xval(val):
  return int((val*(XMAX - XMIN)/200) + 90)  

def map_yval(val):
  return int(val*(YMAX - YMIN)/200)
  

def rotate(grad):
    ms = grad*2/180
    dc = ms*1023/20
    direc.duty(int(dc))

# Motor is off when p1 and p2 are 00 or 11
def motor(speed):
  dcf = 1023

  if car_st == 1:    # Carro Encendido
    if speed > 0:
      #dcf = 1023 - speed
      dcf = speed
      mot_p1.duty(dcf)
      mot_p2.duty(0)
    elif speed < 0:
      #dcf = 1023 + speed + 300 # speed negativo
      dcf = speed * -1
      mot_p1.duty(dcf)
      mot_p2.duty(0)

  print("DC: " + str(dcf))
  
f = open("index.html", "r")
html = f.read()
f.close()

addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(MAX_CON)

while True:
    conn, addr = s.accept()
    request = conn.recv(1024)
    conn.sendall('HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Type:text/html\r\n\r\n')
    request = str(request)
    #print("==> Content: " + request)
    ix = request.find('X')
    iy = request.find('Y')
    iz = request.find('Z')
    ston = request.find('/?CAR=ON')
    stoff = request.find('/?CAR=OFF')
    if ston > 0:
      car_st = 1
      #print("ON")

    if stoff > 0:
      #mot.duty(0)
      car_st = 0
      #print("OFF")

    #print("ix: " + str(ix))
    #print("iy: " + str(iy))
    if ix > 0:
        #ie = request.find(' ', ix)
        #print(str(request[ix+1:iy]))
        try:
          ValX = int(request[ix+1:iy])
          ValY = int(request[iy+1:iz])
        except:
          ValX = 0
          ValY = 0

        X = map_xval(ValX)
        Y = map_yval(ValY)
        #print("X: " + str(X))
        #print("Y: " + str(Y))

        motor(Y)

        rotate(X)
        
    else:
        conn.sendall(html)
    conn.sendall('\n')
    conn.close()











