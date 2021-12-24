import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv('.env')

intents = discord.Intents().all()
client = commands.Bot(command_prefix= "!", intents = intents)
important_message_id = "None"
vote_dict = {}

@client.command()
async def nominate(ctx):
    proposition = ctx.message.content.split("!nominate ")[-1]
    if proposition in [vote_dict[key][0] for key in vote_dict.keys()]:
        await ctx.message.channel.send("This proposition has already been nominated.")
    else:
        await ctx.message.channel.send("%s has been nominated. React to this message with 👍 or 👎 to vote. 0 people have"
                                       " voted aye and 0 people have voted nay." % proposition)
        message = await ctx.message.channel.history().get(author__name='Anonymous Voting Bot')
        vote_dict[message.id] = [proposition, 0, 0, []]

@client.command()
async def dismiss(ctx):
    message = ctx.message.content.split("!dismiss ")[-1]
    if message in [vote_dict[key][0] for key in vote_dict.keys()]:
        for key in vote_dict.keys():
            if vote_dict[key][0] == message:
                await ctx.message.channel.send("You have successfully dismissed the nomination for %s." % message)
                del vote_dict[key]
                break
    else:
        await ctx.message.channel.send("No such nomination to be dismissed.")

@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    reaction_message_id = payload.message_id
    message = await channel.fetch_message(reaction_message_id)
    user = client.get_user(payload.user_id)
    reaction = payload.emoji
    if reaction_message_id in vote_dict.keys():
        if user not in vote_dict[reaction_message_id][3]:
            vote_dict[reaction_message_id][3].append(user)
            if str(reaction) == "👍":
                vote_dict[reaction_message_id][1] += 1
            elif str(reaction) == "👎":
                vote_dict[reaction_message_id][2] += 1
        await message.remove_reaction(reaction, user)
        await message.edit(content="%s has been nominated. React to this message with 👍 or 👎 to vote. %d people have"
                                            " voted aye and %d people have voted nay." % (vote_dict[reaction_message_id][0],
                                            vote_dict[reaction_message_id][1], vote_dict[reaction_message_id][2]))

client.run(os.getenv("DISCORD_BOT_TOKEN"))