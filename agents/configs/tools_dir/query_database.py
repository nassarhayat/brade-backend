import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_database_query(user_request: str, database_schemas: str):
  prompt = f"""
  Based on the following database schemas, generate a SQL query to get user requested data: {user_request}:
  
  schemas: {database_schemas}
  
  return format: only return the text for the query, so that it can be run immediately
  """

  response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
          {"role": "system", "content": prompt},
          # {"role": "user", "content": user_question }
      ],
  )

  return response.choices[0].message.content

# get_database_query()