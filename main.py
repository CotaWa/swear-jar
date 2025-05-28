import discord
import os
import json
from collections import defaultdict
from discord.ext import commands
import string
from datetime import datetime

cost_modifier = 1 #For example 1 for 1$ per word or 3 for 3 times the price

def save_database(data):
    global users
    users = {user: value for user, value in data.items() if value > 0}
    data = {user: value for user, value in users.items() if value > 0}
    with open("data.json", "w") as fp:
        json.dump(data, fp)

def load_database():
	dictionary = {}
	with open("data.json", "r") as fp:
		dictionary = json.load(fp)
	return dictionary

def load_users():
    users = {}
    with open("users.json", "r") as fp:
        users = json.load(fp)
    return users

def save_users(data):
    with open("users.json", "w") as fp:
        json.dump(data, fp)

user_word_counts = load_database()
users = load_users()

intents = discord.Intents.default()
try:
    intents.message_content = True
    print("Using message content - make sure it's enabled in Discord Developer Portal")
except:
    print("Message content intent not available - some features may be limited")

bot = commands.Bot(command_prefix='/', intents=intents)


def load_swear_words():
    phrases = []
    with open("swear_words.txt", "r") as file:
        phrases = file.read().split("\n")
    return phrases

phrases = load_swear_words()

@bot.event
async def on_ready():
    total = 0
    for keys in user_word_counts:
        total += user_word_counts[keys]
    print(f"Logged in as {bot.user}")
    print(f"Loaded {total} word counts from database")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    message_lower = message.content.lower()
    message_lower = message_lower.translate(str.maketrans('', '', string.punctuation))

    if "/add_word" in message_lower or "/remove_word" in message_lower:
        return

    for word in message_lower.split():

        try:
            index = phrases.index(word)
            count = message_lower.count(word)
            await message.channel.send(word + " is not nice to say! \n You owe Panda. ☹️")
            user_id = str(message.author.id)
            user_word_counts[user_id] += count
            save_database(user_word_counts)
            break

        except ValueError:
            pass

@bot.command(name="swear_help")
async def help_command(ctx):
    if ctx.guild.get_role(1362743186845339800) in ctx.author.roles:
        await ctx.send("These are the commands you can run: \n /swear_help \n /owe (username) \n /tax (value) \n /add_word (word) \n /remove_word (word) \n /add_debt (user) (amount) \n /remove_debt (user) (amount) \n /swear_total \n /swear_leaderboard")
        return
    elif ctx.author.guild_permissions.administrator:
        await ctx.send("These are the commands you can run: \n /swear_help \n /owe (username) \n /tax (value) \n /add_word (word) \n /remove_word (value) \n /swear_total \n /swear_leaderboard")
        return
    else:
        await ctx.send("These are the commands you can run: \n /swear_help \n /owe (username) \n /swear_total \n /swear_leaderboard")
        return

@bot.command(name="swear_total")
async def total_debt_command(ctx):
    total = 0
    for user in user_word_counts:
        total += user_word_counts[user] * cost_modifier
    await ctx.send(f"Total amount of swear debt is ${total}")

@bot.command(name="swear_leaderboard")
async def leaderboard_command(ctx):
    global users
    sorted_db = {}
    for user in sorted(user_word_counts, key=user_word_counts.get):
        sorted_db[user] = user_word_counts[user]
    strings = []
    user_ids = list(sorted_db.keys())
    user_ids.reverse()
    for user in user_ids:
        target_user = users.get(user, None)
        if target_user == None:
            target_user = await ctx.guild.fetch_member(user)
            users[user] = target_user.name
            save_users(users)
        strings.append(f"{target_user} owes ${sorted_db[user]}")
    await ctx.send('\n'.join(strings))

@bot.command(name="add_debt")
async def add_debt_command(ctx, user: str = None, add: str = None):
    if (ctx.guild.get_role(1362743186845339800) in ctx.author.roles) == False:
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

    if user_id in user_word_counts:
        user_word_counts[user_id] += add
        save_database(user.r_word_counts)
        await ctx.send(f"Added ${add} to {target_user.display_name}'s debt.")
        return

    #If the user isn't in the database already we add them to the database
    user_word_counts[user_id] = add
    save_database(user_word_counts)
    await ctx.send(f"Added ${add} to {target_user.display_name}'s debt.")
    return

@bot.command(name="remove_debt")
async def pay_debt_command(ctx, user: str = None, remove: str = None):
    if (ctx.guild.get_role(1362743186845339800) in ctx.author.roles) == False:
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

    if user_id not in user_word_counts:
        await ctx.send(f"{target_user.display_name} has no debt to be payed off.")
        return
    if remove > user_word_counts[user_id]:
        await ctx.send("Can't remove more debt than the user has.")
        return

    user_word_counts[user_id] -= remove
    save_database(user_word_counts)
    await ctx.send(f"Removed ${remove} from {target_user.display_name}'s debt.")
    return

@bot.command(name="tax")
async def change_tax_command(ctx, tax: str = None):
    if ctx.author.guild_permissions.administrator != True and ctx.guild.get_role(1362743186845339800) in ctx.author.roles != True:
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
    if ctx.author.guild_permissions.administrator != True and ctx.guild.get_role(1362743186845339800) in ctx.author.roles != True:
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
    if ctx.author.guild_permissions.administrator != True and ctx.guild.get_role(1362743186845339800) in ctx.author.roles != True:
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
        total = user_word_counts[user_id] * cost_modifier

    message = f"**{target_user.display_name} owes Panda ${total}**"

    if total == 0:
        message += "\nGood boy."

    await ctx.send(message)

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
