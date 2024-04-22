### An LJT Development
## Mad Progress
# Imports
import discord
import json 

with open('discordtoken.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)

bot = discord.Bot(intents=discord.Intents.all(), activity=discord.Activity(type=discord.ActivityType.streaming, name='Source Hub'))

@bot.event 
async def on_ready():
    print(f'We have logged on as {bot.user}')   

extensions = [# load cogs
    'cogs.nameverification','cogs.contentsubmission', 'cogs.tokenusage'
    
]

if __name__ == '__main__': # import cogs from cogs folder   
    for extension in extensions:
        bot.load_extension(extension)

bot.run(json_object['token'])

