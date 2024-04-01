
import os
import machine

#Setup PINS
LED0 = machine.Pin(12, machine.Pin.OUT)
LED1 = machine.Pin(13, machine.Pin.OUT)
LED0.off()
LED1.on()

try:
  import usocket as socket
except:
  import socket

import network

import esp
esp.osdebug(None)

import gc
gc.collect()



# Wi-Fi configuration
STA_SSID = "PiApB"
STA_PSK = "raspberry"

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

addr = socket.getaddrinfo('0.0.0.0', 880)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)




