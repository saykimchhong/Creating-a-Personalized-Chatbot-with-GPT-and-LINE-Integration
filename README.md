## LINE Chatbot with OpenAI GPT Integration

This repository contains a Python Flask application that implements a LINE chatbot integrated with OpenAI's GPT API. The chatbot can understand and respond to user messages, including both text and images.

## Features

- **Real-time Chat:** The bot interacts with users in real-time using LINE's messaging API.
- **Text and Image Processing:** The bot can process both text messages and image messages, leveraging GPT's capabilities to understand and respond to both modalities.
- **Contextual Responses:** The bot maintains a chat history to provide contextually relevant responses.
- **Chat History Reset:** The chat history is automatically reset after a specified timeout to prevent stale context from affecting interactions.

## Requirements

- Python 3.x
- Flask
- Gunicorn
- line-bot-sdk
- openai

Install these dependencies using pip:

```bash
pip install flask gunicorn line-bot-sdk openai
```

## Setup

1. **LINE Developer Account:**

   - Create a LINE Developer account at [https://developers.line.biz/](https://developers.line.biz/).
   - Create a new provider and channel.
   - Configure the Messaging API settings.
   - Obtain your LINE access token and save it as `LINE_ACCESS_TOKEN`.

2. **OpenAI API Key:**

   - Sign up for an OpenAI account at [https://openai.com/](https://openai.com/).
   - Create an API key and save it as `OPENAI_API_KEY`.

3. **Environment Variables:**
   - Replace the placeholders within the code with your actual `LINE_ACCESS_TOKEN` and `OPENAI_API_KEY`. Alternatively, set these as environment variables for security:
     ```bash
     export LINE_ACCESS_TOKEN="your_line_access_token"
     export OPENAI_API_KEY="your_openai_api_key"
     ```

## Running the Bot

1. **Start the Flask app:**

   ```bash
   flask run --host=0.0.0.0
   ```

   This will run the bot on your local machine, accessible at `http://127.0.0.1:5000/`.

2. **Use Gunicorn for production:**
   - Install Gunicorn:
     ```bash
     pip install gunicorn
     ```
   - Start the bot using Gunicorn:
     ```bash
     gunicorn --bind 0.0.0.0:5000 app:app
     ```
   - This will run the bot on a specific port (5000 in this case) and make it accessible from other machines on the network.

## Usage

1. Add your LINE bot as a friend on your LINE app.
2. Send text or image messages to the bot.
3. The bot will respond based on your message and the context of the conversation.

## Code Breakdown

- **`app.py`:** This file contains the core code for the Flask application, handling incoming LINE requests and processing them with the GPT API.
  - **`lineaccesstoken`:** Stores the LINE access token.
  - **`line_bot_api`:** Initializes the LINE bot API client.
  - **`messaging_api`:** Initializes the LINE messaging API client.
  - **`client`:** Initializes the OpenAI client.
  - **`chat_history`:** Stores the conversation history.
  - **`reset_history()`:** Resets the chat history after 10 minutes to prevent stale context.
  - **`add_message()`:** Adds a message to the chat history.
  - **`encode_image()`:** Encodes an image as a base64 string.
  - **`save_image_locally()`:** Saves an image received from LINE locally for processing.
  - **`send_message()`:** Sends a message to the GPT API and returns the response.
  - **`/webhook` route:** Handles incoming requests from LINE, extracting events and processing them.
  - **`event_handle()`:** Processes individual LINE events, handling text and image messages.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you have any suggestions, bug fixes, or feature requests.

## License

This project is licensed under the MIT License.
