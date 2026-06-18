#!/usr/bin/env python3

import asyncio
import threading
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

RED_LED = 13 # 13; 6

message_received = False

gpio_handle = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(gpio_handle, RED_LED)

# LED OFF at startup
lgpio.gpio_write(gpio_handle, RED_LED, 0)

# =========================
# TELEGRAM
# =========================

bot = Bot(BOT_TOKEN)

# Create one persistent event loop
telegram_loop = asyncio.new_event_loop()


def telegram_loop_runner():
    asyncio.set_event_loop(telegram_loop)
    telegram_loop.run_forever()


threading.Thread(
    target=telegram_loop_runner,
    daemon=True
).start()


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

        # First text message -> LED ON
        if not message_received:
            turn_red_led_on()
            message_received = True
            print("First message received - RED LED ON")

        message = decoded["text"]

        # Default sender
        sender = packet.get("fromId", "Unknown")

        # Resolve node name if known
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

        # Determine DM vs Channel
        to_id = packet.get("toId", "")

        if to_id.startswith("!"):
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

        # Send to Telegram using persistent event loop
        asyncio.run_coroutine_threadsafe(
            send_to_telegram(output),
            telegram_loop
        )

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

    try:
        telegram_loop.call_soon_threadsafe(
            telegram_loop.stop
        )
    except Exception:
        pass

    print("Disconnected.")
