import discord
import os
from dotenv import load_dotenv
import requests
import json
import random
import wikipedia
from discord.ext import commands

load_dotenv()  # Loads environment variables from .env file


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")  # Gets info from the site
    json_data = json.loads(response.text)  # Converts into text
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


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Call process_commands so other commands like $hello and $quote work
    await bot.process_commands(message)

    if message.content.startswith('$wiki'):
        query = message.content.split(' ')[1:]
        try:
            result = wikipedia.page(' '.join(query))
            summary_length = 3500  # Adjust this value as needed
            if len(result.summary) > summary_length:
                shortened_summary = result.summary[:summary_length] + "..."
                await message.channel.send(shortened_summary)
            else:
                await message.channel.send(result.summary)
        except wikipedia.exceptions.DisambiguationError as e:
            disambiguation_message = f"The search '{' '.join(query)}' may refer to:\n" + "\n".join(
                e.options[:10])  # Limit to 10 options
            await message.channel.send(disambiguation_message)
        except wikipedia.exceptions.PageError:
            await message.channel.send("I couldn't find that article on Wikipedia.")
        except discord.errors.HTTPException as e:
            if "content must be 4000 or fewer in length" in str(e):
                await message.channel.send("The Wikipedia summary is too long! Try refining your search term.")


@bot.command()
async def hello(ctx):
    await ctx.channel.send('Hello!')


@bot.command()
async def generate(ctx):
    car = get_random_car_image()  # Calls the function to generate the image
    await ctx.channel.send(car)  # Prints it out in form of an image


@bot.command()
async def quote(ctx):
    quotes = get_quote()  # Calls the function to generate quotes
    await ctx.channel.send(quotes)  # Prints it out

@bot.command()
async def thankyou(ctx):
    await ctx.channel.send('Your Welcome!!')

# Add a shutdown command
@bot.command()
async def shutdown(ctx):
    await ctx.channel.send("Shutting down the bot. Goodbye!")
    await bot.close()  # Safely disconnects the bot


bot.run(os.getenv('TOKEN'))
