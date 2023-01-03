import coloredlogs
import traceback
import logging
import discord
import asyncio
import sys

from modules import util

log = logging.getLogger('FortniteData')
coloredlogs.install(level=None if util.debug == False else 'DEBUG')

util.configuration = util.get_config()

bot = discord.Bot(
    intents = discord.Intents.default(),
    auto_sync_commands = True,
    debug_guilds = util.configuration.get('admin_guilds', None)
)

def run():

    for logger in list(logging.Logger.manager.loggerDict):
        if logger.startswith('FortniteData') == False:
            logging.getLogger(logger).disabled = True

    log.info('Booting...')

    for cog in util.configuration.get('cogs'):
        try:
            bot.load_extension(f'cogs.{cog}')
            log.debug(f'Loaded cog {cog}.')
        except:
            log.error(f'An error ocurred loading cog "{cog}". Traceback: {traceback.format_exc()}')

    util.database = util.get_mongoclient().fortnitedata

    log.debug('Starting discord bot...')

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(bot.start(util.configuration.get('bot_token')))
    except KeyboardInterrupt:
        log.info('KeyboardInterrupt, exiting...')
        loop.run_until_complete(bot.close())
    except Exception:
        log.critical(f'An error ocurred starting discord bot. Traceback:\n{traceback.format_exc()}')
        loop.run_until_complete(bot.close())
    finally:
        loop.close()
        sys.exit()


if __name__ == '__main__':

    run()