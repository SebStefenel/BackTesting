# This gets the API key from a file on my computer, if you wish to use this code, please replace the file path with your own API key
with open("C:\\Users\\sstefenel\\Desktop\\Alpaca.txt", "r", encoding="utf-8") as file:
    lines = file.read().splitlines()

API_KEY = lines[0].split()[0]
Secret = lines[0].split()[1]