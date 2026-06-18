#!/usr/bin/env python3

import asyncio
import time
import lgpio

from telegram import Bot

import meshtastic
import meshtastic.tcp_interface
from pubsub import pub

# =========================
# CONFIG
# =========================

BOT_TOKEN = "XXXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
CHAT_ID = -XXXXXXXXX

MESHTASTIC_HOST = "localhost"

# =========================
# LED CONFIG
# =========================

# RED_LED = 13; GREEN_LED = 6
RED_LED = 13

# Becomes True after first text message
message_received = False

# Open GPIO chip
gpio_handle = lgpio.gpiochip_open(0)

# Configure LED pin as output
lgpio.gpio_claim_output(gpio_handle, RED_LED)

# LED OFF at startup
lgpio.gpio_write(gpio_handle, RED_LED, 0)

# =========================
# TELEGRAM
# =========================

bot = Bot(BOT_TOKEN)

async def send_to_telegram(text):
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=text
        )
    except Exception as e:
        print(f"Telegram send error: {e}")

# =========================
# LED FUNCTIONS
# =========================

def turn_red_led_on():
    lgpio.gpio_write(
        gpio_handle,
        RED_LED,
        1
    )


# =========================
# MESHTASTIC CALLBACK
# =========================

def on_receive(packet, interface):
    global message_received

    try:
        decoded = packet.get("decoded", {})

        # Ignore non-text packets
        if "text" not in decoded:
            return

        # Debug (remove later if desired)
        print(packet)

        # First message received -> turn LED on
        if not message_received:
            turn_red_led_on()
            message_received = True
            print("First message received - RED LED ON")

        message = decoded["text"]

        # Default sender
        sender = packet.get("fromId", "Unknown")

        # Try to resolve human-readable node name
        try:
            node_num = packet.get("from")

            if node_num and node_num in interface.nodesByNum:
                node = interface.nodesByNum[node_num]

                sender = (
                    node.get("user", {}).get("longName")
                    or node.get("user", {}).get("shortName")
                    or sender
                )

        except Exception:
            pass

        # Determine destination type
        if packet.get("pkiEncrypted", False):
            destination = "DM"
        else:
            destination = f"CH{packet.get('channel', 0)}"

        output = f"[{destination}] {sender}: {message}"

        print(output)

        # Save to file
        with open(
            "messages.txt",
            "a",
            encoding="utf-8"
        ) as f:
            f.write(output + "\n")

        # Forward to Telegram
        try:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(send_to_telegram(output))
            finally:
                loop.close()

        except Exception as e:
            print(f"Telegram error: {e}")

    except Exception as e:
        print(f"Packet processing error: {e}")

# =========================
# MAIN
# =========================

print("Starting Meshtastic Telegram Bridge...")
print("Connecting to Meshtastic daemon...")

interface = meshtastic.tcp_interface.TCPInterface(
    MESHTASTIC_HOST
)

print("Connected.")
print("Waiting for messages...")

# Subscribe to text messages
pub.subscribe(
    on_receive,
    "meshtastic.receive.text"
)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    try:
        interface.close()
    except Exception:
        pass

    try:
        # Turn LED OFF
        lgpio.gpio_write(
            gpio_handle,
            RED_LED,
            0
        )

        lgpio.gpiochip_close(
            gpio_handle
        )

    except Exception:
        pass

    print("Disconnected.")

