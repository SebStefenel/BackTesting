# This gets the API key from a file on my computer, if you wish to use this code, please replace the file path with your own API key
with open("C:\\Users\\sstefenel\\Desktop\\FinnhubAPIkey.txt", "r", encoding="utf-16") as file:
    sstefenel_API_KEY = file.read().strip()

API_KEY = sstefenel_API_KEY 