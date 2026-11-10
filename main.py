import json
import os
import struct
import subprocess
import sys
import time
import webbrowser

import pyautogui
import socket
from vosk import Model, KaldiRecognizer

SERIAL_PORT = "COM4"
BAUD_RATE = 921600
MODEL_PATH = r"vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000

MAGIC = b"\xAA\x55"
PACKET_AUDIO = 0x01
PACKET_BUTTON = 0x02
AUDIO_BYTES = 320 * 2

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.12


def notify_board(conn, code):
    try:
        if conn and conn.fileno() != -1:
            conn.sendall(code.encode("ascii"))
    except (OSError, AttributeError):
        pass


def normalize(text):
    return " ".join(text.lower().strip().split())


def process_command(text):
    text = normalize(text)

    if text in (
        "exit voice remote",
        "quit voice remote",
        "stop listening",
        "turn off voice remote",
        "shut down voice remote",
        "exit remote",
        "quit remote"
    ):
        return "QUIT"

    if any(p in text for p in (
        "end presentation",
        "stop presentation",
        "exit presentation"
    )):
        return "END_PRESENTATION"

    if text in (
        "mute",
        "mute sound",
        "mute volume",
        "unmute",
        "unmute sound",
        "turn sound off",
        "turn sound on"
    ) or "mute" in text:
        return "MUTE"

    if any(p in text for p in (
        "volume up",
        "increase volume",
        "turn it up",
        "louder"
    )):
        return "VOLUME_UP"

    if any(p in text for p in (
        "volume down",
        "decrease volume",
        "turn it down",
        "quieter"
    )):
        return "VOLUME_DOWN"

    if any(p in text for p in (
        "open notepad",
        "launch notepad"
    )) or text == "notepad":
        return "NOTEPAD"

    if any(p in text for p in (
        "open calculator",
        "launch calculator",
        "open calc"
    )) or text == "calculator":
        return "CALCULATOR"

    if any(p in text for p in (
        "open file explorer",
        "open explorer",
        "open files"
    )):
        return "EXPLORER"

    if any(p in text for p in (
        "open browser",
        "open google",
        "open internet",
        "open edge"
    )):
        return "BROWSER"

    if any(p in text for p in (
        "next slide",
        "go to next slide",
        "show next slide"
    )) or text == "next":
        return "NEXT"

    if any(p in text for p in (
        "previous slide",
        "go back one slide"
    )):
        return "PREVIOUS"

    if "first slide" in text:
        return "FIRST"

    if "last slide" in text:
        return "LAST"

    if "start presentation" in text or "start slideshow" in text:
        return "START_PRESENTATION"

    if text in ("play", "play media", "resume playback"):
        return "PLAY"

    if text in ("pause", "pause media", "pause playback"):
        return "PAUSE"

    if any(p in text for p in (
        "next track",
        "next song",
        "skip song"
    )):
        return "NEXT_TRACK"

    if any(p in text for p in (
        "previous track",
        "previous song"
    )):
        return "PREVIOUS_TRACK"

    if text in (
        "go home",
        "go to homepage",
        "go to home page"
    ):
        return "GO_HOME"

    if text == "close tab":
        return "CLOSE_TAB"

    if text == "new window":
        return "NEW_WINDOW"

    if text == "close window":
        return "CLOSE_WINDOW"

    return "UNKNOWN"


def execute_command(command, conn):
    if command == "MUTE":
        pyautogui.press("volumemute")

    elif command == "VOLUME_UP":
        for _ in range(3):
            pyautogui.press("volumeup")
            time.sleep(0.04)

    elif command == "VOLUME_DOWN":
        for _ in range(3):
            pyautogui.press("volumedown")
            time.sleep(0.04)

    elif command == "NOTEPAD":
        subprocess.Popen(["notepad.exe"])

    elif command == "CALCULATOR":
        subprocess.Popen(["calc.exe"])

    elif command == "EXPLORER":
        subprocess.Popen(["explorer.exe"])

    elif command == "BROWSER":
        webbrowser.open("https://www.google.com")

    elif command == "NEXT":
        pyautogui.press("right")

    elif command == "PREVIOUS":
        pyautogui.press("left")

    elif command == "FIRST":
        pyautogui.press("home")

    elif command == "LAST":
        pyautogui.press("end")

    elif command == "START_PRESENTATION":
        pyautogui.press("f5")

    elif command == "END_PRESENTATION":
        pyautogui.press("esc")

    elif command in ("PLAY", "PAUSE"):
        pyautogui.press("space")

    elif command == "NEXT_TRACK":
        pyautogui.press("nexttrack")

    elif command == "PREVIOUS_TRACK":
        pyautogui.press("prevtrack")

    elif command == "GO_HOME":
        pyautogui.hotkey("alt", "home")

    elif command == "CLOSE_TAB":
        pyautogui.hotkey("ctrl", "w")

    elif command == "NEW_WINDOW":
        pyautogui.hotkey("win", "e")

    elif command == "CLOSE_WINDOW":
        print("Closing the active window. Save any work first.")
        pyautogui.hotkey("alt", "f4")

    elif command == "UNKNOWN":
        notify_board(conn, "E")
        print("No matching command.")
        return

    notify_board(conn, "D")
    print("Executed:", command)


def handle_button(button_id, talk_state, conn):
    if button_id == 1:
        if talk_state:
            print("\nTALK enabled. Speak a command.")
            notify_board(conn, "L")
        else:
            print("\nTALK paused.")
            notify_board(conn, "I")

    elif button_id == 2:
        print(
            "\nVOICE COMMANDS:"
            "\nVolume up"
            "\nVolume down"
            "\nMute"
            "\nOpen Notepad"
            "\nOpen Calculator"
            "\nOpen File Explorer"
            "\nOpen Browser"
            "\nNext slide"
            "\nPrevious slide"
            "\nFirst slide"
            "\nLast slide"
            "\nStart presentation"
            "\nEnd presentation"
            "\nPlay"
            "\nPause"
            "\nNext track"
            "\nPrevious track"
            "\nGo home"
            "\nClose tab"
            "\nNew window"
            "\nClose window"
            "\nExit voice remote"
        )
        notify_board(conn, "I")

    elif button_id == 3:
        print("\nNEXT button pressed.")
        execute_command("NEXT", conn)

    elif button_id == 4:
        print("\nSELECT button pressed.")
        pyautogui.press("enter")
        notify_board(conn, "D")

    elif button_id == 5:
        print("\nExit button pressed. Stopping Voice Remote.")
        notify_board(conn, "X")
        return False

    return True


def extract_packets(buffer):
    packets = []

    while True:
        start = buffer.find(MAGIC)

        if start < 0:
            if buffer.endswith(MAGIC[:1]):
                return packets, buffer[-1:]
            return packets, b""

        if start > 0:
            buffer = buffer[start:]

        if len(buffer) < 5:
            return packets, buffer

        packet_type = buffer[2]
        length = buffer[3] | (buffer[4] << 8)

        if length > 1024:
            buffer = buffer[1:]
            continue

        total = 5 + length

        if len(buffer) < total:
            return packets, buffer

        payload = buffer[5:total]
        packets.append((packet_type, payload))
        buffer = buffer[total:]

def main():
    if not os.path.isdir(MODEL_PATH):
        print("Vosk model folder not found:", os.path.abspath(MODEL_PATH))
        print("Place the extracted Vosk model folder beside this script.")
        sys.exit(1)

    print("Loading offline Vosk model...")
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.SetWords(False)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", 5000))
        server.listen(1)
        print("\nWi-Fi Voice Remote server started.")
        print("Listening on port 5000...")
        print("Waiting for your ESP32 to connect...")
        conn, address = server.accept()
        print("ESP32 connected from:", address)
        conn.settimeout(0.2)
    except OSError as exc:
        print("Network server error:", exc)
        server.close()
        sys.exit(1)

    buffer = b""
    talk_enabled = False
    running = True
    exit_requested = False

    notify_board(conn, "R")

    print("\nWi-Fi Voice Remote connected.")
    print("Press TALK to enable microphone streaming.")
    print("Press HELP to view commands on the OLED.")
    print("Hold SELECT for about 2 seconds to exit.")
    print("Or say 'exit voice remote' to close the app.")
    print("Vosk recognition works offline.")

    try:
        while running:
            try:
                chunk = conn.recv(4096)
            except socket.timeout:
                continue

            if not chunk:
                print("\nESP32 disconnected.")
                break

            buffer += chunk
            packets, buffer = extract_packets(buffer)

            for packet_type, payload in packets:
                if packet_type == PACKET_BUTTON:
                    if len(payload) >= 2:
                        button_id = payload[0]
                        state = bool(payload[1])

                        print(
                            "Button ID:", button_id,
                            "Talk state:", payload[1]
                        )

                        if button_id == 1:
                            talk_enabled = state
                            recognizer = KaldiRecognizer(model, SAMPLE_RATE)
                            recognizer.SetWords(False)

                        if not handle_button(button_id, state, conn):
                            exit_requested = True
                            running = False
                            break

                elif (
                    packet_type == PACKET_AUDIO
                    and len(payload) == AUDIO_BYTES
                    and talk_enabled
                ):
                    if recognizer.AcceptWaveform(payload):
                        phrase = json.loads(
                            recognizer.Result()
                        ).get("text", "").strip()

                        if phrase:
                            print("\nHeard:", phrase)
                            command = process_command(phrase)
                            print("Command:", command)

                            if command == "QUIT":
                                print("Exiting Voice Remote...")
                                exit_requested = True
                                notify_board(conn, "X")
                                running = False
                                break

                            execute_command(command, conn)

                    else:
                        partial = json.loads(
                            recognizer.PartialResult()
                        ).get("partial", "")

                        if partial:
                            print(
                                "\rListening: " + partial + " " * 10,
                                end="",
                                flush=True
                            )

    except KeyboardInterrupt:
        print("\nStopping Voice Remote...")

    except OSError as exc:
        print("\nWi-Fi connection error:", exc)

    finally:
        notify_board(conn, "X" if exit_requested else "I")
        conn.close()
        server.close()
        print("Voice Remote stopped.")


if __name__ == "__main__":
    main()
