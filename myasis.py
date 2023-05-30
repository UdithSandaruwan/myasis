import speech_recognition as sr
import webbrowser
import pyautogui
import pyttsx3
import openai
import json
from Adafruit_IO import Client, RequestError, Feed

# Set up OpenAI API key and text-to-speech engine
openai.api_key = ''
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Set up speech recognition and microphone
r = sr.Recognizer()
mic = sr.Microphone(device_index=1)

# Set up Adafruit IO credentials
aio_username = 'udith2005'
aio_key = ''
toggle1_feed_name = 'led1'
toggle2_feed_name = 'led2'

# Set up Adafruit IO client
aio = Client(aio_username, aio_key)

# Initialize conversation variables
conversation = ""
user_name = "User"
bot_name = "mesh"

# Start the main loop
while True:
    # Listen for user input
    with mic as source:
        print("\nListening...")
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source)
    print("No longer listening")

    # Recognize user input using Google speech recognition
    try:
        user_input = r.recognize_google(audio)
    except sr.UnknownValueError:
        continue

    # Add user input to the conversation log
    prompt = user_name + ": " + user_input + "\n" + bot_name + ": "
    conversation += prompt

    # Handle specific user inputs
    if "open browser" in user_input.lower():
        webbrowser.open('https://www.google.com')
        response_str = "Opening browser"
    elif "open notepad" in user_input.lower():
        pyautogui.press('win')
        pyautogui.typewrite('notepad')
        pyautogui.press('enter')
        response_str = "Opening notepad"
    elif "open calculator" in user_input.lower():
        pyautogui.press('win')
        pyautogui.typewrite('calculator')
        pyautogui.press('enter')
        response_str = "Opening calculator"
    elif "turn on led" in user_input.lower():
        aio.send_data(toggle1_feed_name, 1)  # Send 1 to turn on the first toggle
        response_str = "Turning on led"
    elif "turn off led" in user_input.lower():
        aio.send_data(toggle1_feed_name, 0)  # Send 0 to turn off the first toggle
        response_str = "Turning off led"
    elif "turn on switch" in user_input.lower():
        aio.send_data(toggle2_feed_name, 1)  # Send 1 to turn on the second toggle
        response_str = "Turning on switch"
    elif "turn off switch" in user_input.lower():
        aio.send_data(toggle2_feed_name, 0)  # Send 0 to turn off the second toggle
        response_str = "Turning off switch"
    elif "exit" in user_input.lower():
        break
    else:
        # Use OpenAI API to generate a response based on the conversation log
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=conversation,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response_str = response["choices"][0]["text"].replace("\n", "")
        response_str = response_str.split(user_name + ":", 1)[0].split(bot_name + ":", 1)[0]

    # Add the response to the conversation log and print it
    conversation += response_str + "\n"
    print(response_str)

    # Use text-to-speech engine to speak the response
    engine.say(response_str)
    engine.runAndWait()
