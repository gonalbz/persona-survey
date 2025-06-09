import socketio
import asyncio
from datetime import datetime

# Initialize the Socket.IO client
sio = socketio.AsyncClient(logger=True, engineio_logger=True)

# API endpoint
API_URL = "http://localhost:8000"

# Global flag for completion
survey_complete = False

@sio.event
async def connect():
    print("Connected to server!")

@sio.event
async def disconnect():
    print("Disconnected from server!")

@sio.event
async def processing_started(data):
    print("\n" + data['message'])

@sio.event
async def survey_completed(data):
    """Handle completed survey results."""
    global survey_complete
    
    if data['status'] == 'success':
        responses = data['responses']
        print(f"\nResults received! Got {len(responses)} responses.")
        print("\nSample responses:")
        for response in responses[:2]:  # Show first 2 responses
            print(f"\nPersona: {response['persona']}")
            print(f"Response: {response['response'][:150]}...")
    
    survey_complete = True

@sio.event
async def survey_error(data):
    """Handle error messages from the server."""
    global survey_complete
    print(f"\nError: {data['message']}")
    survey_complete = True

async def run_survey(question: str, num_personas: int = 5):
    """Run a survey and wait for results."""
    global survey_complete
    survey_complete = False
    
    try:
        print("Connecting to server...")
        await sio.connect(API_URL)
        print("Connected! Submitting survey...")
        
        # Submit the survey
        await sio.emit('submit_survey', {
            'question': question,
            'num_personas': num_personas
        })
        
        # Wait for completion or timeout
        timeout = datetime.now().timestamp() + 300  # 5 minute timeout
        while not survey_complete and datetime.now().timestamp() < timeout:
            await asyncio.sleep(1)
            
        if not survey_complete:
            print("\nTimeout waiting for results!")
            
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if sio.connected:
            await sio.disconnect()

async def main():
    # Example survey question
    question = "You think hotdog is a sandwich answer YES or NO?"
    await run_survey(question, num_personas=5)

if __name__ == "__main__":
    asyncio.run(main()) 