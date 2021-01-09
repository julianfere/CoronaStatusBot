import discord
from discord.ext import commands
from pymongo import MongoClient
import asyncio
clientdb = MongoClient(CLIENT.LINK)
DB = clientdb[CLUSTER.NAME]


class Config(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Listo')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        info = {
            '_id': guild.name,
            'command_channel': 0,
            'data': {}
        }

        collection = DB[str(guild.id)]
        collection.insert_one(info)
        print(f'Joined in {guild.name}')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        collection = DB[str(guild.id)]
        collection.drop()
        print(f'Kicked from {guild.name}')

    @commands.command(aliases=['c'])
    async def config(self, ctx, channel: discord.TextChannel, msg):
        '''
        !config #Channel "Country" to set the channel
        '''
        command = ctx.message
        if ctx.message.author.guild_permissions.manage_messages:
            collection = DB[str(ctx.message.guild.id)]
            infodb = collection.find_one({'_id': ctx.message.guild.name})
            info = {'$set': {'command_channel': channel.id}}
            if infodb is None:
                collection.update_one({'command_channel': 0}, info)
            else:
                collection.update_one(
                    {'command_channel': infodb['command_channel']}, info)

            msj = await ctx.send(f'Channel set to <#{channel.id}>')
            await asyncio.sleep(8)
            await msj.delete()
        else:
            ctx.send('You dont have permissions to do that :(')

        await asyncio.sleep(8)
        await command.delete()


def setup(client):
    client.add_cog(Config(client))
