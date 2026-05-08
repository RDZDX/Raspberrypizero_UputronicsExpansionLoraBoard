Create apt source for beta meshtasticd

echo "deb http://download.opensuse.org/repositories/network:/Meshtastic:/beta/Raspbian_12/ /" | sudo tee /etc/apt/sources.list.d/meshtastic.list

curl -fsSL https://download.opensuse.org/repositories/network:Meshtastic:beta/Raspbian_12/Release.key | \
gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/meshtastic.gpg > /dev/null

Or for alpha  meshtasticd

echo "deb http://download.opensuse.org/repositories/network:/Meshtastic:/alpha/Raspbian_12/ /" | sudo tee /etc/apt/sources.list.d/meshtastic.list

curl -fsSL https://download.opensuse.org/repositories/network:Meshtastic:alpha/Raspbian_12/Release.key | \
gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/meshtastic.gpg > /dev/null

sudo apt-get update
sudo apt-get install meshtasticd

sudo raspi-config
From menu enable SPI

Edit: /boot/firmware/config.txt and add on end
[all]
enable_uart=1
dtoverlay=spi0-2cs

Create config file: /etc/meshtasticd/config.d/Uputronics-rfm95_CE1.yaml

Lora:
  Module: RF95
  IRQ: 16               # CE0=25; CE1=16
  spidev: spidev0.1     # CE0=spidev0.0; CE1=spidev0.1

Edit /etc/meshtasticd/config.yaml and change this settings

Lora:
  # Default to auto-detecting the module type
  # This will be overridden by configs from config.d
#  Module: auto

Webserver:
  Port: 9443 # Port for Webserver & Webservices
  RootPath: /usr/share/meshtasticd/web # Root Dir of WebServer
  SSLKey: /etc/meshtasticd/ssl/private_key.pem # Path to SSL Key, generated if not present
  SSLCert: /etc/meshtasticd/ssl/certificate.pem # Path to SSL Certificate, generated if not present

Launch webbrowser: https://192.168.X.X:9443

Change settings on web interface:
Menu: Config->Lora->Region=EU_898; Transmit Power=20

restart raspberrypi