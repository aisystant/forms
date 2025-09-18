
# forms

A simple HTTP service for handling website form submissions and forwarding them to a Telegram chat.

## Features
- Accepts POST requests with JSON, form, or multipart data
- Forwards form data and file uploads to a specified Telegram chat
- Supports plain text, JSON, and file payloads
- Deployable via Docker and Nomad

## Requirements
- Python 3.12+
- [Flask](https://flask.palletsprojects.com/)
- [Requests](https://docs.python-requests.org/)

## Environment Variables
- `TELEGRAM_BOT_TOKEN` (required): Telegram bot token for sending messages

## Usage

### Local Development
1. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
2. Set the Telegram bot token:
	```bash
	export TELEGRAM_BOT_TOKEN=your-telegram-bot-token
	```
3. Run the app:
	```bash
	python app.py
	```
	The service will listen on `0.0.0.0:8010`.

### Endpoints
- `GET /` — Health check, returns `ok`.
- `POST /post` — Accepts form submissions. Forwards data and files to Telegram.

#### Example cURL
```bash
curl -X POST http://localhost:8010/post \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "file=@/path/to/file.pdf"
```

## Docker
Build and run the service with Docker:
```bash
docker build -t forms .
docker run -e TELEGRAM_BOT_TOKEN=your-telegram-bot-token -p 8010:8010 forms
```

## Nomad Deployment
See `nomad-job.hcl` for a sample Nomad job spec. The service expects the `TELEGRAM_BOT_TOKEN` to be provided as an environment variable.

## License
MIT
