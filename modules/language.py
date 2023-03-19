import aiofiles
import logging
import orjson

log = logging.getLogger('FortniteData.modules.language')

class Languages:

    def __init__(self, languages: list):
        self.languages = languages
        self.data = dict()

    async def initialize(self):

        log.info('Initializing languages...')

        for lang in self.languages:
            try:
                async with aiofiles.open(f'langs/{lang}.json', 'r', encoding='utf-8') as f:
                    self.data[lang] = orjson.loads(await f.read())
                    log.info(f'Loaded "{lang}".')
            except:
                log.error(f'An error ocurred loading language {lang}')

    async def get_str(self, lang: str, key: str):

        language = self.data.get(lang, None)

        if language == None:
            log.error(f'Unable to return string, language "{lang}" is not loaded.')
            return key

        string = language.get(key, None)

        if not string:
            log.error(f'String for "{key}" not found.')
            return key
        else:
            return string
