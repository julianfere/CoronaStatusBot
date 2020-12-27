import discord
from discord.ext import commands
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import asyncio
from datetime import date,timedelta

clientdb = MongoClient("mongodb+srv://fere:LUNAteamo123@cluster0.wy2pb.mongodb.net/Cluster0?retryWrites=true&w=majority")
DB = clientdb["Cluster0"]
class Corona(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        self.guild = guild

    @commands.Cog.listener()
    async def on_ready(self):
        print('cog.Corona ready')



    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.user_id != self.client.user.id:
            print('User')
            if payload.emoji.name == '🔄':
                channel = self.client.get_channel(payload.channel_id)
                msg = await channel.fetch_message(payload.message_id)
                self.collection = DB[str(payload.guild_id)]
                guild = await self.client.fetch_guild(payload.guild_id)
                c = self.collection.find_one({'_id':guild.name})
                c = c['country']
                await msg.remove_reaction(payload.emoji,payload.member)
                embed_a = discord.Embed(title='Updating please wait...',color=0xf50000)
                embed_a.set_author(name="Coronavirus Update", icon_url="https://flespi.io/covid19/img/android-icon-192x192.a7ab640c.png")
                await msg.edit(embed=embed_a)
                e,warning = self.get_information(c)
                embed=discord.Embed(title=e[0], color=0xf50000)
                embed.set_author(name="Coronavirus Update", icon_url="https://flespi.io/covid19/img/android-icon-192x192.a7ab640c.png")
                embed.add_field(name="Total Cases", value=e[1], inline=True)
                embed.add_field(name="New Cases", value=e[2], inline=True)
                embed.add_field(name="Active Cases", value=e[7], inline=True)
                embed.add_field(name="Total Deaths", value=e[3], inline=True)
                embed.add_field(name="Total Recovered", value=e[5], inline=False)
                if not warning: 
                    embed.add_field(name="Date",value=date.today().strftime("%d/%m/%Y"))
                else:
                    yesterday = (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")
                    embed.add_field(name='Date',value=yesterday)
                await msg.edit(embed=embed)

    @commands.command(pass_context=True,aliases=['u'])
    async def update(self,ctx):
        command = ctx.message
        self.collection = DB[str(ctx.guild.id)]
        info = self.collection.find_one({'_id':ctx.guild.name})
        e,warning = self.get_information(info['country'])
        embed=discord.Embed(title=e[0], color=0xf50000)
        embed.set_author(name="Coronavirus Update", icon_url="https://flespi.io/covid19/img/android-icon-192x192.a7ab640c.png")
        embed.add_field(name="Total Cases", value=e[1], inline=True)
        embed.add_field(name="New Cases", value=e[2], inline=True)
        embed.add_field(name="Active Cases", value=e[7], inline=True)
        embed.add_field(name="Total Deaths", value=e[3], inline=True)
        embed.add_field(name="Total Recovered", value=e[5], inline=False)
        if not warning: 
            embed.add_field(name="Date",value=date.today().strftime("%d/%m/%Y"))
        else:
            yesterday = (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")
            embed.add_field(name='Date',value=yesterday)
        embed.set_footer(text="Source: https://www.worldometers.info/coronavirus/")
        if info['msg_id'] == 0:
            msg = await ctx.send(embed=embed)
            update_info = {'$set':{'msg_id':msg.id}}
            self.collection.update_one({'msg_id':info['msg_id']},update_info)
        else:
            channel = self.client.get_channel(info['command_channel'])
            try:
                msg = await channel.fetch_message(info['msg_id'])
            except Exception as e:
                print('Se rompe acá?',e)
                msg = await channel.send(embed=embed)
                update_info = {'$set':{'msg_id':msg.id}}
                self.collection.update_one({'msg_id':info['msg_id']},update_info)

            await msg.edit(embed=embed)     
        await msg.add_reaction('\U0001F504')
        await asyncio.sleep(5)
        await command.delete()
    
    def get_information(self,country):
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
                if test_data[0].replace('\n','') == country and count != 2:
                    count += 1
                    data_to_compare.append(test_data)
            except Exception as e:
                print(e)               

        if '' in data_to_compare[0]:
            return(data_to_compare[1],True) #---> True means "This is the actual date info"
        else:
            return(data_to_compare[0],False) #---> False means "This is info from past days"






            
        
def setup(client):
    client.add_cog(Corona(client))