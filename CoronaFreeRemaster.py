import discord
from discord.ext import commands
import random
import asyncio
import datetime
import os

TOKEN  = 'DISCORD.BOT.TOKEN'

offset = -datetime.timedelta(hours=3)
tzone = datetime.timezone(offset=offset,name='utc-3')
currentDT = datetime.datetime.now(tz=tzone)
# print(bcolors.WARNING+'A '+str(currentDT.year) + ", M " + str(currentDT.month) + ", D " +str(currentDT.day) + ", H " +str(currentDT.hour) + ", m" +str(currentDT.minute) + ", s" +str(currentDT.second)+bcolors.ENDC)

client = commands.Bot(command_prefix = '!')    



for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(TOKEN)

