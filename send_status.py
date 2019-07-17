#!/usr/bin/python3

def get_endpoint(param, SERVER, EMBY_API):
    endpoint = "{}{}?api_key={}".format(SERVER, param, EMBY_API)
    return endpoint


def system_info_item(string, item, SERVER, EMBY_API):
    url = get_endpoint(string, SERVER, EMBY_API)
    response = requests.get(url)
    data = response.json()
    return data[item]


def check_server(SERVER, EMBY_API):
    url = get_endpoint("System/Ping", SERVER, EMBY_API)
    response = requests.post(url)
    data = response.text
    if data == "Emby Server":
        # update.message.reply_text("Your Server is Online")
        return "Your Server is Online"


def system_info():
    system_info_item('System/Info', 'OperatingSystemDisplayName', SERVER, EMBY_API)
    Status = str(check_server(SERVER, EMBY_API))
    Server_Name = system_info_item('System/Info', 'ServerName', SERVER, EMBY_API)
    Local_Address = system_info_item('System/Info', 'LocalAddress', SERVER, EMBY_API)
    WAN_Address = system_info_item('System/Info', 'WanAddress', SERVER, EMBY_API)
    Emby_Version = system_info_item('System/Info', 'Version', SERVER, EMBY_API)
    Update_Available = str(system_info_item('System/Info', 'HasUpdateAvailable', SERVER, EMBY_API))
    Movies = str(system_info_item('Items/Counts', 'MovieCount', SERVER, EMBY_API))
    Series = str(system_info_item('Items/Counts', 'SeriesCount', SERVER, EMBY_API))
    Episodes = str(system_info_item('Items/Counts', 'EpisodeCount', SERVER, EMBY_API))
    Channels = str(system_info_item('LiveTV/Channels', 'TotalRecordCount', SERVER, EMBY_API))
    message = """
    {}
    Server Name: {}
    Local Address: {}
    Remote Address: {}
    Version: {}
    Update Available: {}
    
    Movies: {}
    Series: {}
    Episodes: {}
    Channels: {}
    """.format(Status, Server_Name, Local_Address, WAN_Address, Emby_Version, Update_Available, Movies, Series, Episodes, Channels)
    return message


def send_status():
    text = system_info()
    data = {"chat_id": CHAT, "text": text}
    url = "https://api.telegram.org/bot{}/sendMessage".format(API_TOKEN)
    requests.post(url, data)


if __name__ == '__main__':
    import requests
    from sys import argv

    ######################## CHANGE ME ########################
    API_TOKEN = "111111111111111111111111111"
    CHAT = "11111111"
    SERVER = "https://emby.server.domain/"
    EMBY_API = "AAAAAAAAAAAAAAAA"
    ###########################################################

    if len(argv) == 1:
        send_status()
