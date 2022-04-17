import requests
import json

def get_inspire():
  response = requests.get('https://zenquotes.io/api/random/')
  json_inspire_quote = json.loads(response.text)
  quote = json_inspire_quote[0]['q']
  author = json_inspire_quote[0]['a']

  return quote, author
  # try:
  #   image = json_inspire_quote[0]['l']
  #   return quote, author, image
  # except:
  #   return quote, author