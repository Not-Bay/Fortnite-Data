from urllib.parse import urlencode
from motor import motor_asyncio
from pymongo import results
import traceback
import aiofiles
import logging
import asyncio
import discord
import aiohttp
import time
import json
import sys

###
## Some global variables
###

debug = True if '--debug' in sys.argv else False

version = '4.1.1'

log = logging.getLogger('FortniteData.modules.util')

configuration = None
database = None
ready = False
languages = {}
fortniteapi = {}
error_cache = {}

on_ready_count = 0
start_time = time.time()

###
## Critical
###

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

    client = motor_asyncio.AsyncIOMotorClient(connection_string)

    try:
        client.server_info()
        log.debug('Connected.')
        return client
    except Exception as e:
        log.critical(f'Failed while connecting to database. Traceback:\n{traceback.format_exc()}')
        sys.exit(1)

def get_str(lang: str, string: str):

    try:
        return languages[lang].get_item(item = string)
    
    except KeyError:

        return languages['en'].get_item(item = string)


def get_lang(ctx: discord.ApplicationContext):
    locales = configuration.get('locales', {})
    user_locale = ctx.interaction.locale

    if user_locale in list(locales.keys()):

        return user_locale.replace(user_locale, locales[user_locale])
        
        

async def wait_cache_load():

    while True:
        if fortniteapi._loaded_cosmetics == False:
            await asyncio.sleep(0.5)
        else:
            return True


###
## Database Functions
###

# Servers

async def database_get_server(ctx: discord.ApplicationContext):

    data = await database.guilds.find_one({'server_id': ctx.guild_id})
    if data == None:
        await database_store_server(ctx)
        return await database.guilds.find_one({'server_id': ctx.guild_id})
    return data

async def database_store_server(ctx: discord.ApplicationContext):

    if isinstance(ctx, discord.Guild):
        guild_id = ctx.id
    else:
        guild_id = ctx.guild_id

    log.debug('Inserting guild into database...')

    check = await database.guilds.find_one({'server_id': guild_id})

    if check == None:

        data = {
            "server_id": guild_id,
            "added": int(time.time()),
            "language": "en",
            "search_language": "en",
            "shop_channel": {
                "enabled": False,
                "channel": None,
                "webhook": None,
                "webhook_id": None,
                "config": {
                    "header": '',
                    "subheader": '',
                    "footer": ''
                }
            },
            "updates_channel": {
                "enabled": False,
                "channel": None,
                "webhook": None,
                "webhook_id": None,
                "config": {
                    "shopsections": True,
                    "cosmetics": True,
                    "playlists": True,
                    "news": True,
                    "aes": True
                }
            }
        }
        insert =await  database.guilds.insert_one(data)

        if isinstance(insert, results.InsertOneResult):
            log.debug(f'Inserted guild into database. Id: {insert.inserted_id}')
            return insert
        else:
            log.error(f'Failed database insertion of guild {guild_id}')
            return None
    
    else:

        log.debug('Guild is already in database. Returning existing')
        return check

async def database_remove_server(ctx: discord.ApplicationContext):

    if isinstance(ctx, discord.Guild):
        guild_id = ctx.id
    else:
        guild_id = ctx.guild_id

    log.debug(f'Removing guild "{guild_id}" from database...')

    delete = await database.guilds.delete_one({'server_id': guild_id})

    if isinstance(delete, results.DeleteResult):

        log.debug(f'Guild "{guild_id}" removed successfully.')
        return delete

    else:
        log.error(f'Failed database delete of guild {guild_id}')
        return None


async def database_update_server(ctx: discord.ApplicationContext, changes: dict):

    if isinstance(ctx, discord.Guild):
        guild_id = ctx.id
    else:
        guild_id = ctx.guild_id

    log.debug(f'Updating guild "{guild_id}" data. Changes: "{changes}"')

    update = await database.guilds.update_one({'server_id': guild_id}, changes)

    if isinstance(update, results.UpdateResult):

        log.debug(f'Updated guild "{guild_id}" data successfully.')
        return update

    else:
        log.error(f'Failed guild "{guild_id}" data update.')
        return None

###
## Language Stuff
###

class Language:

    def __init__(self, language: str):
        self.language = language
        self.data = None

        self._loaded = False

    def get_item(self, item: str):
        if self._loaded == False:
            return False

        string = self.data.get(item, None)
        if string == None:
            log.error(f'Missing string "{item}" on {self.language}.')
            return item
        
        return string

    async def load_language_data(self):

        log.debug(f'Loading languge {self.language}...')

        try:

            with open(f'langs/{self.language}.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
                self._loaded = True
            
            return True
        
        except:

            try:

                with open(f'langs/{self.language}.json', 'r', encoding='utf-8-sig') as f:
                    self.data = json.load(f)
                    self._loaded = True

                log.debug(f'Language {self.language} loaded!')
                
                return True
            
            except:

                log.error(f'An error ocurred loading language {self.language}.')

                return False

###
## API
###

class FortniteAPI:

    def __init__(self, language: str):

        self.language = language

        self.ClientSession = aiohttp.ClientSession
        self.headers = {
            'Authorization': configuration.get('fortnite-api-key')
        }

        self._loaded_cosmetics = False
        self._loaded_playlists = False
        
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
        self.banners = []

        self.playlists = []


    async def _load_cosmetics(self):

        log.debug(f'[{self.language}] Updating cosmetic cache...')

        async with self.ClientSession() as session:
            
            response = await session.get(f'https://fortnite-api.com/v2/cosmetics/br?language={self.language}', headers=self.headers)

            if response.status != 200:
                data = None
            else:
                data = await response.json()

            if data == None:
                log.warning('Something was wrong with cosmetics API. Using cached cosmetics')
                async with aiofiles.open(f'cache/cosmetics/all_{self.language}.json', 'r', encoding='utf-8') as f:
                    data = json.loads(await f.read())

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

            if cosmetic['type']['value'] == 'banner':
                if cosmetic not in self.banners:
                    self.banners.append(cosmetic)
                    continue
      

        async with aiofiles.open(f'cache/cosmetics/all_{self.language}.json', 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data))

        self._loaded_cosmetics = True

        log.debug(f'[{self.language}] Updated cosmetic cache. Loaded {len(self.all_cosmetics)} cosmetics.')

        return self.all_cosmetics

    async def _load_playlists(self):

        log.debug(f'[{self.language}] Updating playlists cache...')

        data = await self.get_playlists(language=self.language)

        if data == False:
            log.warning('Something was wrong with playlists API. Using cached playlists')
            
            async with aiofiles.open(f'cache/playlists/{self.language}.json', 'r', encoding='utf-8') as f:
                data = json.loads(await f.read())

        addedCount = 0

        for playlist in data['data']:

            if playlist not in self.playlists:

                self.playlists.append(playlist)
                addedCount += 1
    
        async with aiofiles.open(f'cache/playlists/{self.language}.json', 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data))
        
        self._loaded_playlists = True

        log.debug(f'[{self.language}] Updated playlists cache. Loaded {addedCount} playlists.')

        return self.playlists
        
    async def get_cosmetic(self, query: str, **kwargs):

        cosmetic_types = kwargs.get('cosmetic_types', None)
        match_method = kwargs.get('match_method', 'starts')

        if len(self.all_cosmetics) == 0:
            return False

        lists_to_search = []

        if cosmetic_types != None:

            for i in cosmetic_types:

                if i == 'outfit':
                    lists_to_search.append(self.outfits)
                elif i == 'emote':
                    lists_to_search.append(self.emotes)
                elif i == 'backpack':
                    lists_to_search.append(self.backpacks)
                elif i == 'pickaxe':
                    lists_to_search.append(self.pickaxes)
                elif i == 'wrap':
                    lists_to_search.append(self.wraps)
                elif i == 'contrail':
                    lists_to_search.append(self.contrails)
                elif i == 'loadingscreen':
                    lists_to_search.append(self.loadingscreens)
                elif i == 'spray':
                    lists_to_search.append(self.sprays)
                elif i == 'glider':
                    lists_to_search.append(self.gliders)
                elif i == 'banner':
                    lists_to_search.append(self.banners)
                else:
                    log.error(f'Unknown cosmetic type "{i}". Will be skipped')

        else:

            lists_to_search = [self.all_cosmetics]

        results = []

        is_id = query.lower().startswith(('cid_', 'bid_', 'pickaxe_', 'eid_', 'musicpack_', 'spid_', 'lsid_', 'wrap_', 'glider_', 'bannertoken_'))

        for cosmeticlist in lists_to_search:

            for item in cosmeticlist:

                if is_id:
                    if match_method == 'starts':
                        if item['id'].lower().startswith(query.lower()):
                            results.append(item)

                    elif match_method == 'contains':
                        if query.lower() in item['id'].lower():
                            results.append(item)

                else:
                    if match_method == 'starts':
                        if item['name'].lower().startswith(query.lower()):
                            results.append(item)
                    
                    elif match_method == 'contains':
                        if query.lower() in item['name'].lower():
                            results.append(item)

        return results

    async def get_playlist(self, query: str, **kwargs):

        match_method = kwargs.get('match_method', 'starts')

        log.debug(f'Searching playlists with match method "{match_method}". Query: "{query}"')

        if len(self.playlists) == 0:
            return False

        results = []

        is_id = query.lower().startswith('playlist_')

        for playlist in self.playlists:

            if is_id:
                if match_method == 'starts':
                    if playlist['id'].lower().startswith(query.lower()):
                        results.append(playlist)

                elif match_method == 'contains':
                    if query.lower() in playlist['id'].lower():
                        results.append(playlist)

            else:

                if playlist['name'] == None: # some playlists don't have name
                    nameOrId = playlist['id'].replace('playlist_', '')
                else:
                    if playlist['subName'] == None:
                        nameOrId = f'{playlist["name"]}'
                    else:
                        nameOrId = f'{playlist["name"]} {playlist["subName"]}'

                if match_method == 'starts':
                    if nameOrId.lower().startswith(query.lower()):
                        results.append(playlist)
                
                elif match_method == 'contains':
                    if query.lower() in nameOrId.lower():
                        results.append(playlist)

        return results

    async def get_new_items(self, language='en'):

        async with self.ClientSession() as session:
                
            response = await session.get(f'https://fortnite-api.com/v2/cosmetics/br/new?language={language}', headers=self.headers)

            if response.status != 200:
                return False
            else:
                return await response.json()

    async def get_news(self, language='en'):

        async with self.ClientSession() as session:

            response = await session.get(f'https://fortnite-api.com/v2/news?language={language}', headers=self.headers)

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

    async def get_playlists(self, language='en'):

        async with self.ClientSession() as session:
                
            response = await session.get(f'https://fortnite-api.com/v1/playlists?language={language}', headers=self.headers)

            if response.status != 200:
                return False
            else:
                return await response.json()

def get_custom_shop_url(server: dict):

    shopconfig = server['shop_channel']['config']
    shopconfig['cache'] = int(time.time()) # just to prevent discord from caching old shop images

    BaseURL = 'https://api.nitestats.com/v1/shop/image'

    query_string = urlencode(shopconfig)

    return BaseURL + '?' + query_string


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

class Colors:

    BLURPLE = 0x2200CC
    BLUE = 0x0068DE
    GREEN = 0x00CC2C
    YELLOW = 0xDECF00
    ORANGE = 0xDE6F00
    RED = 0xDE1E00

def get_section_displayname(section_id: str, sections_data: list):
    for section in sections_data:
        if section['sectionId'] == section_id:
            return section.get('sectionDisplayName', section_id)
    return section_id