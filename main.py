import speech_recognition as sr
import pyautogui
import webbrowser

recognizer = sr.Recognizer()
def process_command(text):
    text = text.lower().strip()

    #presentaion commands
    if ("next slide" in text or
        "go to next slide" in text or
        "show next slide" in text or
        text == "next"):
        return "NEXT_SLIDE"
    elif ("previous slide" in text or
          "last slide" in text and "previous" in text or
          "go back one slide" in text):
        return "PREVIOUS_SLIDE"
    elif "first slide" in text:
        return "FIRST_SLIDE"
    elif "last slide" in text:
        return "LAST_SLIDE"
    elif "start presentation" in text:
        return "START_PRESENTATION"
    elif ("end presentation" in text or
          "stop presentation" in text or
          "exit presentation" in text):
        return "END_PRESENTATION"

    #Media commands
    elif text == "play" or "play media" in text:
        return "PLAY"
    elif text == "pause" or "pause media" in text:
        return "PAUSE"
    elif "volume up" in text or "increase volume" in text:
        return "VOLUME_UP"
    elif "volume down" in text or "decrease volume" in text:
        return "VOLUME_DOWN"
    elif "mute" in text or "unmute":
        return "MUTE"
    elif "next track" in text or "next song" in text:
        return "NEXT_TRACK"
    elif "previous track" in text or "previous song" in text:
        return "PREVIOUS_TRACK"

    # System commands
    elif "open browser" in text:
        return "OPEN_BROWSER"
    elif "close tab" in text:
        return "CLOSE_TAB"
    elif "open file" in text or "open document" in text or "open folder" in text:
        return "OPEN_FILE"
    elif "go home" in text or "go to home" in text or "go to homepage" in text:
        return "GO_HOME"
    elif "lock screen" in text or "lock computer" in text or "lock pc" in text or "lock my computer" in text:
        return "LOCK_SCREEN"
    elif "shutdown" in text or "shut down" in text:
        return "SHUTDOWN"

    # TV commands
    elif "power on" in text:
        return "TV_POWER_ON"
    elif "power off" in text:
        return "TV_POWER_OFF"
    elif "tv volume up" in text:
        return "TV_VOLUME_UP"
    elif "tv volume down" in text:
        return "TV_VOLUME_DOWN"
    elif "tv mute" in text:
        return "TV_MUTE"
    elif "channel up" in text:
        return "CHANNEL_UP"
    elif "channel down" in text:
        return "CHANNEL_DOWN"
    elif "input" in text:
        return "TV_INPUT"

    # Navigation commands
    elif "move up" in text:
        return "MOVE_UP"
    elif "move down" in text:
        return "MOVE_DOWN"
    elif "move left" in text:
        return "MOVE_LEFT"
    elif "move right" in text:
        return "MOVE_RIGHT"
    elif "select" in text:
        return "SELECT"
    elif "back" in text:
        return "BACK"
    elif "home" in text:
        return "HOME"
    return "UNKNOWN"


#execution of commands
def execute_command(command):
    #presentaion execution
    if command == "NEXT_SLIDE":
        pyautogui.press("right")
    elif command == "PREVIOUS_SLIDE":
        pyautogui.press("left")
    elif command == "FIRST_SLIDE":
        pyautogui.press("home")
    elif command == "LAST_SLIDE":
        pyautogui.press("end")
    elif command == "START_PRESENTATION":
        pyautogui.press("f5")
    elif command == "END_PRESENTATION":
        pyautogui.press("esc")

    #media execution
    elif command == "PLAY":
        pyautogui.press("space")
    elif command == "PAUSE":
        pyautogui.press("space")
    elif command == "VOLUME_UP":
        pyautogui.press("volumeup")
    elif command == "VOLUME_DOWN":
        pyautogui.press("volumedown")
    elif command == "MUTE":
        pyautogui.press("volumemute")
    elif command == "NEXT_TRACK":
        pyautogui.press("nexttrack")
    elif command == "PREVIOUS_TRACK":
        pyautogui.press("prevtrack")

    #System execution
    elif command == "OPEN_BROWSER":
        webbrowser.open("https://www.google.com")
    elif command == "CLOSE_TAB":
        pyautogui.hotkey("ctrl", "w")
    elif command == "OPEN_FILE":
        pyautogui.hotkey("ctrl", "o")
    elif command == "GO_HOME":
        pyautogui.press("home")
    elif command == "LOCK_SCREEN":
        pyautogui.hotkey("win", "l")
    elif command == "SHUTDOWN":
        pyautogui.hotkey("alt", "f4")

    #TV execution
    elif command == "TV_POWER_ON":
        pyautogui.press("power")    
    elif command == "MOVE_UP":
        pyautogui.press("up")
    elif command == "MOVE_DOWN":
        pyautogui.press("down")
    elif command == "MOVE_LEFT":
        pyautogui.press("left")
    elif command == "MOVE_RIGHT":
        pyautogui.press("right")
    elif command == "SELECT":
        pyautogui.press("enter")
    elif command == "BACK":
        pyautogui.press("esc")
    elif command == "HOME":
        pyautogui.press("home")


print("VOICE REMOTE TEST")
print("Speak a command...")

with sr.Microphone() as source:
    print("Adjusting for background noise...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Listening...")
    audio = recognizer.listen(source)
print("Processing...")

#Speech recognition and command execution
try:
    text = recognizer.recognize_google(audio)
    print()
    print("You said:")
    print(text)

    # Convert speech to command
    command = process_command(text)

    print("Command:")
    print(command)

    # Execute command
    if command != "UNKNOWN":
        execute_command(command)
        print()
        print("Action executed successfully.")
    else:
        print()
        print("Command not recognized.")

except sr.UnknownValueError:
    print("Could not understand the speech.")
except sr.RequestError as e:
    print("Speech recognition service error:", e)