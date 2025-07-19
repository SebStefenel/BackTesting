import finnhub
from key import API_KEY

finnhub_client = finnhub.Client(api_key=API_KEY)

print(finnhub_client.earnings_calendar(_from="2021-06-10", to="2021-06-30", symbol="AAPL", international=False))
