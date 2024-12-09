import os
import requests
from datetime import datetime, timedelta
from msal import ConfidentialClientApplication

class MicrosoftEmailTool:
    def __init__(self):
        self.client_id = os.getenv('MS_CLIENT_ID')
        self.client_secret = os.getenv('MS_CLIENT_SECRET')
        self.tenant_id = os.getenv('MS_TENANT_ID')
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ['https://graph.microsoft.com/.default']
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
    def _get_access_token(self):
        try:
            app = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )
            
            result = app.acquire_token_for_client(scopes=self.scope)
            
            if "error" in result:
                print(f"Error getting token: {result.get('error_description', result.get('error'))}")
                return None
                
            return result.get('access_token')
            
        except Exception as e:
            print(f"Exception in _get_access_token: {str(e)}")
            return None

    async def get_emails(self, email, password, days=7):
        """
        Get emails from the specified Microsoft account
        """
        try:
            access_token = self._get_access_token()
            
            if not access_token:
                return {
                    'status': 'error',
                    'message': 'Failed to obtain access token'
                }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Try to get messages directly
            url = f"{self.graph_url}/users/{email}/messages"
            params = {
                '$select': 'subject,receivedDateTime,from,bodyPreview',
                '$top': 10,  # Start with a small number for testing
                '$orderby': 'receivedDateTime DESC'
            }
            
            print(f"Making request to: {url}")
            response = requests.get(url, headers=headers, params=params)
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            if response.status_code == 200:
                emails = response.json().get('value', [])
                return {
                    'status': 'success',
                    'data': emails
                }
            else:
                error_message = response.text
                print(f"Error response: {error_message}")
                
                # Try to get user information to verify permissions
                user_response = requests.get(
                    f"{self.graph_url}/users/{email}",
                    headers=headers
                )
                print(f"User info response: {user_response.status_code}")
                print(f"User info: {user_response.text}")
                
                return {
                    'status': 'error',
                    'message': f'Failed to fetch emails: {error_message}'
                }
                
        except Exception as e:
            print(f"Exception: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error: {str(e)}'
            } 