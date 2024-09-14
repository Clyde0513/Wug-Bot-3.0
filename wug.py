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
from gruut import sentences
import argostranslate.package
import argostranslate.translate
import time
from collections import defaultdict
import regex as re
import unicodedata

# api_instance = argostranslate.apis.LibreTranslateAPI()
codes = [ "ar", "zh", "en", "fr", "de", "hi", "it", "ja", "pl", "pt", "tr", "ru", "es" ]
mappings = set()
processed = set()
cooldown = {}

# Download and install Argos Translate package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()

# Build a dictionary of available packages based on (from_code, to_code)
package_dict = {
    (pkg.from_code, pkg.to_code): pkg for pkg in available_packages
}


for from_code in codes:
    if from_code in processed:
        continue
    for to_code in codes:
        if from_code == to_code:
            continue
        package_to_install = package_dict.get((from_code, to_code))
        if package_to_install is not None:
            # argostranslate.package.install_from_path(package_to_install)
            mappings.add((from_code, to_code))
            processed.add(from_code)
            print((from_code, to_code))

# for from_code in codes:
#     for to_code in codes:
#         if from_code != to_code and not (from_code, to_code) in mappings:
#             # Fetch the package from the dictionary
#             package_to_install = package_dict.get((from_code, to_code))
#             if package_to_install is None:
#                 continue
#             # Install the package
#             argostranslate.package.install_from_path(package_to_install.download()) 

#             # Note down the installed language mapping 
#             mappings.add((from_code, to_code))   
#             print((from_code, to_code))

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
                '$syllabify ' : self.handle_syllabification
            }
            for command, handler in commands_dict.items(): # Command is key; handler is value
                if message.content.startswith(command):
                    user_id = message.author.id
                    if user_id in cooldown:
                        await message.reply("Please stop spamming! Wait 5 seconds.", mention_author=False)
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
        params = message.content[len('$translate '):].strip().split(maxsplit=2)
        if len(params) != 3:
            await message.reply("Please send messages in this format: $translate [from-code] [to-code] [word or sentence].", mention_author=False)
            return
        from_code, to_code, text_to_translate = params
        if not (from_code, to_code) in mappings:
            if not from_code in codes or not to_code in codes:
                await message.reply('Please enter an available language (type $help for a list of available languages).', mention_author=False)
                return
            for code in codes:
                if code == from_code or code == to_code:
                    continue
                if (from_code, code) in mappings and (code, to_code) in mappings:
                    tempTranslation = argostranslate.translate.translate(text_to_translate,from_code,code)
                    translatedText = argostranslate.translate.translate(tempTranslation,code,to_code)
                    await message.channel.send(f'Translation: {translatedText}')
                    return
            await message.reply('Sorry, translations between these languages are not yet supported.', mention_author=False)
            return
        else:
            translatedText = argostranslate.translate.translate(text_to_translate,from_code,to_code)
            await message.channel.send(f'Translation: {translatedText}')

    async def handle_translation(self,message):
        params = message.content[len('$translate '):].strip().split(maxsplit=2)
        if len(params) != 3:
            await message.reply("Please send messages in this format: $translate [from-code] [to-code] [word or sentence].", mention_author=False)
            return
        from_code, to_code, text_to_translate = params
        if not (from_code, to_code) in mappings:
            if not from_code in codes or not to_code in codes:
                await message.reply('Please enter an available language (type $help for a list of available languages).', mention_author=False)
                return
            for code in codes:
                if code == from_code or code == to_code:
                    continue
                if (from_code, code) in mappings and (code, to_code) in mappings:
                    tempTranslation = argostranslate.translate.translate(text_to_translate,from_code,code)
                    translatedText = argostranslate.translate.translate(tempTranslation,code,to_code)
                    await message.channel.send(f'Translation: {translatedText}')
                    return
            await message.reply('Sorry, translations between these languages are not yet supported.', mention_author=False)
            return
        else:
            translatedText = argostranslate.translate.translate(text_to_translate,from_code,to_code)
            await message.channel.send(f'Translation: {translatedText}')

    async def handle_syllabification(self,message):        
        # Source: https://en.wikipedia.org/wiki/IPA_vowel_chart_with_audio
        vowels = set(['i','y','ɨ','ʉ','ɯ','u','ɪ','ʏ','ʊ','e','ø','ɘ','ɵ','ɤ','o','ə','ɛ','œ','ɜ','ɞ','ʌ','ɔ','æ',
        'ɐ','a','ɶ','ä','ɑ','ɒ','ɚ'])

        # Source: https://en.wikipedia.org/wiki/Diphthong
        diphthongs = set(['oʊ', 'aʊ', 'aɪ', 'eɪ', 'ɔɪ'])

        # Source: https://en.wikipedia.org/wiki/Help:IPA/English
        onsetClusters = set(['p','b','t','ɾ','d','tʃ','dʒ','k','ɡ','dj','ð','f','g','h','j',
        'k','l','lj','m','n','nj','ɹ','s','ʃ','v','w','z','ʒ','θ','pl','bl','kl','gl','pɹ','bɹ','tɹ','dɹ','kɹ',
        'gɹ','ɡɹ','ɡ','tw','dw','gw','kw','pw','fl','sl','θl','ʃl','fɹ','θɹ','ʃɹ','sw','θw','vw','pj','bj','tj','kj','gj',
        'mj','fj','vj','θj','sj','zj','hj','lj','sp','st','sk','sm','sn','sf','sθ','spl','skl','spɹ','stɹ','skw',
        'spj','stj','skj','smj','snj','sfɹ'])

        def remove_diacritics(s):
            # Normalize to NFD (Normalization Form D) to decompose characters
            s_decomposed = unicodedata.normalize('NFD', s)
            
            # Filter out combining diacritic marks
            s_no_diacritics = ''.join(c for c in s_decomposed if not unicodedata.combining(c))
        
            # Optionally, normalize back to NFC (Normalization Form C) if needed
            return unicodedata.normalize('NFC', s_no_diacritics)

        def find_onsets(cluster):
            n = len(cluster)
            lengths = []
    
            # Iterate over all possible starting points for substrings
            for start in range(len(cluster)):
                # Iterate over all possible ending points for substrings starting from `start`
                for end in range(start + 1, n + 1):
                    substring = cluster[start:end]
                    if substring in onsetClusters:
                        lengths.append(((end-start), start, end))
        
            return sorted(lengths, reverse=True, key=lambda x: x[0])
        
        cleaned_string = re.sub(r'[^a-zA-Z\s-]', '', message.content[len('$syllabify '):])
        reply = ''
        words = []
        ipa = []

        # Convert each word in the sentence to IPA
        for sent in sentences(cleaned_string,lang="en-us"):
            for word in sent:
                if (word.phonemes):
                    words.append(word.text)
                    ipa.append(remove_diacritics(((''.join(word.phonemes)).replace("ˈ","")).replace("ˌ","")))
        
        if not ipa:
            await message.reply('Please include at least one alphabetic character in your prompt!', mention_author=False)
            return

        for word in ipa:
            reply += '•••••••••••••••\n'
                    
            reply += f'Word: {words[ipa.index(word)]} ({word})\n'
            syllables = []
            i = 0

            while i < len(word):
                # Find the next vowel or diphthong
                j = i
                while j < len(word) and word[j] not in vowels:
                    j += 1
                if j == len(word):
                    break

                # Check for diphthong
                if j < len(word) - 1 and word[j:j+2] in diphthongs:
                    nucleus_end = j + 1
                else:
                    nucleus_end = j

                # Find the onset of the next syllable
                k = nucleus_end + 1
                while k < len(word) and word[k] not in vowels:
                    k += 1
                
                if k < len(word):
                    onsets = find_onsets(word[nucleus_end+1:k])
                    
                    # Find the longest onset cluster whose next character is a vowel
                    if onsets:
                        for onset in onsets:
                             if (word[nucleus_end+1+onset[0]+onset[1]] in vowels):
                                coda_end = nucleus_end+onset[1]
                                break
                    else:
                        coda_end = k-1
                else:
                    coda_end = len(word) - 1

                syllables.append((i, coda_end))
                i = coda_end + 1
            
            reply += f'Syllable count: {len(syllables)}\n'

            for idx, (start, end) in enumerate(syllables):
                syllable_text = word[start:end+1]
                reply += f'  Syllable: {syllable_text}\n'

                # Find onset
                j = start
                while j <= end and word[j] not in vowels:
                    j += 1
                if j > start:
                    reply += f'     Onset: {word[start:j]}\n'
                else:
                    reply += f'     Onset: none\n'

                # Find nucleus
                k = j
                while k <= end and (word[k] in vowels or (k < end and word[k:k+2] in diphthongs)):
                    k += 1
                reply += f'     Nucleus: {word[j:k]}\n'

                # Find coda
                if k <= end:
                    reply += f'     Coda: {word[k:end+1]}\n'
                else:
                    reply += f'     Coda: none\n'

        await message.channel.send(reply)
        
    async def handle_help(self,message):
        await message.channel.send("Type '$ipa [word or sentence]' for a word/sentence to translate.\n\nType '$translate [from-code] [to-code] [word or sentence]' to translate between any two available languages.\n\nThese languages are currently available: Arabic (ar), Chinese (zh), English (en), French (fr), German (de), Hindi (hi), Italian (it), Japanese (ja), Polish (pl), Portuguese (pt), Turkish (tr), Russian (ru), and Spanish (es).\n\nPlease specify the two-letter code of any language used in a translation command.\n\nType '$syllabify [word or sentence]' to get a complete syllabification analysis of any word or sentence.")    

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
