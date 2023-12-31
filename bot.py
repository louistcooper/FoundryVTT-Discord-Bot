import discord, boto3

intents = discord.Intents.default()
intents.message_content = True
#intents.members = True

client = discord.Client(intents=intents)

# Grabbing credentials from file creds.txt
with open('creds.txt', 'r') as file:
    data = file.readlines()
    file.close()

instance_id = data[0].replace('instance_id = ', '').replace('\n', '')
discord_bot_token = data[1].replace('discord_bot_token = ', '').replace('\n', '')

ec2 = boto3.resource('ec2')
instance = ec2.Instance(instance_id)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------------')
    print("AWS instance is currently: " + instance.state['Name'].upper())

@client.event
async def on_message(message):
    member_ids = (member.id for member in message.mentions)
    if client.user.id in member_ids:
        if 'stop' in message.content:
            if not is_stopping() and is_on():
                if turn_off_instance():
                    await message.channel.send('AWS Instance stopping')
                else:
                    await message.channel.send('Error stopping AWS Instance, try again in a bit')
            else:
                await message.channel.send('AWS Instance is already stopping or is off')
        elif 'start' in message.content:
            if not is_on() and not is_stopping():
                if turn_on_instance():
                    await message.channel.send('AWS Instance starting')
                else:
                    await message.channel.send('Error starting AWS Instance, try again in a bit')
        elif 'status' in message.content:
            await message.channel.send('AWS Instance state is currently: ' + get_instance_state_string())
        elif 'reboot' in message.content:
            if reboot_instance():
                await message.channel.send('AWS Instance rebooting')
            else:
                await message.channel.send('Error rebooting AWS Instance')
        else:
            await message.channel.send('Unknow command? Try start, stop, status or reboot')

def turn_off_instance():
    try:
        instance.stop(Hibernate=False,DryRun=False,Force=False)
        return True
    except:
        return False

def turn_on_instance():
    try:
        instance.start(DryRun=False)
        return True
    except:
        return False

def get_instance_state_string():
    return instance.state['Name']

def is_stopping():
    status = get_instance_state_string()
    if status == "stopping":
        return True
    else:
        return False

def is_on():
    status = get_instance_state_string()
    if status == "running":
        return True
    else:
        return False

def is_starting():
    status = get_instance_state_string()
    if status == "pending":
        return True
    else:
        return False

def reboot_instance():
    try:
        instance.reboot(DryRun=False)
        return True
    except:
        return False


client.run(discord_bot_token)
