
import requests
from discord.utils import escape_markdown

class SteamServer():
    def __init__(self, data):
        self.name = data.get('name', None)
        self.address = data.get('addr', None)
        self.players = data.get('players', None)
        self.maxPlayers = data.get('max_players', None)
        self.map = data.get('map', None)

    def __str__(self):
        return ('```%s <steam://connect/%s>\n	%s (%s / %s)```' % (escape_markdown(self.name), self.address, self.map, self.players, self.maxPlayers))

class SteamServerBrowser():
    def __init__(self, apiKey, appID):
        self.apiKey = apiKey
        self.appID = appID

    def get(self, limit=30):
        result = requests.get('https://api.steampowered.com/IGameServersService/GetServerList/v1/?key=%s&limit=%s&filter=appid\%s' % (self.apiKey, limit, self.appID))

        if result.status_code != 200:
            return []

        try:
            result = result.json()
            return sorted([SteamServer(server) for server in result['response']['servers']], key=lambda x: x.players, reverse=True)
        except:
            return []
