from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
# import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError
import asyncio
from clerk_backend_api import Clerk

from fastapi import Depends
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


clerk_config = ClerkConfig(jwks_url="https://pro-corgi-40.clerk.accounts.dev/.well-known/jwks.json")
clerk_auth_guard = ClerkHTTPBearer(config=clerk_config)


# async def read_root(credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
#     return JSONResponse(content=jsonable_encoder(credentials))

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
s = Clerk(
    bearer_auth="sk_test_ldJiADURoHaujfpIiIGMhHuVo2FlGEltatM64Cfkzz",
)
print("clerk", s)

async def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
#   print(credentials, "credentials")
  try:
      res = s.users.get(user_id=credentials.decoded['sub'])
      if res is not None:
          # Optionally print or log user details
        #   print('User details:', res)
          return res  # Return the user details directly
      else:
          raise HTTPException(status_code=401, detail="User not found")
  except Exception as e:
      print("Error verifying token:", e)
      raise HTTPException(status_code=401, detail="Invalid token")
  # print(credentials, "credentials")
  # res = s.users.get(user_id=credentials.decoded['sub'])
  # if res is not None:
  #   print('res', res)
  #   pass
  # return JSONResponse(content=jsonable_encoder(credentials))
  # decoded = jwt.decode(token, options={"verify_signature": False})
  # print('dec', decoded)
  # print('token', token)
  # try:
  #   # res = s.clients.verify(request={
  #   #   "token": token,
  #   # })
  #   res = s.users.get(user_id='user_2oXbkWwjR1Kyzu9TH2SCSm3pc2f')
  #   if res is not None:
  #       print('res', res)
  #       # handle response
  #       pass
  #   # payload = jwt.decode(
  #   #   token, 
  #   #   key='', 
  #   #   algorithms=['RS256']
  #   # )
  #   # return payload
  # except InvalidTokenError:
  #   raise HTTPException(status_code=401, detail="Invalid token")
