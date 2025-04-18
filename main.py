import discord
import os
import json
from collections import defaultdict
from discord.ext import commands
#from flask import Flask
#import threading
import time
import string
from datetime import datetime

cost_modifier = 1 #For example 1 for 1$ per word or 3 for 3 times the price
save_interval = 600 #In seconds

def save_database(data):
#    while True:
#        now = datetime.now()
    with open("data.json", "w") as fp:
        json.dump(data, fp)
#        print("Saved data to file at " + str(now))
#        time.sleep(save_interval)

def load_database():
	dictionary = {}
	with open("data.json", "r") as fp:
		dictionary = json.load(fp)
	return dictionary

user_word_counts = load_database()

intents = discord.Intents.default()
try:
    intents.message_content = True
    print("Using message content - make sure it's enabled in Discord Developer Portal")
except:
    print("Message content intent not available - some features may be limited")

bot = commands.Bot(command_prefix='/', intents=intents)


phrases = []
#phrases = ["fuck", "shit", "cunt", "kys", "bitch", "dickhead", "dick", "asshole", "ass", "bastard", "hawk tuah", "pussy", "moist", "halgean", "aeriki", "penis", "sex", "cock", "vagina", "porn", "bahoosay", "poosay", "lindau", "tandong", "tanderium", "ooo.ooo", "aaa.aaa"]


def load_swear_words():
    with open("swear_words.txt", "r") as file:
        phrases = file.read().split("\n")
    #del phrases[-1]
    #print(phrases)
    return phrases

phrases = load_swear_words()
print(phrases)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Loaded {sum(len(words) for words in user_word_counts.values())} word counts from database")

@bot.event
async def on_message(message):
    #print("1")
    if message.author == bot.user:
        return

    await bot.process_commands(message)
    #print("2")

    message_lower = message.content.lower()
    message_lower = message_lower.translate(str.maketrans('', '', string.punctuation))
    #print(message_lower.split())

    if "/add_word" in message_lower or "/remove_word" in message_lower:
        return

    for word in message_lower.split():
        #print("3")

        try:
            index = phrases.index(word)
            #print(word)
            #print("4")
            count = message_lower.count(word)
            await message.channel.send(word + " is not nice to say! \n You owe Panda. ☹️")
            user_id = str(message.author.id)
            user_word_counts[user_id] += count
            save_database(user_word_counts)
            break

        except ValueError:
            #print(word)
            pass

@bot.command(name="swear_help")
async def help_command(ctx):
    if ctx.author.guild_permissions.administrator:
        await ctx.send("These are the commands you can run: \n /swear_help \n /owe (username) \n /tax (value) \n /add_word (word) \n /remove_word (word) \n /add_debt (user) (amount) \n /remove_debt (user) (amount)")
    else:
        await ctx.send("These are the commands you can run: \n /swear_help \n /owe (username)")

@bot.command(name="add_debt")
async def add_debt_command(ctx, user: str = None, add: str = None):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You don't have permissions to run this command.")
        return
    if user == None:
        await ctx.send("Please provide user.")
        return
    if add == None:
        await ctx.send("Please provide a number")
        return
    try:
        add = int(add)
    except:
        await ctx.send("Please provide a number.")
    if add <= 0:
        await ctx.send("Please provide an integer that is bigger than 0.")
        return

    global user_word_counts

    if user in user_word_counts:
        user_word_counts[user] += add
        return

    #If the user isn't in the database already we add them to the database
    user_word_counts[user] = add
    return

@bot.command(name="remove_debt")
async def pay_debt_command(ctx, user: str = None, remove: str = None):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You don't have permissions to run this command.")
        return
    if user == None:
        await ctx.send("Please provide user.")
        return
    if remove == None:
        await ctx.send("Please provide a positive number more than 0.")
        return
    try:
        remove = int(remove)
    except:
        await ctx.send("Please provide a number.")
    if remove <= 0:
        await ctx.send("Please provide an integer that is bigger than 0.")

    global user_word_counts

    if user not in user_word_counts:
        await ctx.send("User has no debt to be payed off.")
        return
    if remove > user_word_counts[user]:
        await ctx.send("Can't remove more debt than the user has.")
        return

    user_word_counts[user] -= remove
    return

@bot.command(name="tax")
async def change_tax_command(ctx, tax: str = None):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You don't have permissions to run this command.")
        return

    global cost_modifier
    if tax is None:
        await ctx.send("Please provide a value. Usage: /tax (value)")
        return

    try:
        tax = int(tax)
    except:
        await ctx.send("Please provide an integer.")
        return

    if tax > 10:
        await ctx.send("Please provide a number less than 10")
        return

    if tax <= 0:
        await ctx.send("Please provide a positive number that is more than 0.")
        return

    cost_modifier = tax
    await ctx.send("Cost modifier changed to " + str(tax))
    return

@bot.command(name="add_word")
async def add_word_command(ctx, word: str = None):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You don't have permissions to run this command.")
        return

    global phrases
    if word is None:
        await ctx.send("Please provide a word. Usage: /add_word word")
        return

    word_lower = word.lower()
    phrases.append(word_lower)
    with open("swear_words.txt", "w") as file:
        file.write('\n'.join(phrases))
    await ctx.send("Banned phrases updated.")
    return

@bot.command(name="remove_word")
async def remove_word_command(ctx, word: str = None):
    if ctx.author.guild_permissions.administrator != True:
        await ctx.send("You don't have permissions to run this command.")
        return

    global phrases
    if word is None:
        await ctx.send("Please provide a word. Usage: /remove_word word")
        return

    word_lower = word.lower()
    phrases.remove(word_lower)
    with open("swear_words.txt", "w") as file:
        file.write('\n'.join(phrases))
    await ctx.send("Banned phrases updated")
    return

@bot.command(name="owe")
async def owe_command(ctx, username: str = None):
    if username is None:
        await ctx.send("Please provide a username. Usage: /owe username")
        return

    if ctx.message.mentions:
        target_user = ctx.message.mentions[0]
    else:

        target_user = None
        if username.isdigit():
            try:
                target_user = await bot.fetch_user(int(username))
                target_user = ctx.guild.get_member(target_user.id)
            except:
                target_user = None

        if target_user is None:
            for member in ctx.guild.members:
                if username.lower() in member.name.lower() or (member.nick and username.lower() in member.nick.lower()):
                    target_user = member
                    break

    if target_user is None:
        await ctx.send(f"Could not find user with name '{username}'")
        return

    user_id = str(target_user.id)

    total = 0
    if user_id in user_word_counts:
        for phrase, count in user_word_counts[user_id].items():
            total += (count * cost_modifier)

    message = f"**{target_user.display_name} owes Panda ${total}**"

    if total == 0:
        message += "\nGood boy."

    await ctx.send(message)

#app = Flask('')

#@app.route('/')
#def home():
#    return "Discord bot is running!"

#def run():
#    app.run(host='0.0.0.0', port=9090)

#def keep_alive():
#    t = Thread(target=run)
#    t.start()


#keep_alive()

try:
    token = os.environ['TOKEN']
except KeyError:
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv('TOKEN')

    if not token:
        print("ERROR: No Discord token found! Add TOKEN to Secrets or .env file")
        exit(1)

print("Bot is connecting to Discord...")
try:
    bot.run(token)
except discord.errors.LoginFailure as e:
    print(f"ERROR: Failed to login to Discord. Token may be invalid: {e}")
    print("Please regenerate your token at https://discord.com/developers/applications")
except Exception as e:
    print(f"ERROR: An unexpected error occurred: {e}")
