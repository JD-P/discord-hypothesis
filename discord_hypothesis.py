from hypothesis_tracker import HypothesisTracker
import argparse
import time
import threading
import asyncio
import discord
import h_annot
import json

client = discord.Client()

async def monitor_hypo_group():
    
    await client.wait_until_ready()
    channels = []
    for channel_id in config["channels"]:
        channels.append(discord.Object(id=channel_id))
    while not client.is_closed:
        if not results_lock.acquire(timeout=3):
            await asyncio.sleep(30)
            continue
        for channel in channels:
            for annotation_row in results:
                msg = build_message(annotation_row)
                await client.send_message(channel, msg)
        results_lock.release()
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

    #TODO: Fix the fact that this usually evaluates true because annotations reply to long texts
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    parser.add_argument("--test", "-t", help="Turn on debug features and commands.")
    arguments = parser.parse_args()

    results = []
    results_lock = threading.Lock()

    with open(arguments.config_file) as infile:
        try:
            config = json.load(infile)
        except IOError:
            print("Couldn't find the config file, make sure you have config.json in the bot directory!")
            exit()

    
    hypo_track = HypothesisTracker(results, results_lock, config["hypo-api-key"], config["hypo-group-id"])
    hypo_thread = threading.Thread(target=hypo_track.get_loop)
    hypo_thread.start()

    client.loop.create_task(monitor_hypo_group())
    client.run(config["discord-api-key"])


