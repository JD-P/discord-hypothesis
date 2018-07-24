import argparse
import discord
import asyncio
import h_annot
import sqlite3
import json


parser = argparse.ArgumentParser()
parser.add_argument("config_file")
arguments = parser.parse_args()


with open(arguments.config_file) as infile:
    try:
        config = json.load(infile)
    except IOError:
        print("Couldn't find the config file, make sure you have config.json in the bot directory!")
        exit()

client = discord.Client()



async def monitor_hypo_group():
    # Track processed annotation ID's so we don't double report
    try:
        with open("processed.json") as infile:
            in_memory = json.load(infile)
    except IOError:
        in_memory = [] 
    await client.wait_until_ready()
    channels = []
    for channel_id in config["channels"]:
        channels.append(discord.Object(id=channel_id))
    while not client.is_closed:
        results = json.loads(
            h_annot.api.search(config["hypo-api-key"],
                               group=config["hypo-group-id"],
                               limit=10)
            )
        for channel in channels:
            for annotation_row in results["rows"]:
                if annotation_row["id"] in in_memory:
                    continue
                msg = "{} made a new annotation on {} ({})".format(
                    annotation_row["user"].split(":")[1],
                    annotation_row["document"]["title"][0],
                    annotation_row["links"]["html"])
                await client.send_message(channel, msg)
        for annotation_row in results["rows"]:
            if annotation_row["id"] in in_memory:
                continue
            in_memory.append(annotation_row["id"])
            if len(in_memory) > 10: # Limit held ID's in memory to the last ten entries
                del(in_memory[0])
        with open("processed.json", "w") as outfile:
            json.dump(in_memory, outfile)
        await asyncio.sleep(300)

@client.event
async def on_message(message):
    global config
    if message.content.startswith('!register'):
        await client.send_message(message.channel, "Not implemented.")

client.loop.create_task(monitor_hypo_group())
client.run(config["discord-api-key"])
