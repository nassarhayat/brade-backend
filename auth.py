from fastapi import Depends, HTTPException
# import jwt
from jwt import PyJWKClient
from clerk_backend_api import Clerk
from fastapi import Depends
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials

clerk_config = ClerkConfig(jwks_url="https://pro-corgi-40.clerk.accounts.dev/.well-known/jwks.json")
clerk_auth_guard = ClerkHTTPBearer(config=clerk_config)

s = Clerk(
    bearer_auth="sk_test_ldJiADURoHaujfpIiIGMhHuVo2FlGEltatM64Cfkzz",
)
print("clerk", s)

async def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
#   print(credentials, "credentials")
  try:
      res = s.users.get(user_id=credentials.decoded['sub'])
      if res is not None:
        #   print('User details:', res)
          return res  # Return the user details directly
      else:
          raise HTTPException(status_code=401, detail="User not found")
  except Exception as e:
      print("Error verifying token:", e)
      raise HTTPException(status_code=401, detail="Invalid token")
