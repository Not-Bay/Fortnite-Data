import requests
import datetime
import crayons
import json
import main
import sys

def log(content):

    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'{crayons.green(timestamp)} {content}')

    with open('values.json', 'r', encoding='utf-8') as f:
        values = json.load(f)

    webhook = values['webhook']

    if '--debug' not in sys.argv:

        data = {"content": f"`{timestamp}` {content}"}
        return requests.post(webhook, data=data)


def logdebug(content):

    if '--debug' in sys.argv:

        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        print(f'{crayons.green(timestamp)} {crayons.yellow("[DEBUG]", bold=True)} {content}')


async def create_config(guild):
    guilds = main.serverconfig()
    if str(guild.id) in guilds:
        return False
    
    file = 'bservers' if '--debug' in sys.argv else 'servers'

    with open(f'settings/{file}.json', 'r', encoding='utf-8') as f:
        guilds = json.load(f)


    newdata = {
        "prefix": "f!",
        "lang": "en",
        "search_lang": "en",
        "shop_channel": 1,
        "updates_channel": 1,
        "max_results": 5,
        "shop_config": {
            "header": "",
            "subheader": "",
            "footer": "",
            "background": ""
        },
        "updates_config": {
            "playlists": True,
            "cosmetics": True,
            "blogposts": True,
            "news": True,
            "aes": True
            }
        }
    
    guilds[str(guild.id)] = newdata

    with open(f'settings/{file}.json', 'w', encoding='utf-8') as fw:
        json.dump(guilds, fw, indent=4, ensure_ascii=False)

    return True

async def delete_config(guild):
    guilds = main.serverconfig()
    if str(guild.id) not in guilds:
        return False

    del guilds[str(guild.id)]

    file = 'bservers' if '--debug' in sys.argv else 'servers'

    with open(f'settings/{file}.json', 'w', encoding='utf-8') as f:
        json.dump(guilds, f, indent=4, ensure_ascii=False)
    return True



async def set_config(ctx, config, value):
    guilds = main.serverconfig()

    if config == None:
        return

    if value == None:
        return

    file = 'servers' if '--debug' not in sys.argv else 'bservers'
    
    guilds[str(ctx.guild.id)][config] = value

    with open(f'settings/{file}.json', 'w', encoding='utf-8') as f:
        json.dump(guilds, f, indent=4, ensure_ascii=False)
    return True


def compose_shop_headers(guild):
    servers = main.serverconfig()
    
    composed_headers = {}

    if servers[str(guild.id)]["shop_config"]["header"] != '':
        composed_headers["header"] = servers[str(guild.id)]["shop_config"]["header"]

    if servers[str(guild.id)]["shop_config"]["subheader"] != '':
        composed_headers["subheader"] = servers[str(guild.id)]["shop_config"]["subheader"]
    
    if servers[str(guild.id)]["shop_config"]["footer"] != '':
        composed_headers["footer"] = servers[str(guild.id)]["shop_config"]["footer"]

    if servers[str(guild.id)]["shop_config"]["background"] != '':
        composed_headers["background"] = servers[str(guild.id)]["shop_config"]["background"]

    return composed_headers

def rarity_color(value):
    if value == 'legendary':
        return 0xf0b132
    elif value == 'epic':
        return 0x9d4dbb
    elif value == 'rare':
        return 0x0086FF
    elif value == 'uncommon':
        return 0x65b851
    elif value == 'common':
        return 0x575757
    elif value == 'icon':
        return 0x00FFFF
    elif value == 'marvel':
        return 0xED1D24
    elif value == 'shadow':
        return 0x292929
    elif value == 'dc':
        return 0x2b3147
    elif value == 'slurp':
        return 0x09E0F0
    elif value == 'dark':
        return 0xFF00FF
    elif value == 'frozen':
        return 0x93F7F6
    elif value == 'lava':
        return 0xF55F35
    elif value == 'starwars':
        return 0xCCCC00
    elif value == 'gaminglegends':
        return 0x0e004d
    else:
        return 0xffffff