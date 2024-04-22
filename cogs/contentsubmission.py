import discord
from discord import option
from discord.ext import commands
from discord.commands import slash_command
import json 
from random import randint

server = [1226452892899217461]
admins = [675238101253226496, 844043507072237588]

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

class contentids():
    def __init__(self, NotFulfilled, initialdata, subject, link, userdata, interaction, submissionid=None):
        self.notfulfilled = NotFulfilled
        self.initialdata = initialdata
        self.link = link
        self.subject = subject
        self.userdata = userdata
        self.interaction = interaction
        self.submissionid = submissionid
        
    async def submissionidwriter(self):
        print(self.initialdata)
        subjects = self.initialdata['Subjects']
        NotFulfilled = True
        
        while NotFulfilled:
            submissionid = random_with_N_digits(5)
            if str(submissionid) not in str(subjects):
                if self.userdata[f'{self.interaction.user.id}']['content'] == None:
                    self.userdata[f'{self.interaction.user.id}']['content'] = [{submissionid:self.link}]

                elif self.userdata[f'{self.interaction.user.id}']['content'] != None:
                    self.userdata[f'{self.interaction.user.id}']['content'].append({submissionid:self.link})

                for subjectindex in range(len(subjects)):
                    if ''.join(subjects[subjectindex].keys()) == self.subject:
                        if subjects[subjectindex][self.subject][1]['content'] == None:
                            subjects[subjectindex][self.subject][1]['content'] = [{submissionid:self.link, 'userid': self.interaction.user.id, 'name':f"{self.userdata[f'{self.interaction.user.id}']['firstname']} {self.userdata[f'{self.interaction.user.id}']['lastname']}", 'accepted':False}]
                            break 
                        elif subjects[subjectindex][self.subject][1]['content'] != None:
                            subjects[subjectindex][self.subject][1]['content'].append({submissionid:self.link, 'userid': self.interaction.user.id, 'name':f"{self.userdata[f'{self.interaction.user.id}']['firstname']} {self.userdata[f'{self.interaction.user.id}']['lastname']}", 'accepted':False})
                            break 
                self.submissionid = submissionid
                self.initialdata['Subjects'] = subjects
                NotFulfilled = False


class contentchecker(discord.ui.View):
    def __init__(self, bot, link, subject, channel=None):
        self.bot = bot
        self.link = link
        self.subject = subject
        self.channel = channel
        super().__init__()

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(content="Bludwin, you took too long to respond, all buttons are disabled.", view=self)
    
    
    @discord.ui.button(label="Check", row=0, style=discord.ButtonStyle.success)
    async def accept_button_callback(self, button, interaction):
        self.disable_all_items()
        embed = discord.Embed(
                title="Content Submission has sent for approval",
                description=f"Your content has been submitted to our administrators to verify it's quality. You'll receive a token to access other content, if it's approved.",
                color=discord.Colour.from_rgb(255,255,255))
        embed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')
        await interaction.response.send_message(embed=embed)

        with open('contentdata.json','r') as contentdataread:
            initialdata = json.load(contentdataread)
        with open ('userdata.json','r') as userdataread:
            userdata = json.load(userdataread)
        
        
        subid = contentids(NotFulfilled=True, initialdata=initialdata, userdata=userdata, subject=self.subject, interaction=interaction, link=self.link)
        await subid.submissionidwriter()

        with open('contentdata.json','w') as contentdatawrite:
            json.dump(subid.initialdata, contentdatawrite)
        with open('userdata.json', 'w') as userdatawrite:
            json.dump(subid.userdata, userdatawrite)
        
        self.embed = discord.Embed(
                title="Content Submission Request",
                description=f"<@!{interaction.user.id}> requested to submit the content {self.link}. \n **The ID is** ```{subid.submissionid}```",
                color=discord.Colour.from_rgb(255,255,255))
        self.embed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')
        
        for x in range(0,(len(admins))):
            name = self.bot.get_user(admins[x])
            if name is None:
                name = self.bot.fetch_user(admins[x])
            await name.send(embed=self.embed)

    @discord.ui.button(label="Abort", row=0, style=discord.ButtonStyle.danger)
    async def deny_button_callback(self, button, interaction):
        self.disable_all_items()
        

class categorycreation(discord.ui.View):
    def __init__(self, bot, subjectname, link):
        self.bot = bot
        self.subjectname = subjectname
        self.link = link 
        super().__init__()

    async def on_timeout(self):
        self.disable_all_items()
    
    @discord.ui.button(label="Yes", row=0, style=discord.ButtonStyle.success)
    async def accept_button_callback(self, button, interaction):
        self.disable_all_items()
        
        perms = discord.PermissionOverwrite(send_messages=False, view_channel=True, use_application_commands = True, read_message_history=True, read_messages = True)
        guild = self.bot.get_guild(server[0])
        role = await guild.create_role(name=f'{self.subjectname}')
        channel = await guild.create_text_channel(name=f'{self.subjectname.capitalize()}', category=guild.by_category()[1][0], overwrites={role:perms})
        
        with open("contentdata.json","r") as file:
            jsonData = json.load(file)
            
        jsonData['Subjects'].append(({str(self.subjectname):[{'role_id': role.id},{'content': None},{'channel_id':channel.id}]}))
        
        with open('contentdata.json','w') as file:
            json.dump(jsonData, file)
        await interaction.response.send_message(f"The category has now been created", ephemeral=True)
        
        embed = discord.Embed(
                    title="Content Submission",
                    description=f"Thanks for submitting the content. Please make the document view only and add the email: ```sourcev1bot@gmail.com``` \n Make sure that your document is up to date as it cannot be modified and this will be the final submission that we will use to assess quality, determining your access to other resources. \n Once you have added the email, press the **Check** button, within the next **minute** so we can access the document to assess it's validity, and you'll then get a direct message to confirm if it passes the quality control test. After being validated, you'll then have be rewarded with a token that you can use to get access to other documents of a single subject. /n For example, if you submit an english essay, you'll be rewarded with a token that can be used to access science notes that someone might have posted. If you have changed your mind, or have another reason to cancel, press the abort button.",
                    color=discord.Colour.from_rgb(255,255,255))
        embed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')

        await interaction.followup.send(embed=embed, view=contentchecker(bot=self.bot, link=self.link, subject=self.subjectname))

    @discord.ui.button(label="Abort", row=0, style=discord.ButtonStyle.danger)
    async def deny_button_callback(self, button, interaction):
        self.disable_all_items()
        await interaction.response.send_message(f"You have succesfully aborted the creation of the category", ephemeral=True)


class contentsubmission(commands.Cog):
    def __init__(self, bot, reason=None):
        self.bot = bot
        self.reason = reason
    
    @staticmethod 
    def subjectAutocomplete(self: discord.AutocompleteContext):
        with open("contentdata.json","r") as file:
            jsonData = json.load(file)
        subjectsdata = jsonData["Subjects"]
        return [''.join(subject.keys()) for subject in subjectsdata]
    
    @staticmethod 
    def returnsubmission(self: discord.AutocompleteContext):
        return ['Accepted','Rejected']
    
    @slash_command(guild_ids=server, name='contentsubmission', description='Send in your resources to gain access to other resources!')
    @option(name="subject", description="Your selected subject for this content to be submitted in", autocomplete=subjectAutocomplete)
    @option(name='link', description='A link to the google document with your resource', required=True )
    async def contentsubmission(self, ctx: discord.ApplicationContext, subject, link):
        with open("contentdata.json","r") as file:
            jsonData = json.load(file)
        listsubjects = [''.join(subject.keys()) for subject in jsonData["Subjects"]]
        if subject not in listsubjects:
            embed = discord.Embed(
                    title="Content Submission",
                    description=f"Your subject doesn't seem to exist yet. Would you like to create a new category for it?",
                    color=discord.Colour.from_rgb(255,255,255))
            embed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')
            await ctx.respond(embed=embed, view=categorycreation(bot=self.bot, subjectname=f'{subject}', link=link))
        
        else: 
            embed = discord.Embed(
                    title="Content Submission",
                    description=f"Thanks for submitting the content. Please make the document view only and add the email: ```sourcev1bot@gmail.com``` \n Make sure that your document is up to date as it cannot be modified and this will be the final submission that we will use to assess quality, determining your access to other resources. \n Once you have added the email, press the **Check** button, within the next **minute** so we can access the document to assess it's validity, and you'll then get a direct message to confirm if it passes the quality control test. After being validated, you'll then have be rewarded with a token that you can use to get access to other documents of a single subject. /n For example, if you submit an english essay, you'll be rewarded with a token that can be used to access science notes that someone might have posted. If you have changed your mind, or have another reason to cancel, press the abort button.",
                    color=discord.Colour.from_rgb(255,255,255))
            embed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')

            await ctx.respond(embed=embed, view=contentchecker(bot=self.bot, link=link, subject=subject))
    
    @slash_command(guild_ids=server, name='returnsubmission', description='Approve or Reject a resource submitted by a user with the submissionid')
    @option(name='submissionid', description='The submissionid of the content that you are referring to', required=True)
    @option(name='submissionresult', description='An accepted or rejected value that determines if the submission will be listed', autocomplete=returnsubmission, required=True)
    @option(name='tokens', description='The quantity of tokens to reward the content poster with')
    @option(name='reason', description='The reason for acceptance or rejection, typically the latter')
    async def returnsubmission(self, ctx:discord.ApplicationContext, submissionid, submissionresult, tokens, reason):
        submissionresult = True if submissionresult == 'Accepted' else False
        if ctx.author.id not in admins:
            await ctx.respond('You are not an administrator with permissions to return submission results and provide tokens.', ephemeral=True)
            return 
        else:
            if submissionresult == True:
                with open('contentdata.json','r') as f:
                    initcontentdata = json.load(f)
                    contentdata = initcontentdata['Subjects']
                for subjectindex in range(len(contentdata)):
                    subject = contentdata[subjectindex]
                    if subject[''.join(subject.keys())][1]['content'] == None and subjectindex == len(contentdata)-1:
                        ctx.respond('''The submissionID doesn't seem to exist, are you sure you entered it correctly?''', ephemeral=True)
                    if subject[''.join(subject.keys())][1]['content'] != None:
                        for listingindex in range(len(subject[''.join(subject.keys())][1]['content'])):
                            listing = subject[''.join(subject.keys())][1]['content'][listingindex] 
                            if submissionid in listing.keys():
                                if listing['accepted'] == True:
                                    await ctx.respond('Another administrator has already give the go ahead to this submission!', ephemeral=True)
                                    return
                                #change the contentdata with submissionid to True (accepted) and get userID
                                userid = listing['userid']
                                listing['accepted'] = True
                                with open('contentdata.json','w') as writecontent:
                                    initcontentdata['Subjects'] = contentdata
                                    json.dump(initcontentdata, writecontent)

                                #add tokens to users balance and direct message user with embed
                                with open('userdata.json','r') as userdatas:
                                    modifiedtokensdata = json.load(userdatas)
                                    if modifiedtokensdata[f'{userid}']['tokens'] == None:
                                        modifiedtokensdata[f'{userid}']['tokens'] = int(tokens)
                                    else:
                                        modifiedtokensdata[f'{userid}']['tokens'] += int(tokens)
                                with open('userdata.json','w') as usersdata:
                                    json.dump(modifiedtokensdata,usersdata)
                                    
                                #fetch user and send embed
                                user = self.bot.get_user(userid)
                                if user is None:
                                    user = self.bot.fetch_user(userid)
                                    
                                contentresultsembed = discord.Embed(
                                        title="Content Submission Results",
                                        description=f"""**Hey {modifiedtokensdata[str(userid)]['firstname']}**, thanks so much for your recent submission of content. Your submission with the submission id of: **{submissionid}** has been accepted
                                        and tokens of quantity {tokens} has been added to your balance. \n **You can now use the command:** ```/getaccess subject:``` **AND** ```/balance``` \n These commands respectively, will allow you to get access to a subject for a specific price, and check the quantity of tokens you have in your balance. The reason which justified the token quantity, was given as: ```{reason}.```""",
                                        color=discord.Colour.from_rgb(255,255,255))
                                contentresultsembed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')
                                await user.send(embed=contentresultsembed)

                                #post to channel that has already been created

                                contentsubmissionembed = discord.Embed(
                                        title=f"""Content Submission by {modifiedtokensdata[str(userid)]["firstname"]} {modifiedtokensdata[str(userid)]["lastname"]}""",
                                        description=f"Link: {listing[submissionid]} \n SubmissionID: {submissionid}",
                                        color=discord.Colour.from_rgb(255,255,255))
                                contentsubmissionembed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')
                                channelid = subject[''.join(subject.keys())][2]['channel_id']
                                channel = self.bot.get_channel(channelid)
                                await channel.send(embed=contentsubmissionembed)
                                await ctx.respond(f"""Sucessfully accepted the submission, of ID {submissionid} and posted by {listing['name']}. Token count of {tokens} has been added to users balance, and the content has bene posted as an embed in the channel""")
                                return
                            if submissionid not in listing.keys() and subjectindex == len(contentdata)-1 and listingindex == len(subject[''.join(subject.keys())][1]['content'])-1:
                                await ctx.respond('''The submissionID doesn't seem to exist, are you sure you entered it correctly?''', ephemeral=True)
                                return

                                    
            elif submissionresult == False:
                with open('userdata.json','r') as userdatas:
                    modifiedtokensdata = json.load(userdatas)
                with open('contentdata.json','r') as f:
                    contentdata = json.load(f)['Subjects']
                #iterate through subject in the subjects 
                for subjectindex in range(len(contentdata)):
                    subject = contentdata[subjectindex][''.join(contentdata[subjectindex].keys())]
                    #iterate through each listing in subject
                    if subject[1]['content'] != None:
                        for listingindex in range(len(subject[1]['content'])):
                            listing = subject[1]["content"][listingindex]
                            #check if each listing has submissionid 
                            if submissionid in listing.keys():
                                userid = listing['userid']
                                user = self.bot.get_user(userid)
                                if user is None:
                                    user = self.bot.fetch_user(userid)

                                #establish embed
                                contentresultsembed = discord.Embed(
                                                title="Content Submission Results",
                                                description=f"""**Hey {modifiedtokensdata[str(userid)]['firstname']}**, thanks so much for your recent submission of content. Unfortunately, your submission with the SubmissionID of: **{submissionid})** has been rejected, and the reason which justified the rejection, was given as: ```{reason}.```""",
                                                color=discord.Colour.from_rgb(255,255,255))
                                contentresultsembed.set_author(name='Source', icon_url='https://res.cloudinary.com/drt9lxvky/image/upload/v1712798628/sourcev1.png_uzc8zh.jpg')
                                await user.send(embed=contentresultsembed)
                                await ctx.respond('''The submission continues to remain as unaccepted and will not grant tokens or be uploaded to the respective channel''', ephemeral=True)
                                return
                            elif submissionid not in listing.keys() and subjectindex == len(contentdata)-1 and listingindex == len(subject[1]['content'])-1:
                                await ctx.respond('''The submission does not seem to exist, are you sure you entered it correctly?''', ephemeral=True)
                            

                
                            
def setup(bot):
    bot.add_cog(contentsubmission(bot))