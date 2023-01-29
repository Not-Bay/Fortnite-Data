from urllib.parse import urlencode
import aiofiles
import logging
import aiohttp
import orjson

log = logging.getLogger('FortniteData.modules.api')

class API:

    def __init__(self, name: str, base_url: str, authorization: str = None):

        self.name = name
        self.base_url = base_url
        self.authorization = authorization

        self.client = None

    async def send_request(
        self,
        method: str,
        endpoint: str,
        parameters: dict = None,
        headers: dict = {},
        body: dict = None,
    ):

        log.debug(f'[{self.name}] Sending {method} request to "{endpoint}"')

        if self.client == None:
            self.client = aiohttp.ClientSession()

        final_url = f'{self.base_url}{endpoint}'

        if parameters != None:
            final_url += f'?{urlencode(parameters)}' # append parameters to url

        if self.authorization != None:
            headers['Authorization'] = self.authorization

        async with self.client.request(
            method = method,
            url = final_url,
            body = body,
            headers = headers
        ) as request:

            log.debug(f'[{self.name}] Request sent, received status {request.status}.')

            return request

class FortniteAPI(API):

    def __init__(self, api_key: str):
        super().__ini__(
            name = 'Fortnite-API',
            base_url = 'https://fortnite-api.com',
            authorization = api_key
        )

        self.cache = dict()

    def clear_cache(self):
        self.cache = dict() # new empty dict

    async def fetch_cosmetics(self, language: str = 'en', allow_cached: bool = True):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v2/cosmetics/br',
            parameters = {
                'language': language
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] Cosmetics fetch failed.')
        
            if allow_cached == True:

                log.info(f'[{self.name}] Trying to use cached data...')

                try:
                    async with aiofiles.open(f'cache/cosmetics/all_{language}.json', 'r', encoding='utf-8') as f:
                        return orjson.loads(await f.read())
                except:
                    log.error(f'[{self.name}] Unable to load cached data.')
                    return None

        else:

            data = await response.json(loads=orjson.loads)

            async with aiofiles.open(f'cache/cosmetics/all_{language}.json', 'w', encoding='utf-8') as f:
                await f.write(orjson.dumps(data).decode())
                log.debug(f'[{self.name}] updated local cosmetics cache.')

            return data

    async def fetch_playlists(self, language: str = 'en', allow_cached: bool = True):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v1/playlists',
            parameters = {
                'language': language
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] Playlists fetch failed.')
        
            if allow_cached == True:

                log.info(f'[{self.name}] Trying to use cached data...')

                try:
                    async with aiofiles.open(f'cache/playlists/{language}.json', 'r', encoding='utf-8') as f:
                        return orjson.loads(await f.read())
                except:
                    log.error(f'[{self.name}] Unable to load cached data.')
                    return None

        else:

            data = await response.json(loads=orjson.loads)

            async with aiofiles.open(f'cache/playlists/{language}.json', 'w', encoding='utf-8') as f:
                await f.write(orjson.dumps(data).decode())
                log.debug(f'[{self.name}] updated local playlists cache.')

            return data

    async def fetch_cosmetics_new(self, language: str = 'en'):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v2/cosmetics/br/new',
            parameters = {
                'language': language
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] New cosmetics fetch failed.')
            return None

        else:

            return await response.json(loads=orjson.loads)

    async def fetch_news(self, language: str = 'en'):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v2/news',
            parameters = {
                'language': language
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] News fetch failed.')
            return None

        else:

            return await response.json(loads=orjson.loads)

    async def fetch_aes(self, key_format: str = 'hex'):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v2/aes',
            parameters = {
                'keyFormat': key_format
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] Aes keys fetch failed.')
            return None

        else:

            return await response.json(loads=orjson.loads)

    async def fetch_creator_code(self, code: str):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v2/creatorcode/search',
            parameters = {
                'name': code
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] Creator fetch failed.')
            return None

        else:

            return await response.json(loads=orjson.loads)

    async def fetch_stats(self, display_name: str, account_type: str = 'epic', time_window: str = 'lifetime',image: str = 'all'):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v2/stats/br/v2',
            parameters = {
                'name': display_name,
                'accountType': account_type, # epic, psn, xbl
                'timeWindow': time_window, # lifetime, season
                'image': image # all, keyboardMouse, gamepad, touch
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] "{display_name}" stats fetch failed.')
            return None

        else:

            return await response.json(loads=orjson.loads)


class BaydevAPI(API):

    def __init__(self):
        super().__init__(
            name = 'BaydevAPI',
            base_url = 'https://baydev.net/api'
        )

    async def fetch_shop_sections(self):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v1/shopsections'
        )

        if response.status != 200:
            log.error(f'[{self.name}] Shop sections fetch failed.')
            return None

        else:

            return await response.json(loads=orjson.loads)

    async def fetch_fortnite_content(self, language: str = 'en'):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v1/fortnite-content',
            parameters = {
                'language': language, # en, es, ja
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] Fortnite content fetch failed.')
            return None

        else:

            return await response.json(loads=orjson.loads)

    async def fetch_manifest(self, platform: str = 'windows'):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v1/manifest',
            parameters = {
                'platform': platform # windows, android, xbox, ps4
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] {platform} manifest fetch failed.')
            return None

        else:

            return await response.json(loads=orjson.loads)

class FortniteCentral(API):

    def __init__(self):
        super().__init__(
            name = 'FortniteCentral',
            base_url = 'https://fortnitecentral.genxgames.gg'
        )

    async def fetch_assets(self):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/api/v1/assets'
        )

        if response.status != 200:
            log.error(f'[{self.name}] Unable to fetch assets.')
            return None

        else:

            return await response.json()

    async def export_asset(
        self,
        path: str,
        raw: bool = True
    ):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/api/v1/export',
            parameters = {
                'path': path,
                'raw': raw
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] Unable to export asset.')
            return None

        else:

            return response.read(), response.content_type

class Nitestats(API):

    def __init__(self):
        super().__init__(
            name = 'Nitestats',
            base_url = 'https://api.nitestats.com'
        )

    async def fetch_shop_hash(self):

        response = await self.send_request(
            method = 'GET',
            endpoint = 'v1/shop/shophash'
        )

        if response.status != 200:
            log.error(f'[{self.name}] Shop fetch failed.')
            return None

        else:

            return await response.text()

    async def fetch_shop(
        self,
        header: str = None,
        subheader: str = None,
        footer: str = None,
        textcolor: str = None,
        background: str = None
    ):

        response = await self.send_request(
            method = 'GET',
            endpoint = '/v1/shop/image',
            parameters = {
                'header': header,
                'subheader': subheader,
                'footer': footer,
                'textcolor': textcolor,
                'background': background
            }
        )

        if response.status != 200:
            log.error(f'[{self.name}] Shop fetch failed.')
            return None

        else:

            return await response.json(loads=orjson.loads)
