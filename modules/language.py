import logging
import orjson

log = logging.getLogger('FortniteData.modules.language')

class Languages:

    def __init__(self, languages: list):
        self.languages = languages
        self.data = dict()

        self.initialized = False

    def initialize(self, reload: bool = False):

        if self.initialized and not reload:
            log.warning('initialization called but already loaded, ignoring.')
            return

        if reload:
            log.info('Reloading languages...')
        else:
            log.info('Initializing languages...')

        for lang in self.languages:
            try:
                with open(f'langs/{lang}.json', 'r', encoding='utf-8') as file:
                    self.data[lang] = orjson.loads(file.read())
                    log.info(f'Loaded "{lang}".')
            except:
                log.exception(f'An error ocurred loading language {lang}')
        
        self.initialized = True

    def get_str(self, key: str, lang: str = 'en'):

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
