from discord.ext import commands
import coloredlogs
import traceback
import logging
import discord
import asyncio
import time
import sys

from modules import util

log = logging.getLogger('FortniteData')
coloredlogs.install(level=None if util.debug == False else 'DEBUG')

# Set up uvloop if possible
try:
    import uvloop # type: ignore
except:
    log.warning('Using default asyncio event loop.')
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    log.debug('Using uvloop.')

bot = commands.AutoShardedBot(
    command_prefix=util.get_prefix,
    intents=discord.Intents.default()
)
bot.remove_command('help')

@bot.event
async def on_connect():
    log.debug('Connected to Discord')

@bot.event
async def on_ready():

    for i in util.configuration.get('languages'):
        lang = util.Language(i)
        load = await lang.load_language_data()
        if load == True:
            util.languages[i] = lang
        else:
            util.languages[i] = False

        util.fortniteapi[i] = util.FortniteAPI(i)

    util.ready = True

    if '--sync-guilds-on-ready' in sys.argv:
        for guild in bot.guilds:
            util.database_store_server(guild)

    log.info(f'Fortnite Data is ready! • Took {int((time.time() - util.start_time))} seconds.')


def run():

    for logger in list(logging.Logger.manager.loggerDict):
        if logger.startswith('FortniteData') == False: # 3rd party modules loggers go brrrrrr
            logging.getLogger(logger).disabled = True

    log.info('Booting...')

    util.log = logging.getLogger('FortniteData.util')

    util.configuration = util.get_config()
    util.database = util.get_mongoclient().fortnitedata

    log.debug('Starting discord bot...')

    for cog in util.configuration.get('cogs'):
        try:
            bot.load_extension(f'cogs.{cog}')
            log.debug(f'Loaded cog {cog}.')
        except:
            log.error(f'An error ocurred loading cog "{cog}". Traceback: {traceback.format_exc()}')

    if len(util.configuration.get('slash_debug_guilds')) != 0:
        util.debug_guilds = util.configuration.get('slash_debug_guilds')

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