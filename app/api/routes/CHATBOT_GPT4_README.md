# Crypto Chatbot with GPT-4 Integration

## Overview

The Crypto Chatbot API now integrates with OpenAI's GPT-4 model to provide intelligent, context-aware responses to cryptocurrency-related questions. The chatbot uses a specialized prompt that guides GPT-4 to provide educational information about cryptocurrency concepts, blockchain technology, trading strategies, and more. The chatbot is designed to only respond to crypto-related queries and will politely decline to answer questions outside this domain.

## Setup

### 1. Install Required Packages

The OpenAI package has been added to the requirements.txt file. Install it with:

```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

Add your OpenAI API key to the .env file:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## How It Works

1. When a user sends a message to the `/api/v1/chatbot/` endpoint, the system attempts to generate a response using GPT-4.

2. If GPT-4 generation is successful (API key is valid and the service is available), the response from GPT-4 is returned to the user.

3. If GPT-4 generation fails (missing API key, service unavailable, etc.), the system returns a friendly error message asking the user to try again later.

## Endpoint

```
POST /api/v1/chatbot/
```

## Request Format

```json
{
  "message": "What is the difference between proof of work and proof of stake?",
  "user_id": "optional-user-identifier"
}
```

## Response Format

```json
{
  "response": "Proof of Work (PoW) and Proof of Stake (PoS) are consensus mechanisms used by blockchain networks to validate transactions..."
}
```

## Example Usage

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/" \
     -H "Content-Type: application/json" \
     -d '{"message": "What are the risks of yield farming in DeFi?"}'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chatbot/",
    json={"message": "How do hardware wallets protect my crypto assets?"}
)

print(response.json())
```

### Non-Crypto Query Example

If you ask a non-crypto related question, the chatbot will politely decline to answer:

```python
response = requests.post(
    "http://localhost:8000/api/v1/chatbot/",
    json={"message": "What's the weather like today?"}
)

# Response will indicate that the chatbot only answers crypto-related questions
```

## Prompt Customization

The GPT-4 model is guided by a specialized prompt defined in `app/api/services/chatbot_prompt.py`. You can modify this prompt to adjust the behavior, knowledge areas, and response style of the chatbot.