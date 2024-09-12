import discord
import logging
import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands
import eng_to_ipa as ipass
from discord import Emoji
import requests
import json
from gruut import sentences
import argostranslate.package
import argostranslate.translate
# import argostranslate.apis
import time
from collections import defaultdict
import nltk
from nltk.corpus import words as nltk_words
from nltk.tokenize import LegalitySyllableTokenizer

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
            await message.reply("Please send messages in this format: $translate [from-lang] [to-lang] [word or sentence].", mention_author=False)
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
        # nltk.download('words')
        # Uncomment the line to download the package once, then it can be commented again
        words = message.content[len('$syllabify '):].strip().split()
        reply = ''

        # Source: https://en.wikipedia.org/wiki/IPA_vowel_chart_with_audio
        vowelSet = set(['i','y','ɨ','ʉ','ɯ','u','ɪ','ʏ','ʊ','e','ø','ɘ','ɵ','ɤ','o','ə','ɛ','œ','ɜ','ɞ','ʌ','ɔ','æ','ɐ','a','ɶ','ä','ɑ','ɒ','ɚ','ɔ˞','ɔ˞'])

        # Source: https://en.wikipedia.org/wiki/Help:IPA/English
        # onsetClusters = set(['p','b','t', 'ɾ', 'd', 'tʃ', 'dʒ', 'k', 'ɡ', 'dj', 'ð', 'f', 'g', 'h', 'j', 'k', 'l', 'lj', 'm', 'n', 'nj', 'ɹ', 's', 'ʃ',  'v', 'w', 'z', 'ʒ', 'θ' 'pl', 'bl', 'kl', 'gl', 'pɹ', 'bɹ', 'tɹ', 'dɹ', 'kɹ', 'gɹ', 'tw', 'dw', 'gw', 'kw', 'pw', 'fl', 'sl', 'θl', 'ʃl', 'fɹ', 'θɹ', 'ʃɹ', 'sw', 'θw', 'vw', 'pj', 'bj', 'tj', 'kj', 'gj', 'mj', 'fj', 'vj', 'θj', 'sj', 'zj', 'hj', 'lj', 'sp', 'st', 'sk', 'sm', 'sn', 'sf', 'sθ', 'spl', 'skl', 'spɹ', 'stɹ', 'skw', 'spj', 'stj', 'skj', 'smj', 'snj', 'sfɹ'])
        tknzr = LegalitySyllableTokenizer(nltk_words.words())

        
        for word in words:
            reply += '•••••••••••••••\n'
            ipaTranslation = ''

            for sent in sentences(word,lang="en-us"):
                for wrd in sent:
                    if (wrd.phonemes):
                        ipaTranslation = ((''.join(wrd.phonemes)).replace("ˈ","")).replace("ˌ","")
            
            if ipaTranslation == '':
                reply += f'Word: {word}\n'
                syllables = tknzr.tokenize(word)
                syllabifiedText = '-'.join(syllables)
                reply += f'Syllabification: {syllabifiedText}\n'
                continue

            reply += f'Word: {word} ({ipaTranslation})\n'
            syllables = tknzr.tokenize(word)
            syllabifiedText = '-'.join(syllables)
            syllablesIPA = []
            for syllable in syllables:
                for sent in sentences(syllable,lang="en-us"):
                    for syl in sent:
                        if (syl.phonemes):
                            syllablesIPA.append(((''.join(syl.phonemes)).replace("ˈ","")).replace("ˌ",""))
            syllabifiedIPAText = '-'.join(syllablesIPA)
            reply += f'Syllabification: {syllabifiedText} ({syllabifiedIPAText})\n'
            reply += '•••••••••••••••\n'

            '''
            nuclei = []
            ipaRaw = ipaTranslation.replace("'","")
            startVowels = -1
            endVowels = -1
            currentRun = False
            syllableNum = 0
            i = 0
            while i < len(ipaRaw):
                if ipaRaw[i] in vowelSet:
                    if not currentRun:
                        startVowels = i
                        currentRun = True
                    endVowels = i
                    if i == len(ipaRaw)-1:
                        nuclei.append((startVowels, endVowels, syllableNum))
                        syllableNum += 1
                else:
                    if currentRun:
                        nuclei.append((startVowels, endVowels, syllableNum))
                        syllableNum += 1
                    currentRun = False
                i += 1

            start = 0
            onsets = []
            for nucleus in nuclei:
                maxClusterStart = start
                for i in range (start, nucleus[0]):
                    if word[start:nucleus[0]] in onsetClusters:
                        maxClusterStart = i
                        onsets.append(maxClusterStart, nucleus[0]-1, nucleus[2])
                start = nucleus[1]+1
            
            syllableCount = nuclei[-1][2]+1

            for i in range(syllableCount):
        '''

            for syllable in syllablesIPA:
                startVowels = -1
                endVowels = -1
                i = 0
                startSet = False

                while i < len(syllable):
                    if syllable[i] in vowelSet:
                        if not startSet:
                            startVowels = i
                            startSet = True
                        endVowels = i
                    else:
                        if startSet:
                            break
                    i += 1

                onset, nucleus, coda = 'none', 'none', 'none'

                if (startVowels > 0):
                    onset = syllable[:startVowels]

                nucleus = syllable[startVowels:endVowels+1]

                if (endVowels < len(syllable)-1) and (endVowels != -1):
                    coda = syllable[endVowels+1:]

                reply += f' Syllable: {syllable}\n'
                reply += f'   Onset: {onset}\n'
                reply += f'   Nucleus: {nucleus}\n'
                reply += f'   Coda: {coda}\n'
        
        await message.channel.send(reply)

    async def handle_help(self,message):
        await message.channel.send("Type '$ipa [word or sentence]' for a word/sentence to translate.\n\nType '$translate [from-lang] [to-lang] [word or sentence]' to translate between any two available languages.\n\nThese languages are currently available: Arabic (ar), Chinese (zh), English (en), French (fr), German (de), Hindi (hi), Italian (it), Japanese (ja), Polish (pl), Portuguese (pt), Turkish (tr), Russian (ru), and Spanish (es).\n\nPlease specify the two-letter code of any language used in a translation command.\n\nType '$syllabify [word or sentence]' to get a complete syllabification analysis of any word or sentence.")    

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
