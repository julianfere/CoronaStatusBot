import discord
from discord.ext import commands
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import asyncio
from datetime import date, timedelta

clientdb = MongoClient(CLIENT.LINK)
DB = clientdb[CLUSTER]


class Corona(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.guild = guild

    @commands.Cog.listener()
    async def on_ready(self):
        print('cog.Corona ready')

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        collection = DB[str(message.guild.id)]
        info = collection.find_one({'_id':message.guild.name})
        data = info['data'].copy()
        if str(message.id) in info['data'].keys():
            data.pop(str(message.id))
            collection.update_one({'data':info['data']},{'$set':{'data':data}})
            print('Elimina3')


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.client.user.id:
            print('User')
            if payload.emoji.name == '🔄':
                channel = self.client.get_channel(payload.channel_id)
                msg = await channel.fetch_message(payload.message_id)
                collection = DB[str(payload.guild_id)]
                guild = await self.client.fetch_guild(payload.guild_id)
                c = collection.find_one({'_id': guild.name})
                data = c['data']
                country = data[str(msg.id)]
                await msg.remove_reaction(payload.emoji, payload.member)
                # Embed for updating
                embed_a = discord.Embed(
                    title='Updating please wait...', color=0xf50000)
                embed_a.set_author(
                    name="Coronavirus Update", icon_url="https://flespi.io/covid19/img/android-icon-192x192.a7ab640c.png")
                # end
                await msg.edit(embed=embed_a)
                embed = self.gen_embed(country)
                await msg.edit(embed=embed)

    @commands.command(aliases=['a'])
    async def add(self, ctx, country):
        """
        Add a new embed 
            use !a {Country}
        """
        if ctx.message.author.guild_permissions.manage_messages:
            command = ctx.message
            collection = DB[str(ctx.message.guild.id)]
            info = collection.find_one({'_id': ctx.message.guild.name})
            data = info['data']
            print('data', data)
            data_ant = info['data'].copy()
            print('data_ant', data_ant)
            embed = self.gen_embed(country)
            channel = self.client.get_channel(info['command_channel'])
            e_message = await channel.send(embed=embed)
            data[str(e_message.id)] = country
            print(data)
            print(data_ant)
            await command.delete()
            collection.update_one({'data': data_ant}, {'$set': {'data': data}})
            await e_message.add_reaction('\U0001F504')

    def gen_embed(self, c):
        """
        A
        """
        e, warning = self.get_information(c)
        embed = discord.Embed(title=e[0], color=0xf50000)
        embed.set_author(name="Coronavirus Update",
                         icon_url="https://flespi.io/covid19/img/android-icon-192x192.a7ab640c.png")
        embed.add_field(name="Total Cases", value=e[1], inline=True)
        embed.add_field(name="New Cases", value=e[2], inline=True)
        embed.add_field(name="Active Cases", value=e[7], inline=True)
        embed.add_field(name="Total Deaths", value=e[3], inline=True)
        embed.add_field(name="Total Recovered", value=e[5], inline=False)
        if not warning:
            embed.add_field(
                name="Date", value=date.today().strftime("%d/%m/%Y"))
        else:
            yesterday = (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")
            embed.add_field(name='Date', value=yesterday)
        embed.set_footer(
            text="Source: https://www.worldometers.info/coronavirus/")

        return embed

    def get_information(self, country):
        html = requests.get('https://www.worldometers.info/coronavirus/').text
        html_soup = BeautifulSoup(html, 'html.parser')
        rows = html_soup.find_all('tr')

        def extract_text(row, tag):
            element = BeautifulSoup(row, 'html.parser').find_all(tag)
            text = [col.get_text() for col in element]
            return text

        heading = rows.pop(0)
        heading_row = extract_text(str(heading), 'th')[1:9]
        count = 0
        data_to_compare = []
        for row in rows:
            test_data = extract_text(str(row), 'td')[1:9]
            try:
                if test_data[0].replace('\n', '') == country and count != 2:
                    count += 1
                    data_to_compare.append(test_data)
            except Exception as e:
                print(e)

        if '' in data_to_compare[0]:
            # ---> True means "This is the actual date info"
            return(data_to_compare[1], True)
        else:
            # ---> False means "This is info from past days"
            return(data_to_compare[0], False)


def setup(client):
    client.add_cog(Corona(client))