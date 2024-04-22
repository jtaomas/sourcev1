import discord
from discord.client import *
from discord.commands import slash_command
from discord.ext import commands
import json

from discord.ui.item import Item

server = [1226452892899217461]
admins = [675238101253226496, 844043507072237588]

users = {}

class account():
    def __init__(self, firstname, lastname, email, accountstatus, subjects=None, tokens=None, accessablesubjects=None, content=None):
        self.subjects = subjects
        self.tokens = tokens
        self.accessablesubjects = accessablesubjects
        self.firstname = firstname
        self.lastname = lastname
        self.email = email 
        self.accountstatus = accountstatus
        self.content = content  

    def name(self, firstname, lastname):
        return(f'{firstname} {lastname}')
    
class acceptanceButtons(discord.ui.View):
    def __init__(self, firstname, lastname, user, userid, guild, bot, email):
        super().__init__()
        self.firstname = firstname
        self.lastname = lastname
        self.guild = guild
        self.user = user
        self.userid = userid
        self.bot = bot
        self.email = email
    
    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(content="Bludwin, you took too long to respond, all buttons are disabled.", view=self)

    @discord.ui.button(label="Accept", row=0, style=discord.ButtonStyle.success)
    async def accept_button_callback(self, button, interaction):
        if self.user.id in admins:
            await interaction.response.send_message(f"It looks like you're an admin and already have been verified with full access.")
        else:
            responds = Verification(firstname=self.firstname, lastname=self.lastname, user=self.user, userid=self.userid, guild=self.guild, bot=self.bot, email=self.email, acceptance=True)
            await self.user.edit(nick=f'{self.firstname} {self.lastname}')
            await responds.sendresult()
            await interaction.response.send_message(f"{self.firstname} {self.lastname} has been accepted into Source", ephemeral=True)

    @discord.ui.button(label="Deny", row=0, style=discord.ButtonStyle.danger)
    async def deny_button_callback(self, button, interaction):
        respond = Verification(firstname=self.firstname, lastname=self.lastname, user=self.user, userid=self.userid, guild=self.guild, bot=self.bot, email=self.email, acceptance=False)
        if self.user.id in admins:
            await interaction.response.send_message(f"It looks like you're an admin and already have access to this channel.")
        else:
            await self.user.edit(nick=f'{self.firstname} {self.lastname}')
            await respond.sendresult()
            await interaction.response.send_message(f"{self.firstname} {self.lastname} has been denied access into Source", ephemeral=True)
        

class Verification(commands.Cog):
    def __init__(self, bot, firstname=None, lastname=None, guild=None, user=None, userid=None, email=None, acceptance=None):
        self.bot = bot
        self.firstname = firstname
        self.lastname = lastname
        self.guild = guild
        self.user = user
        self.userid = userid
        self.bot = bot
        self.email = email
        self.acceptance = acceptance
    
    @slash_command(guild_ids=server, name='nameverification', description='Verify your name to gain access!')
    async def nameverification(self, ctx, firstname: discord.Option(description="Your firstname", required = True), lastname:discord.Option(description="Your last name", required = True), email:discord.Option(description="Your education email address", required = True)):
        with open('./userdata.json','r') as f:
            data = json.load(f)
            try:
                data[str(ctx.author.id)]
                await ctx.respond(f'''Hey {firstname}, you already have an account, if you need help with changing data send a DM to an administrator.''', ephemeral=True)
                return 
            except:
                firstname = firstname.capitalize()
                lastname = lastname.capitalize()
                await ctx.respond(f'''Hey {firstname}, thanks for applying to join the Source community, your request is being processed and we'll DM you a response on your application''', ephemeral=True)
                print(ctx.author)
                if '@education' in email or '@gov' in email:
                        
                    for x in range(0,(len(admins))):
                        name = self.bot.get_user(admins[x])
                        if name is None:
                            name = self.bot.fetch_user(admins[x])
                        
                        self.embed = discord.Embed(
                            title="User Join Request",
                            description=f"**{firstname} {lastname}** has requested to join the SourceV1 community. \n **Education Email Address:** {email}",
                            color=discord.Colour.from_rgb(255,255,255))
                        self.embed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')

                        await name.send(embed=self.embed, view=acceptanceButtons(firstname=firstname, lastname=lastname, userid=ctx.author.id, guild=ctx.guild, user=ctx.author, email=email, bot=self.bot))
                else:
                    await ctx.respond(f'''Hey {firstname}, your email doesn't seem to be an education address or valid.''', ephemeral=True)

    async def sendresult(self):
        
        user = self.bot.get_user(self.userid)
        if user is None:
            user = self.bot.fetch_user(self.userid)
        result = 'accepted' if self.acceptance == True else 'rejected'

        embed = discord.Embed(
            title="SourceV1 Application Results",
            description=f"Hi {self.firstname}, thanks for your request to join the SourceV1 community, we appreciate your interest to join and have taken a look at the credentials you've given us to see if you meet our criteria. \n\n We've received your application, and your request has been **{result}** by our adminstration team. \n\n **If you've been accepted**, submit some content for tokens in <#1227565696628822077>. If you have any queries, concerns or questions, feel free to direct message anyone within our administration team.",
            color=discord.Colour.from_rgb(255,255,255))
        embed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')
        
        await user.send(embed=embed)
            
        if self.acceptance:
            with open('userdata.json','r') as f:
                userdata = json.load(f)
            verifiedrole = self.guild.get_role(1228539719952896080)
            await self.user.add_roles(verifiedrole)
            userdata[f'{self.userid}'] = account(firstname=self.firstname, lastname=self.lastname, accountstatus=self.acceptance, email=self.email).__dict__
            with open('userdata.json', 'w') as filez:
                json.dump(userdata, filez)
        
    
def setup(bot):
    bot.add_cog(Verification(bot))
