# Persona Survey

A  system that simulates realistic personas answering surveys based on unique personality traits to reflect human behavior. This project uses advanced language models to generate authentic, personality-driven responses to survey questions.


## Prerequisites

- Python 3.13 or higher
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/persona-survey.git
cd persona-survey
```

2. Create and activate a virtual environment (recommended):
```bash
uv sync # https://docs.astral.sh/uv/getting-started/installation/
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```


3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Running the API Server

Start the WebSocket-enabled API server:

```bash
python api.py
```

The server will start on `http://localhost:8000`.

### Running Simulations Directly

You can run simulations directly using the Python script:

```bash
python persona_survey.py
```

### Using the Client Example

A client example is provided to demonstrate how to interact with the API:

```bash
python client_example.py
```

## API Documentation

### WebSocket Events

#### Connect
- Event: `connect`
- Description: Establishes WebSocket connection

#### Submit Survey
- Event: `submit_survey`
- Payload:
  ```json
  {
    "question": "Your survey question here",
    "num_personas": 100  // Optional, defaults to 100
  }
  ```

#### Response Events
- `processing_started`: Indicates the survey processing has begun
- `survey_completed`: Contains the survey results
- `survey_error`: Sent if an error occurs during processing

## Project Structure

- `persona_survey.py`: Core simulation logic
- `api.py`: FastAPI and WebSocket server implementation
- `client_example.py`: Example client implementation
- `survey_results.json`: Generated survey responses
- `persona.ipynb`: Jupyter notebook for interactive experimentation

## Dependencies

- datasets: For loading persona data
- langchain & langchain-openai: For AI model integration
- FastAPI & uvicorn: For API server
- python-socketio: For WebSocket support
- python-dotenv: For environment variable management

## License

This project is open source and available under the MIT License.
