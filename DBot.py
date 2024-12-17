import discord
import os
from dotenv import load_dotenv
import requests
import json
import random
import wikipedia
from discord.ext import commands, tasks
from datetime import datetime, timedelta

load_dotenv()  # Loads environment variables from .env file

# Utility functions
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " - " + json_data[0]['a']
    return quote

def get_random_car_image():
    min_width = 400
    max_width = 1920
    min_height = 400
    max_height = 1080

    width = random.randint(min_width, max_width)
    height = random.randint(min_height, max_height)
    return f"https://loremflickr.com/{width}/{height}/car"

# Automated replies dictionary
automated_replies = {
    "hello": "Hi there! How can I assist you today?",
    "bye": "Goodbye! Have a great day!",
    "help": "Here are some commands you can use: $quote, $wiki, $remind, $kick, $ban, $customcmd."
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for moderation commands

bot = commands.Bot(command_prefix='$', intents=intents)
custom_commands = {}  # To store user-defined custom commands
reminders = []  # To store reminders

# Bot ready event
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    reminder_task.start()

# Automated replies and custom command handler
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Automated replies
    for trigger, response in automated_replies.items():
        if trigger in message.content.lower():
            await message.channel.send(response)

    # Custom commands
    if message.content.startswith('$'):
        cmd = message.content[1:]
        if cmd in custom_commands:
            await message.channel.send(custom_commands[cmd])

    await bot.process_commands(message)  # Ensure other commands work

# Commands
@bot.command()
async def hello(ctx):
    await ctx.channel.send('Hello!')

@bot.command()
async def generate(ctx):
    car = get_random_car_image()
    await ctx.channel.send(car)

@bot.command()
async def quote(ctx):
    quotes = get_quote()
    await ctx.channel.send(quotes)

@bot.command()
async def thankyou(ctx):
    await ctx.channel.send('You’re welcome!')

@bot.command()
async def wiki(ctx, *, query):
    try:
        result = wikipedia.page(query)
        summary_length = 3500
        if len(result.summary) > summary_length:
            shortened_summary = result.summary[:summary_length] + "..."
            await ctx.channel.send(shortened_summary)
        else:
            await ctx.channel.send(result.summary)
    except wikipedia.exceptions.DisambiguationError as e:
        options = '\n'.join(e.options[:10])  # Limit to 10 options
        await ctx.channel.send(f"The search '{query}' may refer to:\n{options}")
    except wikipedia.exceptions.PageError:
        await ctx.channel.send("I couldn't find that article on Wikipedia.")

@bot.command()
async def shutdown(ctx):
    await ctx.channel.send("Shutting down the bot. Goodbye!")
    await bot.close()

@bot.command()
async def customcmd(ctx, name: str, *, response: str):
    custom_commands[name] = response
    await ctx.channel.send(f"Custom command '{name}' added!")

# Task reminders
@bot.command()
async def remind(ctx, time: int, *, task: str):
    reminder_time = datetime.now() + timedelta(seconds=time)
    reminders.append((reminder_time, ctx.channel.id, task))
    await ctx.channel.send(f"Reminder set for {time} seconds from now.")

@tasks.loop(seconds=5)
async def reminder_task():
    now = datetime.now()
    for reminder in reminders[:]:
        reminder_time, channel_id, task = reminder
        if now >= reminder_time:
            channel = bot.get_channel(channel_id)
            await channel.send(f"Reminder: {task}")
            reminders.remove(reminder)

# Basic moderation commands
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.channel.send(f"{member} has been kicked. Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.channel.send(f"{member} has been banned. Reason: {reason}")

bot.run(os.getenv('TOKEN'))
