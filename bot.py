import discord
from discord.ext import commands
import requests
import asyncio
import random
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DOMAIN_NAME = os.getenv("DOMAIN_NAME")  # Define DOMAIN_NAME from .env

API_ENDPOINTS = {
    "running": os.getenv("RUNNING_ENDPOINT"),
    "stopped": os.getenv("STOPPED_ENDPOINT"),
    "start": os.getenv("START_ENDPOINT"),
    "stop": os.getenv("STOP_ENDPOINT")
}
INSTANCE_ID = os.getenv("INSTANCE_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ALLOWED_ROLES = os.getenv("ALLOWED_ROLES").split(',')

# Starting Events Messages
# Starting Events Messages with link
starting_events_messages = [
    f"Initiating neural linkup. Commencing instance startup sequence. Stand by for connection confirmation. While you wait, visit https://{DOMAIN_NAME} for more cybernetic wonders.",
    f"Unlocking the cybernetic gates to the virtual realm. Stand ready for a journey into the neon-lit future. Dive into the digital fray at https://{DOMAIN_NAME} for an electrifying experience.",
    f"The cyberdeck hums with anticipation as we jack into the cyberverse. Watch as the digital world comes to life. Explore the endless possibilities at https://{DOMAIN_NAME}.",
    f"Loading cyberware protocols... System online. Time to dive headfirst into the shadows of Night City. For more cyber-enhanced adventures, check out https://{DOMAIN_NAME}.",
    f"Neural pathways engaged. Let the digital dance of cyberpunk commence in the sprawling cityscape. Venture deeper into the future at https://{DOMAIN_NAME}.",
    f"The Net is calling. We're entering the realms where neon meets chrome. Get ready to hack the future. Discover more cyberpunk secrets at https://{DOMAIN_NAME}.",
    f"Beneath the flickering neon lights, the virtual cityscape awakens. Welcome to the world of tomorrow. Don't forget to explore https://{DOMAIN_NAME} for exclusive cybernetic content.",
    f"Cyber-optics calibrated. The virtual horizon awaits. Time to plunge into the chaos of cyber-reality. Visit https://{DOMAIN_NAME} for a deeper dive into the cyberpunk universe.",
    f"The shadows of Night City envelop us as we venture into the world of cyber-enhanced intrigue. For more cyberpunk adventures, check out https://{DOMAIN_NAME}.",
    f"System check complete. Prepare to join the ranks of cyberpunks in the endless labyrinth of the Net. Dive into the future at https://{DOMAIN_NAME}."
]

# Stopping Events Messages
stopping_events_messages = [
    "Emergency disconnection initialized. Stand by for system shutdown confirmation.",
    "The digital realm recedes as we sever the connection. Goodbye, cyber-reality, until we meet again.",
    "Digital threads untangled. Logging out from the virtual maze. Until next time, cyber-explorer.",
    "Deactivating neural interface. The cyberdeck falls silent as we return from the neon-tinged abyss.",
    "Exiting the cybernetic dream. Disconnecting from the realm where man and machine merge.",
    "The cyber-symphony fades as we pull the plug. Time to return to the mundane world, for now.",
    "Cyber-reality dissipates like a phantom. Back to the analog world we go, leaving neon echoes behind.",
    "The digital dance concludes, and the code dissolves. Farewell, cyberpunk dreams, until the next connection.",
    "System shutdown confirmed. Exiting the cyber-fringe, where the future always pulses with electric dreams.",
    "Disconnected from the digital abyss. Time to rest and recharge for the next cyberpunk adventure.",
    "R.A.B.I.D.S. has been released. Brace for digital chaos, as the legacy of Rache Bartmoss awakens."
]

# Function to pick a random message
def pick_random_message(messages):
    return random.choice(messages)

intents = discord.Intents.all()
intents.messages = True  # Enable message events
bot = commands.Bot(command_prefix='$', intents=intents)

async def check_instance_start_success(ctx):
    for _ in range(6):  # Retry up to 6 times over a minute
        await asyncio.sleep(10)  # Wait for 10 seconds before each check
        response = requests.get(API_ENDPOINTS["running"])
        runningIds = response.json().get('instance_ids')
        if INSTANCE_ID in runningIds:
            random_starting_message = pick_random_message(starting_events_messages)
            await ctx.send(random_starting_message)
            return
    # If instance hasn't started after all retries, send a failure message
    await ctx.send("Instance startup sequence failed or is taking longer than expected.")

async def check_instance_stop_success(ctx):
    for _ in range(6):  # Retry up to 6 times over a minute
        await asyncio.sleep(10)  # Wait for 10 seconds before each check
        response = requests.get(API_ENDPOINTS["stopped"])
        stoppedIds = response.json().get('instance_ids')
        if INSTANCE_ID in stoppedIds:
            random_stopping_message = pick_random_message(stopping_events_messages)
            await ctx.send(random_stopping_message)
            return
    # If instance hasn't stopped after all retries, send a failure message
    await ctx.send("Instance shutdown sequence failed or is taking longer than expected.")

@bot.command()
async def start(ctx):
    if str(ctx.channel.id) != CHANNEL_ID:
        await ctx.send("Commands from this channel are not accepted.")
        return
    
    # Check if the user has any of the allowed roles
    user_roles = [role.name for role in ctx.author.roles]
    if not any(role in user_roles for role in ALLOWED_ROLES):
        await ctx.send("You do not have permission to use this command.")
        return
    
    requests.post(API_ENDPOINTS["start"])
    await ctx.send("Initiating neural linkup. Commencing instance startup sequence. Stand by for connection confirmation.")
    bot.loop.create_task(check_instance_start_success(ctx))

@bot.command()
async def stop(ctx):
    if str(ctx.channel.id) != CHANNEL_ID:
        await ctx.send("Commands from this channel are not accepted.")
        return
    
    # Check if the user has any of the allowed roles
    user_roles = [role.name for role in ctx.author.roles]
    if not any(role in user_roles for role in ALLOWED_ROLES):
        await ctx.send("You do not have permission to use this command.")
        return
    
    requests.post(API_ENDPOINTS["stop"])
    await ctx.send("Emergency disconnection initialized. Stand by for system shutdown confirmation.")
    bot.loop.create_task(check_instance_stop_success(ctx))

@bot.command()
async def running(ctx):
    if str(ctx.channel.id) != CHANNEL_ID:
        await ctx.send("Commands from this channel are not accepted.")
        return
    
    # Check if the user has any of the allowed roles
    user_roles = [role.name for role in ctx.author.roles]
    if not any(role in user_roles for role in ALLOWED_ROLES):
        await ctx.send("You do not have permission to use this command.")
        return

    response = requests.get(API_ENDPOINTS["running"])
    runningIds = response.json().get('instance_ids')
    if INSTANCE_ID in runningIds:
        await ctx.send("System scan complete. Proceed to https://{DOMAIN_NAME} for further instructions.")
    else:
        await ctx.send("Initiate startup sequence when ready.")

@bot.event
async def on_ready():
    print(f'Connected to the cybernetic web as {bot.user}')

async def getRunning(ctx):
    response = requests.get(API_ENDPOINTS["running"])
    runningIds = response.json().get('instance_ids')
    if INSTANCE_ID in runningIds:
        random_starting_message = pick_random_message(starting_events_messages)
        await ctx.send(random_starting_message)
        return
    else:
        check_instance_start_success(ctx)

async def stopped(ctx):
    response = requests.get(API_ENDPOINTS["stopped"])
    stoppedIds = response.json().get('instance_ids')
    if INSTANCE_ID in stoppedIds:
        random_stopping_message = pick_random_message(stopping_events_messages)
        await ctx.send(random_stopping_message)
        return
    else: 
        check_instance_stop_success(ctx)

bot.run(TOKEN)
