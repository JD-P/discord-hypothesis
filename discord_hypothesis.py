import argparse
import discord
import asyncio
import h_annot
import sqlite3
import json


parser = argparse.ArgumentParser()
parser.add_argument("config_file")
parser.add_argument("--test", "-t", help="Turn on debug features and commands.")
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
            for annotation_row in reversed(results["rows"]):
                if annotation_row["id"] in in_memory:
                    continue
                else:
                    msg = build_message(annotation_row)
                    await client.send_message(channel, msg)
        for annotation_row in results["rows"]:
            if annotation_row["id"] in in_memory:
                continue
            else:
                in_memory.append(annotation_row["id"])
            #TODO: Figure out why this had double-report issues when recording 10 id's
            if len(in_memory) > 100: # Limit held ID's in memory to the last ten entries
                del(in_memory[0])
        with open("processed.json", "w") as outfile:
            json.dump(in_memory, outfile)
        await asyncio.sleep(300)

@client.event
async def on_message(message):
    global config
    if message.content.startswith('!register'):
        await client.send_message(message.channel, "Not implemented.")

def build_message(annotation_row):
    if annotation_row["text"]:
        msg_base = "{} made a new annotation on {} ({})\n```{}"
    else:
        msg_base = "{} made a new highlight on {} ({})\n```{}"

    if len(annotation_row["text"]) > 325 or len(extract_exact(annotation_row)) > 325:
        msg_base = msg_base + "...```"
    else:
        msg_base = msg_base + "```"

    if annotation_row["text"]:
        preview = annotation_row["text"]
    else:
        preview = extract_exact(annotation_row)

    return msg_base.format(
        annotation_row["user"].split(":")[1],
        annotation_row["document"]["title"][0],
        annotation_row["links"]["html"],
        preview)
    
def extract_exact(annotation_row):
    try:
        annotation_row["target"][0]["selector"]
    except KeyError as e:
        print(annotation_row)
        return "<text not available>"
    for selector in annotation_row["target"][0]["selector"]:
        try:
            return selector["exact"]
        except KeyError:
            continue
    return None
        
client.loop.create_task(monitor_hypo_group())
client.run(config["discord-api-key"])


