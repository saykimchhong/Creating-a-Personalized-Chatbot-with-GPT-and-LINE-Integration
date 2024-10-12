from flask import Flask, request
import json
import threading
from linebot import LineBotApi
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage, PushMessageRequest
from openai import OpenAI
import os
import requests
import tempfile
import base64

# Initialize Flask app
app = Flask(__name__)

# LINE access token
lineaccesstoken = (
    "<Your LINE access token>"  # Replace with your actual LINE access token
)
line_bot_api = LineBotApi(lineaccesstoken)

# Correctly configure MessagingApi client
config = Configuration(access_token=lineaccesstoken)
api_client = ApiClient(configuration=config)
messaging_api = MessagingApi(api_client=api_client)

# OpenAI API key setup
os.environ["OPENAI_API_KEY"] = (
    "<Put your OpenAI API access token here>"  # Replace with your actual OpenAI API key
)
client = OpenAI()

# Initialize the chat history
chat_history = [{"role": "system", "content": "You are a helpful assistant."}]


# Function to reset chat history after 10 minutes
def reset_history():
    global chat_history
    print("Resetting chat history...")
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]


# Function to add messages to the chat history
def add_message(role, content):
    global chat_history
    chat_history.append({"role": role, "content": content})


# Set a timer to reset the chat history after 10 minutes (600 seconds)
reset_timer = threading.Timer(600, reset_history)
reset_timer.start()


# Function to encode image as base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Function to save image locally
def save_image_locally(msg_id):
    # Retrieve the image from LINE using the message ID
    headers = {
        "Authorization": f"Bearer {lineaccesstoken}",
    }
    response = requests.get(
        f"https://api-data.line.me/v2/bot/message/{msg_id}/content", headers=headers
    )
    if response.status_code == 200:
        # Create a temporary file to save the image
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=".jpg"
        )  # Saves as a .jpg image
        with open(temp_file.name, "wb") as f:
            f.write(response.content)
        print(f"Image saved locally at: {temp_file.name}")
        return temp_file.name  # Return the path to the saved file
    else:
        print(f"Failed to retrieve image: {response.status_code} - {response.text}")
        return None


# Function to send a message with text or an image URL to the OpenAI API
def send_message(content, is_image=False):
    if is_image:
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe the image below:"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{content}"},
                },
            ],
        }
    else:
        message = {"role": "user", "content": content}

    # Add the message to the chat history
    add_message(message["role"], message["content"])

    # Request response from the OpenAI API with the current history
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=chat_history, max_tokens=300
    )

    # Parse the assistant's response
    assistant_message = response.choices[0].message.content

    # Add assistant's response to the history
    add_message("assistant", assistant_message)

    return assistant_message


# Flask route to handle incoming requests from LINE
@app.route("/webhook", methods=["POST"])
def callback():
    # Parse the incoming JSON request
    json_line = request.get_json(force=False, cache=False)
    decoded = json.loads(json.dumps(json_line))
    no_event = len(decoded["events"])

    # Iterate over each event and handle it
    for i in range(no_event):
        event = decoded["events"][i]
        event_handle(event)
    return "", 200


# Function to handle events from LINE
def event_handle(event):
    print(event)  # Log the entire event for debugging

    try:
        user_id = event["source"]["userId"]
    except KeyError:
        print("Error: cannot get userId")
        return

    try:
        msg_id = event["message"]["id"]
        msg_type = event["message"]["type"]
    except KeyError:
        print("Error: cannot get message ID and type")
        return

    # Handle text messages
    if msg_type == "text":
        msg = event["message"]["text"]
        print(f"Received text message: {msg}")

        # Send the text message to GPT and get the response
        response = send_message(msg)

        # Send the response back to LINE
        push_message_request = PushMessageRequest(
            to=user_id, messages=[TextMessage(text=response)]
        )
        messaging_api.push_message(push_message_request)

    # Handle image messages
    elif msg_type == "image":
        print(f"Received image message with ID: {msg_id}")

        # Save the image locally
        image_path = save_image_locally(msg_id)

        if image_path:
            # Encode the saved image as base64
            base64_image = encode_image(image_path)

            # Send the encoded image to OpenAI
            description = send_message(base64_image, is_image=True)

            # Send the description back to the user
            push_message_request = PushMessageRequest(
                to=user_id, messages=[TextMessage(text=description)]
            )
            messaging_api.push_message(push_message_request)

    # Log other message types
    else:
        print(f"Received unsupported message type: {msg_type}")


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
