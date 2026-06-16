#!/usr/bin/env python3

import asyncio
import time
from telegram import Bot

import meshtastic
import meshtastic.tcp_interface
from pubsub import pub


# =========================
# CONFIG
# =========================

BOT_TOKEN = "5xxxxxxx1:AXXXXX-AXXXXXXXXXXXXXXXXXXXXX"
CHAT_ID = -60000001

MESHTASTIC_HOST = "localhost"

# =========================
# TELEGRAM
# =========================

bot = Bot(BOT_TOKEN)


async def send_to_telegram(text):
    await bot.send_message(
        chat_id=CHAT_ID,
        text=text
    )


# =========================
# MESHTASTIC CALLBACK
# =========================

def on_receive(packet, interface):
    try:
        decoded = packet.get("decoded", {})

        # Ignore non-text packets
        if "text" not in decoded:
            return

        message = decoded["text"]
        channel = packet.get("channel", 0)

        # Default sender
        sender = packet.get("fromId", "Unknown")

        # Try to resolve human-readable node name
        try:
            node_num = packet.get("from")

            if node_num:
                node = interface.nodesByNum.get(node_num)

                if node:
                    user = node.get("user", {})
                    sender = (
                        user.get("longName")
                        or user.get("shortName")
                        or sender
                    )
        except Exception:
            pass

        output = f"[Channel {channel}] {sender}: {message}"

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
            asyncio.run(
                send_to_telegram(output)
            )
        except Exception as e:
            print(f"Telegram error: {e}")

    except Exception as e:
        print(f"Packet processing error: {e}")


# =========================
# MAIN
# =========================

print("Connecting to Meshtastic daemon...")

interface = meshtastic.tcp_interface.TCPInterface(
    MESHTASTIC_HOST
)

print("Connected.")

# Text messages only
pub.subscribe(
    on_receive,
    "meshtastic.receive.text"
)

print("Listening for messages...")
print("Press Ctrl+C to stop.")

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

    print("Disconnected.")
