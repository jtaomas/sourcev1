import discord
from discord import option
from discord.commands import slash_command
from discord.ext import commands
import json

from discord.ui.item import Item

server = [1226452892899217461]
admins = [675238101253226496, 844043507072237588]

subjectscost = {
    "English": 2,
    "Mathematics": 2,
    "Science": 3,
    "Geography": 1,
    "PDHPE": 1,
    "History": 1,
    "IPT": 3,
    "Food Tech": 1,
    "Graphics Tech": 1,
    "Engineering": 2,
    "DAT": 2,
    "Commerce": 2,
    "History Elective": 1,
    "German": 1,
    "Latin": 1,
    "Indonesian": 1,
    "French": 1,
    "Japanese": 1,
    "Visual Arts": 1,
    "Music": 1
}


class tokenusage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
    @staticmethod 
    def subjectAutocomplete(self: discord.AutocompleteContext):
        with open("contentdata.json","r") as file:
            jsonData = json.load(file)
        subjectsdata = jsonData["Subjects"]
        return [''.join(subject.keys()) for subject in subjectsdata]
    
    @slash_command(guild_ids=server, name='balance', description='Your token balance')
    async def balance(self, ctx):
        with open('userdata.json', 'r') as userdatajson:
            userdata = json.load(userdatajson)
        tokens = userdata[str(ctx.author.id)]["tokens"]
        embed = discord.Embed(
                    title="Token Balance",
                    description=f"**Your balance:** \n Tokens: {tokens} \n Submissions: {len(userdata[str(ctx.author.id)]['content'])}",
                    color=discord.Colour.from_rgb(255,255,255))
        embed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')
        await ctx.respond(embed=embed)
    
    @slash_command(guild_ids=server, name='getaccess', description='Use your tokens to get access to a channel!')
    @option(name="subject", description="Your selected subject to acquire access to", autocomplete=subjectAutocomplete)
    async def getaccess(self, ctx, subject):
        with open('userdata.json', 'r') as userdatajson:
            userdata = json.load(userdatajson)
        with open('contentdata.json', 'r') as contentdatajson:
            contentdata = json.load(contentdatajson)   
        tokens = userdata[str(ctx.author.id)]["tokens"]
        subjects = []
        for subjectcategory in contentdata['Subjects']:
            subjects.append(''.join(subjectcategory.keys()))
        if subject.capitalize() not in subjects:
            await ctx.respond(f'''The subject {subject} doesn't seem to have any content posted in it yet, or doesn't exist. Try something under the autocomplete which will show you avaliable subjects with content.''', ephemeral=True)
            return
        else: 
            #check if token quantity is sufficient 
            if tokens < subjectscost[subject.capitalize()]:
                await ctx.respond(f'''The subject {subject.capitalize()} requires at least {subjectscost[subject.capitalize()]} to access. You only have {tokens} tokens in your balance.''', ephemeral=True)
                return
            #remove tokens from balance if sufficient 
            elif tokens >= subjectscost[subject.capitalize()]:
                tokens = tokens - (subjectscost[subject.capitalize()])
                userdata[str(ctx.author.id)]["tokens"] = tokens
                with open('userdata.json','w') as f:
                    json.dump(userdata, f)
                #give access to channel via role
                roleid = None
                subjectind = None
                for subjectcatindex in range(len(contentdata['Subjects'])):
                    try:
                        contentdata['Subjects'][subjectcatindex][subject.capitalize()][0]['role_id']
                        roleid = contentdata['Subjects'][subjectcatindex][subject.capitalize()][0]['role_id']
                        subjectind = subjectcatindex
                    except: 
                        pass

                guild = self.bot.get_guild(server[0])
                print(roleid)
                role = guild.get_role(roleid)
                print(role)
                await ctx.author.add_roles(role, reason=f'Spent tokens to acquire role')
                await ctx.respond(f'''You have successfully acquired the role to access the subject {subject.capitalize()}. You should now be able to access the channel <#{contentdata['Subjects'][subjectind][subject.capitalize()][2]['channel_id']}>''', ephemeral=True)

    
def setup(bot):
    bot.add_cog(tokenusage(bot))
