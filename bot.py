import discord
import random
import asyncio
import requests
from bs4 import BeautifulSoup
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
import os
# from keys import *
API_KEY_WEATHER = os.getenv("API_KEY_WEATHER")
BASE_URL_WEATHER = os.getenv("BASE_URL_WEATHER")
CLIENT_TOKEN_DISCORD = os.getenv("CLIENT_TOKEN_DISCORD")

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        # THIS IS THE HELP MESSAGE WITH ALL AVAILABLE COMMANDS
        if message.content.startswith('!help'):
            if message.channel.name == "general":
                embed = discord.Embed(title="Help on Bot", description="Some useful commands")
                embed.add_field(name="!meteo cityname", value="Get the current weather at this city")
                embed.add_field(name="!chifoumi", value="Start a Rock Paper Scissors game")
                embed.add_field(name="!email url", value="search for emails adress on the website")

                await message.channel.send(content=None, embed=embed)

        # THIS IS FOR DELETE ALL MESSAGE IN THE CHANNEL WHERE WE CALL !CLEAR
        if message.content.startswith('!clear'):
            if str(message.author) == "Ypo#1356":
                await message.channel.purge()

        # THIS IS FOR GETTING EMAILS FROM A WEBSITE
        if message.content.startswith('!email'):
            input_email = message.content.strip('!email ')

            if not str(input_email).startswith('http'):
                input_url = "https://" + input_email
            else:
                input_url = input_email

            new_urls = deque([input_url])

            # a set of urls that we have already crawled
            processed_urls = set()

            # a set of crawled emails
            emails = set()

            # process urls one by one until we exhaust the queue
            while len(new_urls):
                # move next url from the queue to the set of processed urls
                url = new_urls.popleft()
                processed_urls.add(url)

                # extract base url to resolve relative links
                parts = urlsplit(url)
                base_url = "{0.scheme}://{0.netloc}".format(parts)
                path = url[:url.rfind('/')+1] if '/' in parts.path else url

                # get url's content
                print("Processing %s" % url)
                try:
                    response = requests.get(url)
                except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                    # ignore pages with errors
                    continue

                # extract all email addresses and add them into the resulting set
                new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
                emails.update(new_emails)

                # create a beutiful soup for the html document
                soup = BeautifulSoup(response.text, "html.parser")

                # find and process all the anchors in the document
                for anchor in soup.find_all("a"):
                    # extract link url from the anchor
                    link = anchor.attrs["href"] if "href" in anchor.attrs else ''
                    # resolve relative links
                    if link.startswith('/'):
                        link = base_url + link
                    elif not link.startswith('http'):
                        link = path + link
                    # add the new url to the queue if it was not enqueued nor processed yet
                    if not link in new_urls and not link in processed_urls:
                        new_urls.append(link)

            for mail in emails:
                await message.channel.send(f"I found this email : {mail}")

        # THIS IS FOR GETTING THE CURRENT WEATHER IN A CITY
        if message.content.startswith('!meteo'):
            city = message.content.strip('!meteo ')
            if len(city) < 1:
                await message.channel.send("Il faut taper !meteo + le nom d'une ville")
            else:
                request_url = f"{BASE_URL_WEATHER}?appid={API_KEY_WEATHER}&q={city}"
                response = requests.get(request_url)
                if response.status_code == 200:
                    data = response.json()
                    weather = data['weather'][0]['description']
                    temperature = round(data['main']['temp'] - 273.15, 2)

                    embed = discord.Embed(title="Météo du jour", description=city)
                    embed.add_field(name="Temps", value=weather)
                    embed.add_field(name="Température", value=f"{temperature}°C")

                    await message.channel.send(content=None, embed=embed)
                else:
                    await message.channel.send("Heu, c'est une ville ça ?")

        # THIS IS FOR STARTING A CHIFOUMI
        if message.content.startswith('!chifoumi'):
            user_wins = 0
            computer_wins = 0
            options = ["rock", "paper", "scissors"]

            while True:
                await message.channel.send('Rock, paper or scissors ?')

                def is_correct(m):
                    return m.author == message.author and m.content in options

                random_number = random.randint(0, 2)
                computer_pick = options[random_number]

                try:
                    guess = await self.wait_for('message', check=is_correct, timeout=5.0)
                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long you looser ! SCORE : {message.author.name} {user_wins} - {computer_wins} THE MACHINA')

                if guess.content == "rock" and computer_pick == "scissors":
                    user_wins +=1
                    await message.channel.send(f"WIN ! Computer pick {computer_pick} ! SCORE : {message.author.name} {user_wins} - {computer_wins} THE MACHINA")
                    continue
                
                elif guess.content == "paper" and computer_pick == "rock":
                    user_wins +=1
                    await message.channel.send(f"WIN ! Computer pick {computer_pick} ! SCORE : {message.author.name} {user_wins} - {computer_wins} THE MACHINA")
                    continue

                elif guess.content == "scissors" and computer_pick == "paper":
                    user_wins +=1
                    await message.channel.send(f"WIN ! Computer pick {computer_pick} ! SCORE : {message.author.name} {user_wins} - {computer_wins} THE MACHINA")
                    continue

                elif guess.content == "rock" and computer_pick == "rock":
                    await message.channel.send(f"DRAW ! Computer pick {computer_pick} ! SCORE : {message.author.name} {user_wins} - {computer_wins} THE MACHINA")
                    continue
                
                elif guess.content == "paper" and computer_pick == "paper":
                    await message.channel.send(f"DRAW ! Computer pick {computer_pick} ! SCORE : {message.author.name} {user_wins} - {computer_wins} THE MACHINA")
                    continue

                elif guess.content == "scissors" and computer_pick == "scissors":
                    await message.channel.send(f"DRAW ! Computer pick {computer_pick} ! SCORE : {message.author.name} {user_wins} - {computer_wins} THE MACHINA")
                    continue

                else:
                    computer_wins +=1
                    await message.channel.send(f"LOOSE ! Computer pick {computer_pick} ! SCORE : {message.author.name} {user_wins} - {computer_wins} THE MACHINA")
                    continue

        if message.content.startswith('$hello'):
            await message.channel.send('Hello World!')


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

client.run(CLIENT_TOKEN_DISCORD)