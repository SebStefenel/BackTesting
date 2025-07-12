import requests
from key import API_KEY

response = requests.get("https://finnhub.io/api/v1/quote", params={
    'symbol': 'AAPL',
    'token': API_KEY
})

print(response.json())