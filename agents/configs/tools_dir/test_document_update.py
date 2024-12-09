import asyncio
import sys
from pathlib import Path
import json
import websockets

# Add the project root to Python path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

async def test_document_update():
    # Test data that matches the expected format
    test_data = {
        '4KjhdEkEWRrzf43DAyzLjauiyyf9': {
            'cells': [
                [{'value': '14'}, {'value': 'Bahamas Dollar'}, {'value': 'BSD'}, {'value': 1.132608}, {'value': '17/12/2021'}] + [{'value': ''}] * 25,
                [{'value': '164'}, {'value': 'Bahamas Dollar'}, {'value': 'BSD'}, {'value': 1.131608}, {'value': '18/12/2021'}] + [{'value': ''}] * 25,
                [{'value': '314'}, {'value': 'Bahamas Dollar'}, {'value': 'BSD'}, {'value': 1.131608}, {'value': '19/12/2021'}] + [{'value': ''}] * 25,
                [{'value': '464'}, {'value': 'Bahamas Dollar'}, {'value': 'BSD'}, {'value': 1.132394}, {'value': '20/12/2021'}] + [{'value': ''}] * 25
            ]
        }
    }

    try:
        # Connect to the WebSocket server
        async with websockets.connect('ws://localhost:3030/api') as websocket:
            # Prepare the update message
            update_message = {
                'type': 'update_document',
                'documentId': '4KjhdEkEWRrzf43DAyzLjauiyyf9',
                'content': test_data['4KjhdEkEWRrzf43DAyzLjauiyyf9']
            }
            
            print("Sending update request...")
            print(json.dumps(update_message, indent=2))
            
            # Send the update request
            await websocket.send(json.dumps(update_message))
            
            # Wait for the response
            response = await websocket.recv()
            response_data = json.loads(response)
            
            print("\nUpdate Response:", response_data)
            
            # Verify the update by getting the document
            verify_message = {
                'type': 'get_document',
                'documentId': '4KjhdEkEWRrzf43DAyzLjauiyyf9'
            }
            
            print("\nVerifying update...")
            await websocket.send(json.dumps(verify_message))
            verify_response = await websocket.recv()
            verify_data = json.loads(verify_response)
            
            # Check if the update was successful
            if verify_data['type'] == 'document' and verify_data['content']:
                print("\nDocument update successful!")
                print("Updated content:", json.dumps(verify_data['content'], indent=2))
            else:
                print("\nFailed to verify document update")
                print("Verification response:", verify_data)
                
    except Exception as e:
        print(f"\nError during document update test: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    await test_document_update()

if __name__ == "__main__":
    asyncio.run(main()) 