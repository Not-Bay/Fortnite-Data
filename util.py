import traceback
import asyncio
import discord
import logging
import pymongo
import aiohttp
import time
import json
import sys

###
## Some global variables
###

debug = True if '--debug' in sys.argv else False

version = 'dev-4.0'

log = None

configuration = None
database = None
ready = False
languages = []
fortniteapi = None

on_ready_count = 0
start_time = time.time()

###
## Needed for start
###

def get_prefix(bot, message):
    if isinstance(message.channel, discord.DMChannel):
        return configuration.get('default_prefix')
    else:
        server = database.guilds.find_one({'server_id': message.guild.id})
        if server == None:
            return configuration.get('default_prefix')
        else:
            return server.get('prefix')


def get_config():

    log.debug('Loading config.json file...')

    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            log.debug('Loaded.')
            return json.load(f)
    except:
        log.debug('Failed while loading config.json file, trying with "utf-8-sig" encoding...')
        try:
            with open('config.json', 'r', encoding='utf-8-sig') as f:
                log.debug('Loaded.')
                return json.load(f)
        except:
            
            log.critical(f'Failed while trying to load "config.json" file. Traceback:\n{traceback.format_exc()}')
            sys.exit(1)

def get_mongoclient():

    log.debug('Connecting to MongoDB cluster...')

    connection_string = configuration.get('database_connection_str')

    client = pymongo.MongoClient(connection_string)

    try:
        client.server_info()
        log.debug('Connected.')
        return client
    except Exception as e:
        log.critical(f'Failed while connecting to database. Traceback:\n{traceback.format_exc()}')
        sys.exit(1)

async def wait_cache_load():

    while True:
        if fortniteapi._loaded_all == False:
            await asyncio.sleep(0.5)
        else:
            return True


###
## Database Functions
###

# Servers
def database_get_server(guild: discord.Guild):

    data = database.guilds.find_one({'server_id': guild.id})
    return data

def database_store_server(guild: discord.Guild):

    log.debug('Inserting guild into database...')

    check = database.guilds.find_one({'server_id': guild.id})

    if check == None:

        data = {
            "server_id": guild.id,
            "prefix": configuration.get('default_prefix'),
            "language": "en",
            "search_language": "en",
            "shop_channel": {
                "enabled": False,
                "channel": None,
                "webhook": None,
                "webhook_id": None
            },
            "updates_channel": {
                "enabled": False,
                "channel": None,
                "webhook": None,
                "webhook_id": None,
                "config": {
                    "cosmetics": True,
                    "playlists": True,
                    "news": True,
                    "aes": True
                }
            }
        }
        insert = database.guilds.insert_one(data)

        if isinstance(insert, pymongo.results.InsertOneResult):
            log.debug(f'Inserted guild into database. Id: {insert.inserted_id}')
            return insert
        else:
            log.error(f'Failed database insertion of guild {guild.id}')
            return None
    
    else:

        log.debug('Guild is already in database. Returning existing')
        return check

def database_remove_server(guild: discord.Guild):

    log.debug(f'Removing guild "{guild.id}" from database...')

    delete = database.guilds.delete_one({'server_id': guild.id})

    if isinstance(delete, pymongo.results.DeleteResult):

        log.debug(f'Guild "{guild.id}" removed successfully.')
        return delete

    else:
        log.error(f'Failed database delete of guild {guild.id}')
        return None


def database_update_server(guild: discord.Guild, changes: dict):

    log.debug(f'Updating guild "{guild.id}" data. Changes: "{changes}"')

    update = database.guilds.update_one({'server_id': guild.id}, changes)

    if isinstance(update, pymongo.results.UpdateResult):

        log.debug(f'Updated guild "{guild.id}" data successfully.')
        return update

    else:
        log.error(f'Failed guild "{guild.id}" data update.')
        return None

###
## Language Stuff
###


###
## API
###

class FortniteAPI:

    def __init__(self):

        self.ClientSession = aiohttp.ClientSession
        self.headers = {
            'x-api-key': configuration.get('fortnite-api-key')
        }

        self._loaded_all = False
        
        self.all_cosmetics = []

        self.outfits = []
        self.emotes = []
        self.backpacks = []
        self.pickaxes = []
        self.wraps = []
        self.contrails = []
        self.loadingscreens = []
        self.sprays = []
        self.gliders = []


    async def _load_cosmetics(self):

        log.debug('Updating cosmetic cache...')

        if debug == False:
            async with self.ClientSession() as session:
                
                response = await session.get('https://fortnite-api.com/v2/cosmetics/br', headers=self.headers)

                if response.status != 200:
                    data = None
                else:
                    data = await response.json()

                if data == None:
                    log.warning('Something was wrong with cosmetics API. Using cached cosmetics')
                    data = json.load(open('cache/cosmetics.json', 'r', encoding='utf-8'))

        else:
            log.debug('Debug is enabled, loading from cache...')
            data = json.load(open('cache/cosmetics.json', 'r', encoding='utf-8'))


        for cosmetic in data['data']:

            if cosmetic not in self.all_cosmetics:
                self.all_cosmetics.append(cosmetic)

            if cosmetic['type']['value'] == 'outfit':
                if cosmetic not in self.outfits:
                    self.outfits.append(cosmetic)
                    continue

            if cosmetic['type']['value'] == 'emote':
                if cosmetic not in self.emotes:
                    self.emotes.append(cosmetic)
                    continue

            if cosmetic['type']['value'] == 'backpack':
                if cosmetic not in self.backpacks:
                    self.backpacks.append(cosmetic)
                    continue
            
            if cosmetic['type']['value'] == 'pickaxe':
                if cosmetic not in self.pickaxes:
                    self.pickaxes.append(cosmetic)
                    continue

            if cosmetic['type']['value'] == 'wrap':
                if cosmetic not in self.wraps:
                    self.wraps.append(cosmetic)
                    continue

            if cosmetic['type']['value'] == 'contrail':
                if cosmetic not in self.contrails:
                    self.contrails.append(cosmetic)
                    continue

            if cosmetic['type']['value'] == 'loadingscreen':
                if cosmetic not in self.loadingscreens:
                    self.loadingscreens.append(cosmetic)
                    continue

            if cosmetic['type']['value'] == 'spray':
                if cosmetic not in self.sprays:
                    self.sprays.append(cosmetic)
                    continue

            if cosmetic['type']['value'] == 'glider':
                if cosmetic not in self.gliders:
                    self.gliders.append(cosmetic)
                    continue
                

        with open('cache/cosmetics.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self._loaded_all = True

        log.debug(f'Updated cosmetic cache. Loaded {len(self.all_cosmetics)} cosmetics.')

        return self.all_cosmetics

        
    async def get_cosmetic(self, query: str, **kwargs):

        cosmetic_type = kwargs.get('cosmetic_type', None)

        if len(self.all_cosmetics) == 0:
            self._load_cosmetics()

        list_to_search = None

        if cosmetic_type != None:

            if cosmetic_type == 'outfit':
                list_to_search = self.outfits
            elif cosmetic_type == 'emote':
                list_to_search = self.emotes
            elif cosmetic_type == 'backpack':
                list_to_search = self.backpacks
            elif cosmetic_type == 'pickaxe':
                list_to_search = self.pickaxes
            elif cosmetic_type == 'wrap':
                list_to_search = self.wraps
            elif cosmetic_type == 'contrail':
                list_to_search = self.contrails
            elif cosmetic_type == 'loadingscreen':
                list_to_search = self.loadingscreens
            elif cosmetic_type == 'spray':
                list_to_search = self.sprays
            elif cosmetic_type == 'glider':
                list_to_search = self.gliders
            else:
                list_to_search = self.all_cosmetics
                log.debug(f'[FortniteAPI] Unknown cosmetic type "{cosmetic_type}". Searching in "all_cosmetics" list')

        else:

            list_to_search = self.all_cosmetics

        results = []
        is_id = query.lower().startswith(('cid_', 'bid_', 'pickaxe_', 'eid_', 'musicpack_', 'spid_', 'lsid_', 'wrap_', 'glider_'))

        for item in list_to_search:

            if is_id:
                if item['id'].lower().startswith(query.lower()):
                    results.append(item)
            else:
                if item['name'].lower().startswith(query.lower()):
                    results.append(item)

        return results

    async def get_new_items(self, language='en'):

        async with self.ClientSession() as session:
                
            response = await session.get(f'https://fortnite-api.com/v2/cosmetics/br/new?lang={language}', headers=self.headers)

            if response.status != 200:
                return False
            else:
                return await response.json()

    async def get_news(self, language='en'):

        async with self.ClientSession() as session:

            response = await session.get(f'https://fortnite-api.com/v2/news?lang={language}', headers=self.headers)

            if response.status != 200:
                return False
            else:
                return await response.json()

    async def get_aes(self, keyformat='hex'):

        async with self.ClientSession() as session:

            response = await session.get(f'https://fortnite-api.com/v2/aes?keyFormat={keyformat}', headers=self.headers)

            if response.status != 200:
                return False
            else:
                return await response.json()

    async def get_stats(self, account_name=None, account_type='epic'):

        async with self.ClientSession() as session:

            response = await session.get(f'https://fortnite-api.com/v2/stats/br/v2?name={account_name}&accountType={account_type}&image=all', headers=self.headers)

            return await response.json()

    async def get_cc(self, code=None):

        async with self.ClientSession() as session:

            response = await session.get(f'https://fortnite-api.com/v2/creatorcode/search?name={code}', headers=self.headers)

            if response.status != 200:
                return False
            else:
                return await response.json()


def get_color_by_rarity(value):
    
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

###
## Other
###

def get_commands(bot):

    return list(bot.commands)