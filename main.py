import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv('.env')

intents = discord.Intents().all()
client = commands.Bot(command_prefix= "!", intents = intents)
important_message_id = "None"
vote_initiated = False
@client.event
# This has no use apart from being a troubleshooting tool.
async def on_ready():
    print("Bot online")

@client.command()
async def nominate(ctx):
    global vote_initiated
    if vote_initiated == False:
        vote_initiated = True
        global voted_yes
        voted_yes = []
        global voted_no
        voted_no = []
        global member_amount
        member_amount = len(ctx.message.guild.members) - 1
        proposition = ctx.message.content.split("!nominate ")[-1]
        await ctx.message.channel.send("%s has been nominated. React to this message with 👍 or 👎 to vote." % proposition)
        # author__name here be whatever username you assign to your bot when creating it.
        message = await ctx.message.channel.history().get(author__name='Anonymous Voting Bot')
        global important_message_id
        important_message_id = message.id
    else:
        #TODO add capability to manage multiple active propositions.
        await ctx.message.channel.send("You cannot nominate a proposition until the current nomination has been resolved.")

@client.command()
async def dismiss(ctx):
    global vote_initiated
    if vote_initiated == True:
        await ctx.message.channel.send("You have successfully dismissed the current nomination.")
    else:
        await ctx.message.channel.send("No nomination to be dismissed.")
    vote_initiated = False


@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    reaction_message_id = payload.message_id
    message = await channel.fetch_message(reaction_message_id)
    user = client.get_user(payload.user_id)
    global voted_yes
    global voted_no
    emoji = payload.emoji
    if important_message_id != "None":
        if reaction_message_id == important_message_id and (user not in voted_yes) and (user not in voted_no):
            # The two emoji defined here can be anything as long as one is associated with each possible vote.
            if str(emoji) == "👍":
                voted_yes.append(user)
            elif str(emoji) == "👎":
                voted_no.append(user)
            if len(voted_yes) + len(voted_no) == member_amount:
                global vote_initiated
                vote_initiated = False
                # 0.75 of the full member list is an arbitrary conditon for resolving the vote. Other conditions connected to time or amount of votes can easily be substituted.
                if len(voted_yes) / member_amount >= 0.75:
                    await channel.send("This proposition passed.")
                else:
                    await channel.send("This proposition did not pass.")
    await message.remove_reaction(emoji, user)
# This uses a Discord generated when registering an application through the Discord Developer Portal (https://discord.com/developers/applications).
client.run(os.getenv("DISCORD_BOT_TOKEN"))
