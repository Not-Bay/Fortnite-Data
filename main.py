bot_version = '3.3.2'

from discord.ext import commands
import pymongo
import asyncio
import discord
import funcs
import json
import sys
import os

if '--vps' in sys.argv:
    os.chdir('/home/Fortnite-Data/')

with open('values.json', 'r', encoding='utf-8') as f:
    mongodb_url = json.load(f)['mongodb_url']

client = pymongo.MongoClient(mongodb_url)

if '--debug' not in sys.argv:
    db = client.fortnitedata
else:
    db = client.fortnitedata_debug


def cfg():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def getprefix(bot, message):
    return db.guilds.find_one(filter={"server_id": message.guild.id})['prefix']


intents = discord.Intents.default()
bot = commands.Bot(
    command_prefix=getprefix,
    case_insensitive=True,
    intents=intents)
bot.remove_command('help')

extensions = ['general', 'other', 'settings', 'events', 'tasks', 'admin', 'updates']

@bot.event
async def on_ready():

    for guild in bot.guilds:
        try:
            await funcs.create_config(guild)
        except:
            funcs.log(f'Failed to create config for guild {guild.id}')

    for extension in extensions:
        try:
            bot.load_extension(f'extensions.{extension}')
        except Exception as e:
            print(f'Could not load extension {extension}: {e}')

    funcs.log('Fortnite Data Ready')


    #wait 2 days for restart
    if '--debug' not in sys.argv:

        await asyncio.sleep(172800)
        os.system('systemctl restart fortnitedata.service')

general_commands = ['help', 'item', 'leaked', 'shop', 'news', 'creatorcode', 'aes', 'stats', 'playlist', 'banner', 'search', 'export']
other_commands = ['ping', 'info', 'invite', 'settings', 'prefix', 'lang', 'feedback', 'search_lang', 'shopchannel', 'maxresults', 'updateschannel', 'shopconfig', 'updatesconfig']


@bot.command(usage='help [command]')
@commands.cooldown(1, 3, commands.BucketType.user)
async def help(ctx, command = None):

    if command == None:
        embed = discord.Embed(
            title=text(ctx, value='help'),
            color=0x570ae4, 
            timestamp=ctx.message.created_at)
        embed.set_footer(
        text=f"{text(ctx, 'type_help_for_command_details').format(getprefix(bot, ctx.message))} • {text(ctx, value='executed_by')} {ctx.author}",
        icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=bot.user.avatar_url)


        g_cmds = ''.join([f'`{x}` ' for x in general_commands])
        o_cmds = ''.join([f'`{x}` ' for x in other_commands])

        embed.add_field(name=text(ctx, 'general'), value=str(g_cmds))
        embed.add_field(name=text(ctx, 'other'), value=str(o_cmds))

        embed.add_field(name=text(ctx, 'usefull_links'), 
        value = f'{text(ctx, "support_server")}: [discord.gg/UU9HjA5](https://www.discord.com/invite/UU9HjA5)\n{text(ctx, "upvote_link")}: [top.gg/bot/729409703360069722/vote](https://top.gg/bot/729409703360069722/vote)\n{text(ctx, "documentation")}: [docs.fortnitedata.tk](https://docs.fortnitedata.tk)', inline=False)

        await ctx.send(embed=embed)
        return
    
    cmd = bot.get_command(command)

    if cmd == None:
        embed = discord.Embed(
            description = text(ctx, 'command_not_found'),
            color = discord.Colour.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title = text(ctx, value='help'),
        color = 0x570ae4
    )

    embed.add_field(name=text(ctx, 'name'), value=f'`{cmd.name}`')
    embed.add_field(name=text(ctx, 'description'), value=f'`{cmd_description(ctx, cmd.name)}`')
    embed.add_field(name=text(ctx, 'usage'), value=f'`{db.guilds.find_one(filter={"server_id": ctx.guild.id})["prefix"]}{cmd.usage}`')
    embed.add_field(name=text(ctx, 'aliases'), value=''.join(f'`{x}` ' for x in cmd.aliases) if cmd.aliases != [] else text(ctx, 'none'))

    embed.set_footer(
        text=f"{text(ctx, value='executed_by')} {ctx.author}",
        icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)


def text(ctx, value: str):
    server = db.guilds.find_one({"server_id": ctx.guild.id})

    if ctx.guild.id == 718709023427526697: #Custom stuff for Fortnite-LobbyBot Server
        lang = 'es' if ctx.channel.category_id == 719714076087025706 else 'en' if ctx.channel.category_id == 718711009971535943 else 'ja' if ctx.channel.category_id == 719713694874992681 else 'en'
        try:
            with open(f'langs/{lang}.json', 'r', encoding='utf-8') as f:
                return json.load(f)[str(value)]
        except:
            with open(f'langs/{lang}.json', 'r', encoding='utf-8-sig') as f:
                return json.load(f)[str(value)]


    lang = 'es' if server['lang'] == 'es' else 'en' if server['lang'] == 'en' else 'ja' if server['lang'] == 'ja' else 'en'

    try:
        with open(f'langs/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)[str(value)]
    except:
        with open(f'langs/{lang}.json', 'r', encoding='utf-8-sig') as f:
            return json.load(f)[str(value)]

def cmd_description(ctx, value: str):
    server = db.guilds.find_one({"server_id": ctx.guild.id})

    if ctx.guild.id == 718709023427526697: #Custom stuff for Fortnite-LobbyBot Server
        lang = 'es' if ctx.channel.category_id == 719714076087025706 else 'en' if ctx.channel.category_id == 718711009971535943 else 'ja' if ctx.channel.category_id == 719713694874992681 else 'en'
        try:
            with open(f'langs/{lang}.json', 'r', encoding='utf-8') as f:
                return json.load(f)['command_stuff'][str(value)]
        except:
            with open(f'langs/{lang}.json', 'r', encoding='utf-8-sig') as f:
                return json.load(f)['command_stuff'][str(value)]

    lang = 'es' if server['lang'] == 'es' else 'en' if server['lang'] == 'en' else 'ja' if server['lang'] == 'ja' else 'en'

    try:
        with open(f'langs/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)['command_stuff'][str(value)]
    except:
        with open(f'langs/{lang}.json', 'r', encoding='utf-8-sig') as f:
            return json.load(f)['command_stuff'][str(value)]


if __name__ == '__main__':

    token = cfg()['token'] if '--debug' not in sys.argv else cfg()['token_debug']
    
    bot.run(token)