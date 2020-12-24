import discord
from discord.ext import commands
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import asyncio


clientdb = MongoClient("YOUR.MONGO.DB.CLIENT")
DB = clientdb["Cluster0"]
class Corona(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.ok = True
        self.guild = ''

    @commands.Cog.listener()
    async def on_ready(self):
        print('cog.Corona ready')
        
        
    
    @commands.Cog.listener()
    async def on_message(self,ctx):
        if self.ok:
            self.guild = ctx.guild
            self.ok = False
            self.collection = DB[str(self.guild.id)]
            self.ctx = ctx
            self.client.loop.create_task(self.status(self.ctx))

    
    async def status(self,ctx):
        info = self.collection.find_one({'_id':self.guild.name})
        channel = await self.client.fetch_channel(info['command_channel'])
        if channel == 0:
            ctx.send('Error! first you must configure a channel, use !help')
        else:
            while True:
                e = self.get_information()
                embed=discord.Embed(title=e[0], color=0xf50000)
                embed.set_author(name="Coronavirus Update", icon_url="https://flespi.io/covid19/img/android-icon-192x192.a7ab640c.png")
                embed.add_field(name="Total Cases", value=e[1], inline=True)
                embed.add_field(name="New Cases", value=e[2], inline=True)
                embed.add_field(name="Active Cases", value=e[7], inline=True)
                embed.add_field(name="Total Deaths", value=e[3], inline=True)
                embed.add_field(name="Total Recovered", value=e[5], inline=True)
                embed.set_footer(text="Source: https://www.worldometers.info/coronavirus/")
                if info['msg_id'] == 0:
                    msg = await channel.send(embed=embed)
                    update = {'$set':{'msg_id':msg.id}}
                    self.collection.update_one({'msg_id':info['msg_id']},update)
                    info['msg_id'] = msg.id
                    # print('Query updated')
                else:
                    try:
                        msg = await channel.fetch_message(info['msg_id'])
                        await msg.edit(embed=embed)
                    except:
                        await channel.send('The previous message was eliminated')
                        msg = await channel.send(embed=embed)
                        info['msg_id'] = msg.id 
                        update = {'$set':{'msg_id':msg.id}}
                        self.collection.update_one({'msg_id':info['msg_id']},update)
                        
                

                await asyncio.sleep(6300 * 5)

    
    def get_information(self):
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
                if test_data[0].replace('\n','') == 'Argentina' and count != 2:
                    count += 1
                    data_to_compare.append(test_data)
            except Exception as e:
                print(e)               

        if '' in data_to_compare[0]:
            return(data_to_compare[1])
        else:
            return(data_to_compare[0])






            
        
def setup(client):
    client.add_cog(Corona(client))