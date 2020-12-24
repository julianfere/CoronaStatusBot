import discord
from discord.ext import commands
from pymongo import MongoClient
import asyncio
clientdb = MongoClient("YOUR.MONGO.DB.CLIENT")
DB = clientdb["Cluster0"]

class Config(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Listo')
    
    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        info = {
            '_id': guild.name,
            'command_channel':0,
            'msg_id':0,
            'country':''
        }
        collection = DB[str(guild.id)]
        collection.insert_one(info)
        print(f'Joined in {guild.name}')

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        collection = DB[str(guild.id)]
        collection.drop()
        print(f'Kicked from {guild.name}')
    
    @commands.command(aliases = ['c'])
    async def config(self,ctx,channel:discord.TextChannel,msg):
        '''
        !config #Channel "Country" to set the channel and the country for post updates
        '''
        if ctx.message.author.guild_permissions.manage_messages:
            collection = DB[str(ctx.message.guild.id)]
            info = {'$set':{'command_channel':channel.id}}
            infoc = {'$set':{'country':msg}}
            collection.update_one({'command_channel':0},info)
            collection.update_one({'country':''},infoc)
            msj = await ctx.send(f'Channel set to <#{channel.id}> and updates from "{msg}"')
        else:
            print('pito')

    

def setup(client):
    client.add_cog(Config(client))