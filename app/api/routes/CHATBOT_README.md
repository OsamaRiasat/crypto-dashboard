# Crypto Chatbot API

## Overview

The Crypto Chatbot API provides an AI-powered endpoint for users to ask questions about cryptocurrency topics. The chatbot uses GPT-4 to generate responses about cryptocurrency basics, blockchain technology, trading strategies, portfolio management, DeFi concepts, NFTs, and more.

## Endpoint

```
POST /api/v1/chatbot/
```

## Request Format

```json
{
  "message": "What is cryptocurrency?",
  "user_id": "optional-user-identifier"
}
```

### Parameters

- `message` (required): The user's question or message about cryptocurrency
- `user_id` (optional): An identifier for the user, useful for tracking conversations

## Response Format

```json
{
  "response": "Cryptocurrency is a digital or virtual currency that uses cryptography for security and operates on decentralized networks based on blockchain technology..."
}
```

## Example Usage

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Bitcoin?"}'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chatbot/",
    json={"message": "How do I create a crypto portfolio?"}
)

print(response.json())
```

## Features

- **AI-Powered Responses**: All responses are generated using OpenAI's GPT-4 model
- **Cryptocurrency Knowledge**: The chatbot can answer questions on a wide range of crypto topics
- **Educational Focus**: Designed to provide informative, educational content about blockchain and cryptocurrency
- **No Hardcoded Answers**: Dynamic responses tailored to each specific question

## Implementation Details

The chatbot uses a specialized prompt (defined in `chatbot_prompt.py`) to guide the GPT-4 model in generating helpful, accurate, and educational responses about cryptocurrency topics. The prompt ensures the model provides informative content while avoiding investment advice.

## Requirements

- OpenAI API key must be set in the environment variables
- Internet connection for API calls to OpenAI

## Error Handling

If the OpenAI API is unavailable or returns an error, the chatbot will respond with a friendly error message asking the user to try again later.