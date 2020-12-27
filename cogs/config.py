import discord
from discord.ext import commands
from pymongo import MongoClient
import asyncio
clientdb = MongoClient("mongodb+srv://fere:LUNAteamo123@cluster0.wy2pb.mongodb.net/Cluster0?retryWrites=true&w=majority")
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
        command = ctx.message
        if ctx.message.author.guild_permissions.manage_messages:
            collection = DB[str(ctx.message.guild.id)]
            infodb = collection.find_one({'_id':ctx.message.guild.name})
            info = {'$set':{'command_channel':channel.id}}
            infoc = {'$set':{'country':msg}}
            if infodb is None:
                collection.update_one({'command_channel':0},info)
                collection.update_one({'country':''},infoc)
            else:
                collection.update_one({'command_channel':infodb['command_channel']},info)
                collection.update_one({'country':infodb['country']},infoc)
                
            msj = await ctx.send(f'Channel set to <#{channel.id}> and updates from "{msg}"')
            await asyncio.sleep(8)
            await msj.delete()
        else:
            ctx.send('You dont have permissions to do that :(')
        
        await asyncio.sleep(8)
        await command.delete()

        

    

def setup(client):
    client.add_cog(Config(client))