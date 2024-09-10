import discord
import logging
import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands
import eng_to_ipa as ipa
from discord import Emoji
import requests
import json
from transphone import read_tokenizer
from gruut import sentences
import argostranslate.package
import argostranslate.translate   
import time
from collections import defaultdict
    
from_code = "en"
to_code = "es"
cooldown = {}

# Download and install Argos Translate package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())    

###------------------------------TOKEN LOADERS + Error Debugging------------------------------###
load_dotenv()
DISCORD_TOKEN = os.getenv('TOKEN')
GUILD_ID = os.getenv("GUILD")
ALLOWED_CHANNELS = os.getenv("ALLOWED_CHANNELS").strip('[]').split(',')


# DICTIONARY_TOKEN = os.getenv('DICTIONARY')
# THESAURUS_TOKEN = os.getenv('THESAURUS')
# LEARNERS_TOKEN = os.getenv('LEARNERS') # for IPA
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
###-------------------------------------------------------------------------------------------###

class MyDiscord(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        
      
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        # guild = self.get_guild(int(GUILD_ID))
        # if guild:
        #     await guild.create_role(name="Muted")
      

    async def on_message(self, message, *args, **kwargs):
        allowed_channels = [int(channel.strip()) for channel in ALLOWED_CHANNELS]
        if message.author.bot or message.author == self.user:
            return

        if message.channel.id in allowed_channels:
            commands_dict = {
                '$wug' : self.handle_wug,
                '$ipa ' : self.handle_ipa,
                '$translate ' : self.handle_translation,
                '$help' : self.handle_help,
            }
            for command, handler in commands_dict.items(): # Command is key; handler is value
                if message.content.startswith(command):
                    user_id = message.author.id
                    if user_id in cooldown:
                        await message.channel.send("Please stop spamming! Wait 5 seconds.")
                        return
                    
                    cooldown[user_id] = time.time()
                    await handler(message)
                    await message.add_reaction("👍")
                    await asyncio.sleep(5)
                    del cooldown[user_id]
                    break
                
    async def handle_wug(self,message):
        await message.channel.send("Wug's here!")
        
    async def handle_ipa(self,message):
        text_to_translate = message.content[len('$ipa '):].strip()
        for sent in sentences(text_to_translate,lang="en-us"):
            for word in sent:
                if word.phonemes:
                    phonemes_str = ' '.join(word.phonemes)
                    await message.channel.send(f'IPA Translation: /{phonemes_str}/')
        
    async def handle_translation(self,message):
        text_to_translate = message.content[len('$translate '):].strip()
        translatedText = argostranslate.translate.translate(text_to_translate,from_code,to_code)
        await message.channel.send(f'Spanish Translation: {translatedText}')

    async def handle_help(self,message):
        await message.channel.send("Type '$ipa [word or sentence]' for a word/sentence to translate.\nType '$translate [word or sentence]' to translate English words to Spanish")    

intents = discord.Intents.default()
intents.message_content = True

client = MyDiscord(intents=intents)
client.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)

###-------------------------------------------------------Into the Abyss---------------------------------------------------###
            # if message.content.startswith('$list '):
            #     text_to_translate = message.content[len('$list '):].strip()
            #     ipa_translation = ipa.ipa_list(text_to_translate)
            #     unzipped_list = [item[0] for item in ipa_translation]
            #     await message.channel.send(f'IPA transcriptions of each word: {unzipped_list}')
            #     await message.add_reaction("👍")
            
             # url = f"https://dictionaryapi.com/api/v3/references/learners/json/{text_to_translate}?key={LEARNERS_TOKEN}"
                # definitions_response = requests.get(url)
                # # print("Response Status Code:", definitions_response.status_code)
                # # print("Response Content:", definitions_response.text)
                # definitions_data = definitions_response.json()
                # for element in definitions_data:
                #         if 'hwi' in element:
                #             hwi_element = element
                #             break;
                
                   # ipa_transcription = hwi_element['hwi']['prs'][0]['ipa']
                        # ipa_translation = ipa.convert(text_to_translate)
                        #lst = language.tokenize(text_to_translate)
                        
                                #language = read_tokenizer('eng') 
