from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from typing import Dict
import asyncio
import persona_survey
import os

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

# Create FastAPI app
app = FastAPI(title="Persona Survey API")

# Create ASGIApp for Socket.IO
socket_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app
)

# Configure CORS for the main application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def process_survey(socket_id: str, question: str, num_personas: int):
    """Process a survey request and send updates via WebSocket."""
    try:
        # Notify processing start
        await sio.emit('processing_started', {
            'message': 'Processing your request...'
        }, room=socket_id)
        
        print(f"Starting survey processing for socket {socket_id}")
        print(f"Question: {question}")
        print(f"Number of personas: {num_personas}")
        
        # Run the simulation with a single question
        responses = await persona_survey.run_simulations(
            questions=[question],
            num_personas=num_personas
        )
        
        print(f"Got {len(responses)} responses, attempting to save...")
        
        # Save results to file
        try:
            print("Before calling save_results_async")
            await persona_survey.save_results_async(responses)
            print("After calling save_results_async")
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            print(f"Current directory: {os.getcwd()}")
        
        # Format responses for client
        formatted_responses = []
        for response in responses:
            formatted_responses.append({
                'persona': response['persona'],
                'response': response['response']
            })
        
        print(f"Sending {len(formatted_responses)} responses back to client")
        
        # Send results back
        await sio.emit('survey_completed', {
            'status': 'success',
            'responses': formatted_responses
        }, room=socket_id)
        
    except Exception as e:
        error_msg = f"Error processing survey: {str(e)}"
        print(error_msg)
        await sio.emit('survey_error', {
            'status': 'error',
            'message': error_msg
        }, room=socket_id)

@sio.event
async def connect(sid, environ):
    """Handle new WebSocket connection."""
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    """Handle WebSocket disconnection."""
    print(f"Client disconnected: {sid}")

@sio.event
async def submit_survey(sid, data: Dict):
    """Handle new survey request."""
    try:
        # Extract survey parameters
        question = data.get('question')
        num_personas = int(data.get('num_personas', 100))
        
        if not question:
            raise ValueError("Question is required")
        
        # Process survey
        await process_survey(sid, question, num_personas)
        
    except Exception as e:
        print(f"Error in submit_survey: {str(e)}")
        await sio.emit('survey_error', {
            'status': 'error',
            'message': str(e)
        }, room=sid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        socket_app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 