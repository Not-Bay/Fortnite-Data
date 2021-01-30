import requests
import datetime
import crayons
import json
import main
import sys

def log(content):

    timestamp = datetime.datetime.now().strftime('%H:%M:%S')

    with open('values.json', 'r', encoding='utf-8') as f:
        values = json.load(f)

    webhook = values['webhook']

    if '--debug' not in sys.argv:

        data = {"content": f"`{timestamp}` {content}"}
        return requests.post(webhook, data=data)


async def create_config(guild):
    guilds = main.db.guilds

    if guilds.find_one(filter={"server_id": guild.id}) != None:
        return False

    newdata = {
        "server_id": guild.id,
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
    try:
        guilds.insert_one(newdata)
    except Exception as e:
        main.log.critical(f'Could not create initial configuration for "{guild.id}": {e}')

    return True

async def delete_config(guild):
    guilds = main.db.guilds
    try:
        guilds.find_one_and_delete(filter={"server_id": guild.id})
        return True
    except:
        return False


async def set_config(ctx, config, value):
    guilds = main.db.guilds

    if config == None:
        return

    if value == None:
        return
    
    guilds.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {config: value}})

    return True


def compose_shop_headers(guild):
    servers = main.db.guilds

    server = servers.find_one({"server_id": guild.id})
    
    composed_headers = {}

    if servers[str(guild.id)]["shop_config"]["header"] != '':
        composed_headers["header"] = server["shop_config"]["header"]

    if servers[str(guild.id)]["shop_config"]["subheader"] != '':
        composed_headers["subheader"] = server["shop_config"]["subheader"]
    
    if servers[str(guild.id)]["shop_config"]["footer"] != '':
        composed_headers["footer"] = server["shop_config"]["footer"]

    if servers[str(guild.id)]["shop_config"]["background"] != '':
        composed_headers["background"] = server["shop_config"]["background"]

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