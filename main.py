import discord
import os
import json
from collections import defaultdict
from discord.ext import commands
#from flask import Flask
import threading
import time
from datetime import datetime

cost_modifier = 1 #For example 1 for 1$ per word or 3 for 3 times the price
save_interval = 600 #In seconds

def save_database():
#    while True:
#        now = datetime.now()
    with open("data.json", "w") as fp:
        json.dump(db, fp)
#        print("Saved data to file at " + str(now))
#        time.sleep(save_interval)

def load_database():
	dictionary = {}
	with open("data.json", "r") as fp:
		raw_data = fp.read()
		print(raw_data)
		dictionary = json.loads(raw_data)
	return dictionary

def get_nested_defaultdict():
    result = defaultdict(lambda: defaultdict(int))
    if "user_word_counts" in db:
        stored_data = json.loads(db["user_word_counts"])
        for user_id, word_dict in stored_data.items():
            for word, count in word_dict.items():
                result[user_id][word] = count
    return result

db = load_database()

user_word_counts = get_nested_defaultdict()


def save_word_counts():
    data_to_save = {}
    for user_id, word_dict in user_word_counts.items():
        data_to_save[user_id] = dict(word_dict)

    db["user_word_counts"] = json.dumps(data_to_save)

intents = discord.Intents.default()
try:
    intents.message_content = True
    print("Using message content intent - make sure it's enabled in Discord Developer Portal")
except:
    print("Message content intent not available - some features may be limited")

bot = commands.Bot(command_prefix='/', intents=intents)


phrases = []
#phrases = ["fuck", "shit", "cunt", "kys", "bitch", "dickhead", "dick", "asshole", "ass", "bastard", "hawk tuah", "pussy", "moist", "halgean", "aeriki", "penis", "sex", "cock", "vagina", "porn", "bahoosay", "poosay", "lindau", "tandong", "tanderium", "ooo.ooo", "aaa.aaa"]

thread = threading.Thread(target=save_database, daemon=True)
thread.start()

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
    #print(message_lower.split())

    if "/add_word" in message_lower:
        return

    for word in message_lower.split():
        #print("3")

        try:
            index = phrases.index(word)
            #print(word)
            #print("4")
            count = message_lower.count(word)
            await message.channel.send(word + " is not nice to say!")
            user_id = str(message.author.id)
            user_word_counts[user_id][word] += count
            save_word_counts()
            await message.channel.send("You owe Panda. ☹️")
            save_database()
            break

        except ValueError:
            #print(word)
            pass

@bot.command(name="reload")
@commands.has_permissions(administrator=True)
async def reload_command(ctx):
    global phrases
    phrases = load_swear_words()
    await ctx.send("Reloaded swear words")
    return

@reload_command.error
async def reload_command(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")

@bot.command(name="tax")
@commands.has_permissions(administrator=True)
async def change_tax_command(ctx, tax: str = None):
    global cost_modifier
    if tax is None:
        await ctx.send("Please provide a value. Usage: /tax (value)")
        return

    try:
        tax = int(tax)
    except:
        await ctx.send("Please provide a number.")
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

@change_tax_command.error
async def change_tax_command(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")

@bot.command(name="add_word")
@commands.has_permissions(administrator=True)
async def add_word_command(ctx, word: str = None):
    global phrases
    if word is None:
        await ctx.send("Please provide a word. Usage: /add_word word")
        return

    word_lower = word.content.lower()
    phrases.append(word_lower)
    with open("swear_words.txt", "w") as file:
        file.write('\n'.join(phrases))
    await ctx.send("Banned phrases updated.")
    return

@bot.command(name="remove_word")
@commands.has_permissions(administrator=True)
async def remove_word_command(ctx, word: str = None):
    global phrases
    if word is None:
        await ctx.send("Please provide a word. Usage: /remove_word word")
        return

    word_lower = word.content.lower()
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
