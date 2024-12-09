import asyncio
import sys
from pathlib import Path
from microsoft_email import MicrosoftEmailTool
import os
from dotenv import load_dotenv

# Add the project root to Python path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

# Load environment variables
load_dotenv()

async def test_microsoft_email():
    try:
        # Get credentials from environment variables
        email = os.getenv('TEST_EMAIL')
        password = os.getenv('TEST_PASSWORD')
        
        if not email or not password:
            print("Error: TEST_EMAIL and TEST_PASSWORD environment variables must be set")
            return
            
        # Initialize the email tool
        email_tool = MicrosoftEmailTool()
        
        print(f"Fetching emails for {email}...")
        
        # Test getting emails
        result = await email_tool.get_emails(email, password, days=7)
        
        if result['status'] == 'success':
            emails = result['data']
            print(f"\nSuccessfully retrieved {len(emails)} emails:")
            
            for email in emails[:5]:  # Show first 5 emails
                print("\n-------------------")
                print(f"Subject: {email.get('subject')}")
                print(f"From: {email.get('from', {}).get('emailAddress', {}).get('address')}")
                print(f"Received: {email.get('receivedDateTime')}")
                print(f"Preview: {email.get('bodyPreview')[:100]}...")
                
        else:
            print("\nFailed to retrieve emails:")
            print(result['message'])
                
    except Exception as e:
        print(f"\nError during email test: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    await test_microsoft_email()

if __name__ == "__main__":
    asyncio.run(main()) 