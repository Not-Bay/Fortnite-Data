from discord.ext import commands
import io
import funcs
import asyncio
import requests
import discord
import json
import main


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage='item <cosmetic name / cosmetic id>')
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def item(self, ctx, *, args = None):

        if args == None:

            embed = discord.Embed(
                description = main.text(ctx, 'must_enter_value'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)
            return

        serverconfig = main.db.guilds.find_one({"server_id": ctx.guild.id})

        if ctx.guild.id == 718709023427526697: #Custom stuff for Fortnite-LobbyBot Server. hi <3

            searchLanguage = 'en'
            language = 'en'

            if ctx.channel.category_id == 719713694874992681: # ja
                searchLanguage = 'ja'
                language = 'ja'

            elif ctx.channel.category_id == 719714076087025706: # es
                searchLanguage = 'es'
                language = 'es'

            if args.lower().startswith(('cid_', 'bid_', 'pickaxe_', 'eid_', 'musicpack_', 'spid_', 'lsid_', 'wrap_', 'glider_')):
                params = {
                    "language": language,
                    "searchLanguage": searchLanguage,
                    "matchMethod": "contains",
                    "id": args
                }
            else:
                params = {
                    "language": language,
                    "searchLanguage": searchLanguage,
                    "matchMethod": "contains",
                    "name": args
                }

            response = requests.get('https://fortnite-api.com/v2/cosmetics/br/search/all', params=params)

        else:

            if args.lower().startswith(('cid_', 'bid_', 'pickaxe_', 'eid_', 'musicpack_', 'spid_', 'lsid_', 'wrap_', 'glider_')):
                params = {
                    "language": serverconfig['lang'],
                    "searchLanguage": serverconfig['search_lang'],
                    "matchMethod": "contains",
                    "id": args
                }
            else:
                params = {
                    "language": serverconfig['lang'],
                    "searchLanguage": serverconfig['search_lang'],
                    "matchMethod": "contains",
                    "name": args
                }

            response = requests.get('https://fortnite-api.com/v2/cosmetics/br/search/all', params=params)

        if response.status_code == 200:

            geted = response.json()

            results = []

            for item in geted['data']:

                try:
                    item_set = item["set"]["value"]
                except:
                    item_set = main.text(ctx, 'none')
                try:
                    item_introduction = item['introduction']['text']
                except:
                    item_introduction = main.text(ctx, 'not_introduced_yet')

                if item['showcaseVideo'] != None:
                    item_showcase = item['showcaseVideo']
                    youtube_url = 'https://www.youtube.com/watch?v='
                    showcasevideo = youtube_url + item_showcase
                else:
                    showcasevideo = f"`{main.text(ctx, 'none')}`"

                embed = discord.Embed(
                        title=item['type']['displayValue'],
                        color=funcs.rarity_color(item['rarity']['value']),
                        timestamp=ctx.message.created_at
                    )
                embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

                if item['images']['icon'] != None:
                    embed.set_thumbnail(url=item['images']['icon'])

                embed.add_field(name=main.text(ctx, value='name'),value=f'``{item["name"]}``')
                embed.add_field(name=main.text(ctx, value='id'),value=f'``{item["id"]}``')
                
                embed.add_field(name=main.text(ctx, value='description'), value=f'``{item["description"]}``')
                embed.add_field(name=main.text(ctx, value='rarity'), value=f'``{item["rarity"]["displayValue"]}``')
                
                embed.add_field(name=main.text(ctx, value='set'),value=f'`{item_set}`')
                embed.add_field(name=main.text(ctx, value='introduction'),value=f'`{item_introduction}`')

                embed.add_field(name=main.text(ctx, value='showcase_video'), value=f'{showcasevideo}')

                if item['gameplayTags'] != None:
                    gameplaytags = '\n'.join(f'{x}' for x in item['gameplayTags'])
                else:
                    gameplaytags = main.text(ctx, 'none')
                embed.add_field(name='GameplayTags', value=f'`{gameplaytags}`')

                results.append(embed)
            
            sended = 0
            maximum = serverconfig['max_results']
            left = 0
            
            for embed in results:
                if sended != maximum:
                    await ctx.send(embed=embed)
                    await asyncio.sleep(1.1)
                    sended += 1
                else:
                    left += 1

            if left > 0:
                await ctx.send(f'{main.text(ctx, value="max_items_sended").format(left)}')

        elif response.status_code == 404:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:

            embed = discord.Embed(
                description = main.text(ctx, 'no_valid_response').format(response.status_code),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

    @commands.command(aliases=['leaks'], usage='leaked')
    @commands.cooldown(2, 15, commands.BucketType.user)
    async def leaked(self, ctx):

        serverconfig = main.db.guilds.find_one({"server_id": ctx.guild.id})

        params = {"lang": f"{serverconfig['lang']}"}

        response = requests.get('https://api.peely.de/cdn/current/leaks.png', params=params)

        if response.status_code == 200:

            if response.headers['Content-Type'] == 'image/png':

                file = discord.File(io.BytesIO(response.content), 'leaks.png')

                embed = discord.Embed(
                    title = main.text(ctx, 'new_items'),
                    color = 0x570ae4
                )
                embed.set_image(url='attachment://leaks.png')

                await ctx.send(embed=embed, file=file)
                return

            else:

                embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
                )
                await ctx.send(embed=embed)

        elif response.status_code == 404 or 400:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)


            
    @commands.group(usage='news <br / stw / creative>')
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def news(self, ctx):
        serverconfig = main.db.guilds.find_one({"server_id": ctx.guild.id})
        
        if ctx.message.content == f'{serverconfig["prefix"]}news':

            embed = discord.Embed(
                description = f"{main.text(ctx, 'usage')}: `{serverconfig['prefix']}news <br / stw / creative>`",
                color = 0x570ae4
            )
            await ctx.send(embed=embed)
            return

        else:
            pass
    
    @news.command()
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def br(self, ctx, lang=None):
        serverconfig = main.db.guilds.find_one({"server_id": ctx.guild.id})

        response = requests.get(f'https://fortnite-api.com/v2/news/br?language={serverconfig["lang"] if lang == None else lang}')

        if response.status_code == 200:

            img = response.json()['data']['image']

            embed = discord.Embed(
                title=main.text(ctx, value='br_news'),
                color=0x570ae4,
                timestamp=ctx.message.created_at
            )
            embed.set_image(url=img)
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)

        elif response.status_code == 404 or 400:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)

    @news.command()
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def creative(self, ctx, lang=None):
        serverconfig = main.db.guilds.find_one({"server_id": ctx.guild.id})

        response = requests.get(f'https://fortnite-api.com/v2/news/creative?language={serverconfig["lang"] if lang == None else lang}')

        if response.status_code == 200:

            img = response.json()['data']['image']

            embed = discord.Embed(
                title=main.text(ctx, value='cr_news'),
                color=0x570ae4,
                timestamp=ctx.message.created_at
            )
            embed.set_image(url=img)
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)

        elif response.status_code == 404 or 400:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)
    
    @news.command()
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def stw(self, ctx, lang=None):
        serverconfig = main.db.guilds.find_one({"server_id": ctx.guild.id})

        response = requests.get(f'https://api.peely.de/v1/stw/news?lang={serverconfig["lang"] if lang == None else lang}')

        if response.status_code == 200:

            img = response.json()['data']['image']

            embed = discord.Embed(
                title=main.text(ctx, value='stw_news'),
                color=0x570ae4,
                timestamp=ctx.message.created_at
            )
            embed.set_image(url=img)
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)

        elif response.status_code == 404 or 400:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)

    @commands.command(usage='stats <account name>')
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def stats(self, ctx, *, account = None):

        if account == None:

            embed = discord.Embed(
                description = main.text(ctx, 'must_enter_value'),
                color = discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return
        
        with open('values.json', 'r', encoding='utf-8') as f:
            api_key = json.load(f)['fortnite-api_key']

        response = requests.get(
            f'https://fortnite-api.com/v1/stats/br/v2?name={account.replace(" ", "+")}&image=all',
            headers = {
                'Authorization': api_key
            }
        )

        if response.status_code == 200:

            geted = response.json()

            embed = discord.Embed(
                description = f'{main.text(ctx, "player_stats").format(geted["data"]["account"]["name"])}',
                color = 0x570ae4,
                timestamp = ctx.message.created_at
            )
            embed.set_image(url='attachment://stats.jpg')
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed, file=discord.File(io.BytesIO(requests.get(response.json()['data']['image']).content), 'stats.jpg'))

        elif response.status_code == 404 or 400:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)

    @commands.command(aliases=['cc'], usage='creatorcode <code>')
    @commands.cooldown(4, 30, commands.BucketType.user)
    async def creatorcode(self, ctx, *, code=None):

        if code == None:

            embed = discord.Embed(
                description = main.text(ctx, 'must_enter_value'),
                color = discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        response = requests.get(f'https://fortnite-api.com/v2/creatorcode?name={code}')

        if response.status_code == 200:

            geted = response.json()

            code = geted['data']['code']
            code_account = geted['data']['account']['name']
            code_account_id = geted['data']['account']['id']
            code_status = main.text(ctx, value='active') if geted['data']['status'] == 'ACTIVE' else main.text(ctx, 'inactive') if geted['data']['status'] == 'INACTIVE' else main.text(ctx, 'disabled') if geted['data']['status'] == 'DISABLED' else main.text(ctx, value='unknown')
            code_verified = main.text(ctx, 'yes') if geted['data']['verified'] == True else main.text(ctx, 'no')


            embed = discord.Embed(
                title = main.text(ctx, 'creator_code_info'),
                color = 0x570ae4,
                timestamp = ctx.message.created_at
            )
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            embed.add_field(name=main.text(ctx, value='code'), value=f'``{code}``')
            embed.add_field(name=main.text(ctx, value='account'), value=f'``{code_account}``')

            embed.add_field(name=main.text(ctx, value='account_id'), value=f'``{code_account_id}``')
            embed.add_field(name=main.text(ctx, value='status'), value=f'``{code_status}``')

            embed.add_field(name=main.text(ctx, value='verified?'), value=f'``{code_verified}``')

            await ctx.send(embed=embed)

        elif response.status_code == 404 or 400:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)


    @commands.command(usage='shop')
    @commands.cooldown(4, 30, commands.BucketType.user)
    async def shop(self, ctx):
        
        response = requests.get('https://api.nitestats.com/v1/shop/image', params=funcs.compose_shop_headers(ctx.guild))

        if response.status_code == 200:

            embed = discord.Embed(
                title = main.text(ctx, 'item_shop'),
                color = 0x570ae4,
                timestamp = ctx.message.created_at
            )
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            embed.set_image(url='attachment://shop.png')

            await ctx.send(embed=embed, file=discord.File(fp=io.BytesIO(response.content), filename='shop.png'))


        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)

    @commands.command(usage='aes')
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def aes(self, ctx):

        response = requests.get('https://fortnite-api.com/v2/aes')

        if response.status_code == 200:

            geted = response.json()

            aes_build = geted['data']['build']
            aes_mainAes = geted['data']['mainKey']
            aes_dynamicKeys = geted['data']['dynamicKeys']

            embed = discord.Embed(
                title=main.text(ctx, value='aes_keys'),
                description=main.text(ctx, value='aes_keys_description').format(aes_build),
                color=0x570ae4,
                timestamp=ctx.message.created_at
            )
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            for subkeys in aes_dynamicKeys:
                embed.add_field(name=f'{subkeys["pakFilename"]}', value=f'{subkeys["key"]}')

            await ctx.send(embed=embed)

        elif response.status_code == 404 or 400:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)

    @commands.command(usage='playlist <playlist name / exact ID>')
    @commands.cooldown(4, 30, commands.BucketType.user)
    async def playlist(self, ctx, *, args = None):

        if args == None:

            embed = discord.Embed(
                description = main.text(ctx, 'must_enter_value'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)
            return
        
        server = main.db.guilds.find_one({"server_id": ctx.guild.id})
        response = requests.get(f'https://fortnite-api.com/v1/playlists?language={server["lang"]}')

        if response.status_code == 200:

            geted = response.json()
            flag = False
            results = []
            master_string = {}

            for playlist in geted['data']:

                if args.lower() == playlist['id'].lower():
                    master_string = playlist
                    flag = True
                    break

                if args.lower() in playlist['name'].lower():
                    results.append(playlist)

            if flag == True:

                embed = discord.Embed(
                    title = master_string['name'],
                    description = master_string['description'],
                    color = 0x570ae4,
                    timestamp = ctx.message.created_at
                )
                embed.add_field(name='ID', value=f'`{master_string["id"]}`')

                embed.add_field(name=main.text(ctx, 'path'), value=f'`{master_string["path"]}`', inline=False)
                embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

                embed.add_field(name='Gameplay Tags', value=''.join(f'`{x}`\n' for x in master_string['gameplayTags']), inline=False)

                if master_string['images']['showcase'] != None:
                    embed.set_image(url=master_string['images']['showcase'])
                if master_string['images']['missionIcon'] != None:
                    embed.set_thumbnail(url=master_string['images']['missionIcon'])

                await ctx.send(embed=embed)
                return

            if len(results) < 1:

                embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
                )
                await ctx.send(embed=embed)
                return

            desc = ''.join(f'`{x["name"]} - {x["id"]}`\n' for x in results)

            embed = discord.Embed(
                title = main.text(ctx, 'results_for').format(args),
                description = desc,
                color = 0x570ae4,
                timestamp = ctx.message.created_at
            )
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            if len(desc) > 2048:

                await ctx.send(file=discord.File(io.StringIO(json.dumps(results, indent=4)), 'results.json'))
                return

            await ctx.send(embed=embed)

            

        elif response.status_code == 404 or 400:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)

    @commands.command(usage='banner <devname / exact ID>')
    @commands.cooldown(4, 30, commands.BucketType.user)
    async def banner(self, ctx, *, args = None):

        if args == None:

            embed = discord.Embed(
                description = main.text(ctx, 'must_enter_value'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)
            return

        server = main.db.guilds.find_one({"server_id": ctx.guild.id})
        response = requests.get(f'https://fortnite-api.com/v1/banners?language={server["lang"]}')

        if response.status_code == 200:

            geted = response.json()
            flag = False

            master_string = {}
            results = []

            for banner in geted['data']:

                if args.lower() == banner['id'].lower():
                    master_string = banner
                    flag = True
                    break

                if args.lower() in banner['devName'].lower():
                    results.append(banner)

            if flag == True:

                embed = discord.Embed(
                    title = master_string['name'],
                    description = master_string['description'],
                    color = 0x570ae4,
                    timestamp = ctx.message.created_at
                )
                embed.add_field(name=f'ID', value=f'`{master_string["id"]}`', inline=True)
                embed.add_field(name=f'{main.text(ctx, "category")}', value=f'`{master_string["category"]}`')

                embed.set_thumbnail(url=master_string["images"]["icon"])

                embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

                await ctx.send(embed=embed)
                return

            if len(results) < 1:

                embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
                )
                await ctx.send(embed=embed)
                return

            desc = ''.join(f'`{x["name"]} - {x["id"]}`\n' for x in results)

            embed = discord.Embed(
                title = main.text(ctx, 'results_for').format(args),
                description = desc,
                color = 0x570ae4,
                timestamp = ctx.message.created_at
            )
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            if len(desc) > 2048:

                await ctx.send(file=discord.File(io.StringIO(json.dumps(results, indent=4)), 'results.json'))
                return

            await ctx.send(embed=embed)


        elif response.status_code == 404 or 400:

            embed = discord.Embed(
                description = main.text(ctx, 'nothing_found'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description = main.text(ctx, value='no_valid_response'),
                color = discord.Colour.red(),
                timestamp = ctx.message.created_at
            )

            await ctx.send(embed=embed)


def convert(ls: list):
    return {ls[i]: ls[i + 1] for i in range(0, len(ls), 2)}

class BenBot(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(usage='search <path> [params]')
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def search(self, ctx, path = None, *params):

        if path == None:

            embed = discord.Embed(
                description = main.text(ctx, 'must_enter_value'),
                color = discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        else:

            r = requests.get('https://benbot.app/api/v1/files/search', params=convert(["path", path] + list(params)))

            if r.status_code != 200:

                embed = discord.Embed(
                    description = main.text(ctx, 'nothing_found'),
                    color = discord.Colour.red()
                )
                await ctx.send(embed=embed)
                return
            
            else:

                if len(r.json()) > 1:
                
                    string = '\n'
                    string += ''.join(f'`{x}`\n' for x in r.json())
                    string += ''
                    if len(string) < 2048:

                        embed = discord.Embed(
                            title = f'{main.text(ctx, "results_for").format(path)}',
                            description = string,
                            color = 0x570ae4
                        )
                        await ctx.send(embed=embed)
                        return

                    else:

                        file = discord.File(io.StringIO(json.dumps(r.json(), indent=4, ensure_ascii=False)), filename='Results.json')
                        await ctx.send(file=file)
                        return

                else:

                    embed = discord.Embed(
                        description = f'{main.text(ctx, "nothing_found")}',
                        color = discord.Colour.red()
                    )
                    await ctx.send(embed=embed)

    @commands.command(usage='export <path> [params]')
    @commands.cooldown(2, 15, commands.BucketType.user)
    async def export(self, ctx, path = None, *params):

        if path == None:

            embed = discord.Embed(
                description = main.text(ctx, 'must_enter_value'),
                color = discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        response = requests.get('https://benbot.app/api/v1/exportAsset',params=convert(["path", path] + list(params)))

        if response.status_code == 404:
            
            embed = discord.Embed(
                    description = main.text(ctx, 'nothing_found'),
                    color = discord.Colour.red()
                )
            await ctx.send(embed=embed)
            return

        if response.status_code == 200:

            if response.headers['Content-Type'] == 'image/png':
                
                file = discord.File(io.BytesIO(response.content), f'{response.headers["Content-Disposition"]}')
                await ctx.send(file=file)

            elif response.headers['Content-Type'] == 'audio/ogg':

                file = discord.File(io.BytesIO(response.content), f'{response.headers["Content-Disposition"]}')
                await ctx.send(file=file)

            elif response.headers['Content-Type'] == 'application/json':

                file = discord.File(io.StringIO(json.dumps(response.text)), f'{response.headers["Content-Disposition"]}')
                await ctx.send(file=file)

            else:

                await ctx.send(main.text(ctx, "file_type_uknown").format(response.headers["Content-Type"]))

        else:

            embed = discord.Embed(
                    description = main.text(ctx, 'no_valid_response'),
                    color = discord.Colour.red()
                )
            await ctx.send(embed=embed)
            return


def setup(bot):
    bot.add_cog(General(bot))
    bot.add_cog(BenBot(bot))