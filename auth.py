from fastapi import Depends, HTTPException, Request
import os
from jwt import decode as jwt_decode, PyJWTError
from clerk_backend_api import Clerk
from dotenv import load_dotenv
load_dotenv()

# clerk_config = ClerkConfig(jwks_url="https://pro-corgi-40.clerk.accounts.dev/.well-known/jwks.json")

clerk_key = os.getenv("CLERK_KEY")
s = Clerk(
    bearer_auth=clerk_key,
)
# print("clerk", s)

async def verify_token(request: Request):
  auth_header = request.headers.get("authorization")
  if not auth_header or not auth_header.startswith("Bearer "):
      raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
  
  # Step 2: Extract Token
  token = auth_header.split("Bearer ")[1]
#   print("Token received:", token)

  # Step 3: Decode Token (without verifying signature for now)
  try:
      decoded_token = jwt_decode(token, options={"verify_signature": False})
    #   print("Decoded Token:", decoded_token)
  except PyJWTError as e:
    #   print("Error decoding token:", e)
      raise HTTPException(status_code=401, detail="Invalid token format")

  # Step 4: Extract User ID (sub)
  user_id = decoded_token.get("sub")
  if not user_id:
      raise HTTPException(status_code=401, detail="Missing 'sub' claim in token")

  # Step 5: Verify User with Clerk
  try:
      user = s.users.get(user_id=user_id)
    #   print("User details:", user)
      if not user:
          raise HTTPException(status_code=403, detail="User not found or unauthorized")
  except Exception as e:
    #   print("Error fetching user from Clerk:", e)
      raise HTTPException(status_code=500, detail="Error verifying user")

  return {"user_id": user_id, "user": user}
