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
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import StanfordTagger
from nltk.tokenize import RegexpTokenizer
#import epitran
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from io import BytesIO

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
            #argostranslate.package.install_from_path(package_to_install.download())
            mappings.add((from_code, to_code))
            processed.add(from_code)
            print((from_code, to_code))

###------------------------------TOKEN LOADERS + Error Debugging------------------------------###
load_dotenv()
DISCORD_TOKEN = os.getenv('TOKEN')
GUILD_ID = [int(guild.strip()) for guild in os.getenv('GUILD').split(',')]
ALLOWED_CHANNELS = [int(channel.strip()) for channel in os.getenv('ALLOWED_CHANNELS').split(',')]
OTHER_GUILD_ID = int(os.getenv("OTHER_GUILD_ID"))
OTHER_CHANNEL_ID = int(os.getenv("OTHER_CHANNEL_ID"))

# Print the lists for verification
print("GUILD_ID:", GUILD_ID)
print("ALLOWED_CHANNELS:", ALLOWED_CHANNELS)

# DICTIONARY_TOKEN = os.getenv('DICTIONARY')
# THESAURUS_TOKEN = os.getenv('THESAURUS')
# LEARNERS_TOKEN = os.getenv('LEARNERS') # for IPA
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
###-------------------------------------------------------------------------------------------###

# app = Flask(__name__)
# CORS(app)

# @app.route('/api/command', methods=['POST'])
# def handle_command():
#     try:
#         data = request.json
#         command = data.get('command')
#         text = data.get('text')
#         from_lang = data.get('fromLang')
#         to_lang = data.get('toLang')

#         result = ""
#         if command == 'ipa':
#             # Use gruut for IPA translation
#             for sent in sentences(text, lang="en-us"):
#                 for word in sent:
#                     if word.phonemes:
#                         result += f"/{' '.join(word.phonemes)}/ "
#         elif command == 'translate':
#             if (from_lang, to_lang) in mappings:
#                 result = argostranslate.translate.translate(text, from_lang, to_lang)
#             else:
#                 # Try intermediate translation
#                 for code in codes:
#                     if code == from_lang or code == to_lang:
#                         continue
#                     if (from_lang, code) in mappings and (code, to_lang) in mappings:
#                         temp = argostranslate.translate.translate(text, from_lang, code)
#                         result = argostranslate.translate.translate(temp, code, to_lang)
#                         break
#         elif command == 'syllabify':
#             # Call existing syllabification logic and store result
#             # This would need to be adapted from your existing handle_syllabification method
#             # call the syllabification function down below
#                         # Use helper function for syllabification
#             result = handle_syllabification_helper(text)
            
#             # Define helper function outside the class
#             async def handle_syllabification_helper(message):
#                 # Copy the syllabification logic from MyDiscord.handle_syllabification
#                 # but remove self references and return the result instead of sending messages
#                 # Source: https://en.wikipedia.org/wiki/IPA_vowel_chart_with_audio
#                 vowels = set(['i','y','ɨ','ʉ','ɯ','u','ɪ','ʏ','ʊ','e','ø','ɘ','ɵ','ɤ','o','ə','ɛ','œ','ɜ','ɞ','ʌ','ɔ','æ',
#                 'ɐ','a','ɶ','ä','ɑ','ɒ','ɚ'])

#                 # Source: https://en.wikipedia.org/wiki/Diphthong
#                 diphthongs = set(['oʊ', 'aʊ', 'aɪ', 'eɪ', 'ɔɪ'])

#                 # Source: https://en.wikipedia.org/wiki/Help:IPA/English
#                 onsetClusters = set(['p','b','t','ɾ','d','tʃ','dʒ','k','ɡ','dj','ð','f','g','h','j',
#                 'k','l','lj','m','n','nj','ɹ','s','ʃ','v','w','z','ʒ','θ','pl','bl','kl','gl','pɹ','bɹ','tɹ','dɹ','kɹ',
#                 'gɹ','ɡɹ','ɡ','tw','dw','gw','kw','pw','fl','sl','θl','ʃl','fɹ','θɹ','ʃɹ','sw','θw','vw','pj','bj','tj','kj','gj',
#                 'mj','fj','vj','θj','sj','zj','hj','lj','sp','st','sk','sm','sn','sf','sθ','spl','skl','spɹ','stɹ','skw',
#                 'spj','stj','skj','smj','snj','sfɹ'])

#                 try:
#                     def remove_diacritics(s):
#                         # Normalize to NFD (Normalization Form D) to decompose characters
#                         s_decomposed = unicodedata.normalize('NFD', s)
                        
#                         # Filter out combining diacritic marks
#                         s_no_diacritics = ''.join(c for c in s_decomposed if not unicodedata.combining(c))
                    
#                         # Optionally, normalize back to NFC (Normalization Form C) if needed
#                         return unicodedata.normalize('NFC', s_no_diacritics)

#                     def find_onsets(cluster):
#                         n = len(cluster)
#                         lengths = []
                
#                         # Iterate over all possible starting points for substrings
#                         for start in range(len(cluster)):
#                             # Iterate over all possible ending points for substrings starting from `start`
#                             for end in range(start + 1, n + 1):
#                                 substring = cluster[start:end]
#                                 if substring in onsetClusters:
#                                     lengths.append(((end-start), start, end))
                    
#                         return sorted(lengths, reverse=True, key=lambda x: x[0])
                    
#                     cleaned_string = re.sub(r'[^a-zA-Z\s-]', '', message.content[len('$syllabify '):])
#                     reply = ''
#                     words = []
#                     ipa = []

#                     # Convert each word in the sentence to IPA
#                     for sent in sentences(cleaned_string,lang="en-us"):
#                         for word in sent:
#                             if (word.phonemes):
#                                 words.append(word.text)
#                                 ipa.append(remove_diacritics(((''.join(word.phonemes)).replace("ˈ","")).replace("ˌ","")))
                    
#                     if not ipa:
#                         await message.reply('Please include at least one alphabetic character in your prompt!', mention_author=False)
#                         return

#                     for word in ipa:
#                         reply += '•••••••••••••••\n'
                                
#                         reply += f'Word: {words[ipa.index(word)]} ({word})\n'
#                         syllables = []
#                         i = 0

#                         while i < len(word):
#                             # Find the next vowel or diphthong
#                             j = i
#                             while j < len(word) and word[j] not in vowels:
#                                 j += 1
#                             if j == len(word):
#                                 break

#                             # Check for diphthong
#                             if j < len(word) - 1 and word[j:j+2] in diphthongs:
#                                 nucleus_end = j + 1
#                             else:
#                                 nucleus_end = j

#                             # Find the onset of the next syllable
#                             k = nucleus_end + 1
#                             while k < len(word) and word[k] not in vowels:
#                                 k += 1
                            
#                             if k < len(word):
#                                 onsets = find_onsets(word[nucleus_end+1:k])
                                
#                                 # Find the longest onset cluster whose next character is a vowel
#                                 if onsets:
#                                     for onset in onsets:
#                                         if (word[nucleus_end+1+onset[0]+onset[1]] in vowels):
#                                             coda_end = nucleus_end+onset[1]
#                                             break
#                                 else:
#                                     coda_end = k-1
#                             else:
#                                 coda_end = len(word) - 1

#                             syllables.append((i, coda_end))
#                             i = coda_end + 1
                        
#                         reply += f'Syllable count: {len(syllables)}\n'

#                         for idx, (start, end) in enumerate(syllables):
#                             syllable_text = word[start:end+1]
#                             reply += f'  Syllable: {syllable_text}\n'

#                             # Find onset
#                             j = start
#                             while j <= end and word[j] not in vowels:
#                                 j += 1
#                             if j > start:
#                                 reply += f'     Onset: {word[start:j]}\n'
#                             else:
#                                 reply += f'     Onset: none\n'

#                             # Find nucleus
#                             k = j
#                             while k <= end and (word[k] in vowels or (k < end and word[k:k+2] in diphthongs)):
#                                 k += 1
#                             reply += f'     Nucleus: {word[j:k]}\n'

#                             # Find coda
#                             if k <= end:
#                                 reply += f'     Coda: {word[k:end+1]}\n'
#                             else:
#                                 reply += f'     Coda: none\n'

#                     await message.channel.send(reply)
                    
#                 except Exception as e:
#                     await message.channel.send(f'Sorry! An error occurred: {e}')
#                 # Add the rest of the syllabification logic here, returning the result as a string
#                 return "Syllabification analysis: " + text  # Replace with actual implementation
#         elif command == 'tree':
#             # Call existing tree generation logic and store result
#             # This would need to be adapted from your existing handle_syntax_tree method
#             result = "Tree generation functionality to be implemented"
#         elif command == 'logic':
#             # Call existing logic translation and store result
#             # This would need to be adapted from your existing handle_logic method
#             result = "Logic translation functionality to be implemented"
#         elif command == 'morphology':
#             # Call existing morphological analysis and store result
#             # This would need to be adapted from your existing handle_morphology method
#             result = "Morphological analysis functionality to be implemented"

#         return jsonify({'result': result})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # Start Flask server when running directly
# if __name__ == '__main__':
#     # Start Discord bot in a separate thread
#     import threading
#     bot_thread = threading.Thread(target=lambda: client.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG))
#     bot_thread.start()
    
#     # Start Flask server
#     app.run(port=5000)

class MyDiscord(discord.Client):
    
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.other_guild_id = int(os.getenv("OTHER_GUILD_ID"))
        self.other_channel_id = int(os.getenv("OTHER_CHANNEL_ID"))
        
    def get_wordnet_pos(self, treebank_tag):
            if treebank_tag.startswith('J'):
                return wordnet.ADJ
            elif treebank_tag.startswith('V'):
                return wordnet.VERB
            elif treebank_tag.startswith('N'):
                return wordnet.NOUN
            elif treebank_tag.startswith('R'):
                return wordnet.ADV
            else:
                return wordnet.NOUN
    
      
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        # Access the other server's channel
        other_guild = self.get_guild(self.other_guild_id)
        if other_guild:
            other_channel = other_guild.get_channel(self.other_channel_id)
            if other_channel:
                print("WugBot is now online in UCLA Ling server!")
            else:
                print("Channel not found in the other server.")
        else:
            print("Guild not found.")

    async def on_message(self, message, *args, **kwargs):
        
        allowed_channels = ALLOWED_CHANNELS
        allowed_guild = GUILD_ID
        #print(allowed_channels, allowed_guild)
        try:
            if message.author.bot or message.author == self.user:
                return

            if message.channel.id in allowed_channels and message.guild.id in allowed_guild:
                commands_dict = {
                    '$wug' : self.handle_wug,
                    '$ipa ' : self.handle_ipa,
                    '$translate ' : self.handle_translation,
                    '$help' : self.handle_help,
                    '$syllabify ' : self.handle_syllabification,
                    '$tree ' : self.handle_syntax_tree,
                    '$logic ' : self.handle_logic,
                    '$morphology ' : self.handle_morphology
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
        except Exception as e:
            await message.channel.send(f'Sorry! An error occurred: {e}')
                
    async def handle_wug(self,message):
        await message.channel.send("Wug's here!")
        
    # ping a user everytime the user types the sob emoji
 
    async def ping_jen(self, message):
        if message.author.id == 475601737726558219 and ':sob:' in message.content and message.channel.id in ALLOWED_CHANNELS:
            await message.channel.send(f"@a.ira ")
        if message.author.id == 461228583768293386 and ':sob:' in message.content and message.channel.id in ALLOWED_CHANNELS:
            await message.channel.send(f"@__iu__ ")

    async def handle_ipa(self,message): 
        try:
             # Initialize epitran with Tagalog/Filipino support
            # epi_tl = epitran.Epitran('tgl-Latn')
            
            text_to_translate = message.content[len('$ipa '):].strip().encode('utf-8').decode('utf-8', errors='ignore')
            
            # Check if text starts with "tl:" for Tagalog
            # if text_to_translate.startswith('tl:'):
            #     # Remove the prefix and get Tagalog IPA
            #     tagalog_text = text_to_translate[3:].strip()
            #     ipa_text = epi_tl.transliterate(tagalog_text)
            #     await message.channel.send(f'Tagalog IPA Translation: /{ipa_text}/')
            #     return
                
            # Default English IPA using gruut
            for sent in sentences(text_to_translate,lang="en-us"):
                for word in sent:
                    if word.phonemes:
                        phonemes_str = ' '.join(word.phonemes)
                        await message.channel.send(f'IPA Translation: /{phonemes_str}/')
                        
        except Exception as e:
            await message.channel.send(f'Sorry! An error occurred: {e}')

    async def handle_translation(self,message):
        try:
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
        except Exception as e:
            await message.channel.send(f'Sorry! An error occurred: {e}')


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

        try:
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
            
        except Exception as e:
            await message.channel.send(f'Sorry! An error occurred: {e}')
        
    
    
    
    async def handle_syntax_tree(self, message):
        try:
            # Replace contractions
            prompt = message.content[len('$tree '):].replace("'", '').lower()
            words = re.sub(r'[^a-zA-Z\s]', '', prompt)  # Modify to keep hyphens

            # Extract nouns, verbs, and prepositions from WordNet
            def get_words(pos_tag):
                return list(set(word for synset in wordnet.all_synsets(pos_tag) for word in synset.lemma_names()))
            
            nouns = get_words(wordnet.NOUN)
            verbs = get_words(wordnet.VERB)
            adjectives = get_words(wordnet.ADJ)
            adverbs = get_words(wordnet.ADV)

            prepositions = [
                "about", "above", "across", "after", "against", "along", "among", "around", "at", 
                "before", "behind", "below", "beneath", "beside", "between", "beyond", "by", 
                "down", "during", "except", "for", "from", "in", "inside", "into", "near", "of", 
                "off", "on", "out", "outside", "over", "past", "since", "through", "throughout", 
                "to", "toward", "under", "underneath", "until", "up", "upon", "with", "within", 
                "without", "to","me"
            ]

            # https://www.vedantu.com/english/auxiliaries-and-modal-verbs#:~:text=The%20modal%20auxiliary%20words%20are,to%2C%20used%20to%2C%20etc.
            modals = [
                "can", "could", "may", "might", "must", "shall", "should", "will", "would"
            ]

            auxiliaries = [
                "have", "be", "been", "am", "are", "is"
            ]

            # Replace possessives later with their formal representations. Forget about D' for now
            determiners = [
                "the", "a", "an", "this", "that", "his", "her", "their", "its", "my", "your"
            ]

            DP_subjs = [
                "i", "you", "he", "she", "it", "we", "they", "this", "that"
            ]

            DP_objs = [
                "me", "you", "him", "her", "it", "us", "them", "this", "that"
            ]

            complementizers = [
                "that", "if", "whether", "for", '∅'
            ]
            
            interjections = [
                "for", "oh", "wow", "yay", "yes", "no", "okay", "alas", "ouch", "oops", "uh", "uh-oh", "ugh", "yikes"   
            ]

            def clean_word(word):
                """ Clean the word by removing problematic characters. """
                return word.replace('-', '_').replace("'", "")  # Replace hyphens with underscores and remove apostrophes

            # Example CFG with dynamically added words
            nouns_str = " | ".join([f"'{clean_word(noun)}'" for noun in nouns])  
            verbs_str = " | ".join([f"'{clean_word(verb)}'" for verb in verbs])  
            adjectives_str = " | ".join([f"'{clean_word(adjective)}'" for adjective in adjectives])  
            adverbs_str = " | ".join([f"'{clean_word(adverb)}'" for adverb in adverbs])  
            prepositions_str = " | ".join([f"'{preposition}'" for preposition in prepositions])
            tense_str = "'+PAST' | '-PAST' | 'to' | " + " | ".join([f"'{modal}'" for modal in modals])
           #  print(f'tense_str: {tense_str}') # why is it not printing...
            determiners_str = " | ".join([f"'{determiner}'" for determiner in determiners])
            # workaround for now, should probably find a way to separate the subj and obj positions
            misc_DPs_str = " | ".join([f"'{DP}'" for DP in (DP_subjs + DP_objs)])
            print(misc_DPs_str)
            auxiliaries_str = " | ".join([f"'{auxiliary}'" for auxiliary in auxiliaries])
            complementizers_str = " | ".join([f"'{complementizer}'" for complementizer in complementizers])

            # I cannot add complementizers right now, since it doesn't seem to even parse unless the input can get a root node?

            # no support for negation yet or other features, so no need to replace
            grammar = nltk.CFG.fromstring(f"""
                CP -> C TP | TP
                QP -> Q TP
                TP -> DP TBar | T TBar
                T -> T VP | T DP | T AP | T PP | T AdvP | T PP
                TBar -> T AuxP | T VP 
                AuxP -> Aux VP
                VP -> V CP | V DP | V AP | VP PP | VP AdvP | V | V PP
                DP -> D NP | DP PP | _D_
                NP -> AP NP | NP PP | N | N PP
                PP -> P DP
                AP -> A
                AdvP -> Adv 
                Q -> 'can' | 'could' | 'will' | 'would' | 'should' | 'may' | 'might'
                C -> {complementizers_str}
                _D_ -> {misc_DPs_str}
                N -> {nouns_str}
                V -> {verbs_str}
                P -> {prepositions_str}
                T -> {tense_str} | 'did'
                D  -> {determiners_str}
                A -> {adjectives_str}
                Adv -> {adverbs_str}
                Aux -> {auxiliaries_str} | 'did;
            """)

            # Tokenize the sentence
            tokenizer = RegexpTokenizer('(?u)\W+|\$[\d\.]+|\S+')

            # https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
            wordnet_lemmatizer = WordNetLemmatizer()
            tokens = tokenizer.tokenize(words)
            tagged_tokens = nltk.pos_tag(tokens)
            lemmatized_tokens = []
            for token in tagged_tokens:
                lemmatized_token = token[0]
                if (token[1].startswith('N')):
                    lemmatized_token = wordnet_lemmatizer.lemmatize(token[0], 'n')
                elif (token[1].startswith('V')):
                    lemmatized_token = wordnet_lemmatizer.lemmatize(token[0], 'v')
                elif (token[1].startswith('J')):
                    lemmatized_token = wordnet_lemmatizer.lemmatize(token[0], 'a')
                elif (token[1].startswith('R') and token[1] != 'RP'):
                    lemmatized_token = wordnet_lemmatizer.lemmatize(token[0],'r')
                if not any (c.isspace() for c in lemmatized_token):
                    #print(lemmatized_token)
                    #print(f'this tokens label is: {token[1]}\n')
                    # do not consider auxiliaries
                    if (token[1].startswith('V')):
                        # it might be calculating the index wrong due to a typo
                        # tagged_tokens.index(token) > 0 and not tagged_tokens[tagged_tokens.index(token)-1][1].startswith('V')):
                        if token[1] in ['VBD', 'VBN']:
                            lemmatized_tokens.append('+PAST')
                        else:
                            lemmatized_tokens.append('-PAST')
                         #   lemmatized_tokens.append('-PAST')
                           # print(f'added after: {token[0]}')
                lemmatized_tokens.append(lemmatized_token)
            lemmatized_tokens.insert(0, '∅')

            filtered_tokens = [t for t in lemmatized_tokens if not any(c.isspace() for c in t)]
            #print(f'tokens after filtering: {filtered_tokens}') # why is it not parsing???
                
            reply = ''

            # Parse the sentence
            parser = nltk.ChartParser(grammar) # issue: there are no trees being generated?
            trees = list(parser.parse(filtered_tokens))
            
            def tree_to_ascii_art(tree):
                return tree.__str__()
            
            if not trees:
                await message.channel.send("Sorry, can't parse this sentence with current grammar")
                
            for i, tree in enumerate(trees, 1):
            # Convert the tre to ASCII art
                ascii = nltk.tree.TreePrettyPrinter(tree).text()
                # print(var)

            # Convert the tree to ASCII art
                ascii_tree = tree_to_ascii_art(tree)
                
                # Split the ASCII tree into chunks if it's too long
                # max_message_length = 2000  # Discord's message length limit
                # tree_chunks = [ascii_tree[i:i+max_message_length] for i in range(0, len(ascii_tree), max_message_length)]
                
                # Send the ASCII tree as one or more messages
                await message.channel.send(f"Parse Tree {i}:")
                # for chunk in tree_chunks:
                await message.channel.send(f"```\n{ascii}\n```")
                
            for tree in parser.parse(filtered_tokens):
                fig = plt.figure()
                nltk.tree.Tree.fromstring(str(tree)).draw()
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                file = discord.File(buffer, filename='syntax_tree.png')
                await message.channel.send(file=file)
                plt.clf()
                plt.close(fig)
                
                parse_string = ' '.join(str(tree).split()) 
                reply += parse_string
               #  print(f'tokens: {parse_string}')
            
            await message.channel.send(reply)

        except Exception as e:
            await message.channel.send(f'Sorry! An error occurred: {e}')
            
    # Translate sentences into propositonal/predicate logic
    async def handle_logic(self, message):
        try:
            text = message.content[len('$logic '):].strip()
            tokens = nltk.word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            
            # Simple mapping of POS tags to logic symbols
            logic_mapping = {
                'NN': 'N',  # Noun
                'VB': 'V',  # Verb
                'VBD': 'V',  # Past Tense Verb
                'VBG': 'V',  # Gerund Verb
                'VBN': 'V',  # Past Participle Verb
                'VBP': 'V',  # Non-3rd Person Singular Present Verb
                'VBZ': 'V',  # 3rd Person Singular Present Verb
                'JJ': 'A',  # Adjective
                'RB': 'Adv',  # Adverb
                'DT': 'D',  # Determiner
                'IN': 'P',  # Preposition
                'PRP': 'Pron',  # Pronoun
                'CC': 'Conj',  # Conjunction
                'TO': 'Inf',  # Infinitive marker
                'MD': 'Mod',  # Modal
                'NEG': 'Neg'  # Negation
            }
            
            logic_representation = []
            for word, pos in pos_tags:
                logic_symbol = logic_mapping.get(pos, pos)
                logic_representation.append(f"{logic_symbol}({word})")
            
            logic_sentence = ' ∧ '.join(logic_representation)
            await message.channel.send(f"Logic Representation: {logic_sentence}")
            
        except Exception as e:
            await message.channel.send(f'Sorry! An error occurred: {e}')
            
    # Do a morphological analysis of a word or a sentence in a language of choice (e.g., English)
    # Install spacy but after installing spacy, do pip install numpy<2.0.0 
    # BUT this model is trash in terms of accuracy so we are scratching it for now
    async def handle_morphology(self, message):
        try:
            lemmatizer = WordNetLemmatizer()
            prefixes = {
                'un': 'negation',
                're': 'again',
                'dis': 'not',
                'pre': 'before',
                'post': 'after',
                'anti': 'against',
                'pro': 'for',
                'sub': 'under',
                'inter': 'between',
                'super': 'above',
                'semi': 'half',
                'bi': 'two',
                'tri': 'three',
                'quad': 'four',
                'multi': 'many',
                'non': 'not',
                'in': 'not',
                'im': 'not',
                'il': 'not',
                'ir': 'not',
                'mis': 'wrong',
                'over': 'too much',
                'under': 'too little',
                'hyper': 'too much',
                'hypo': 'too little',
                'sub': 'under',
                'super': 'above',
                'ultra': 'beyond',
                'out': 'beyond',
                'extra': 'beyond',
                'intra': 'within',
                'intro': 'within',
                'extra': 'beyond',
                'ex': 'former',
                'co': 'with',
                'com': 'with',
                'con': 'with',
                'col': 'with',
                'cor': 'with',
                'syn': 'with',
                'sym': 'with',
                'de': 'down',
                'dis': 'away',
                'ex': 'out',
                'em': 'in',
                'en': 'in',
                'fore': 'before',
                'in': 'in',
                'im': 'in',
                'il': 'in',
                'ir': 'in',
            }
            suffixes = {
                'ing': {'type': 'inflectional', 'meaning': 'continuous action'},
                'ed': {'type': 'inflectional', 'meaning': 'past tense'},
                'er': {'type': 'derivational', 'meaning': 'agent'},
                'tion': {'type': 'derivational', 'meaning': 'process'},
                'ness': {'type': 'derivational', 'meaning': 'quality'},
                'ly': {'type': 'derivational', 'meaning': 'manner'},
                'ful': {'type': 'derivational', 'meaning': 'full of'},
                'able': {'type': 'derivational', 'meaning': 'can be'},
                'less': {'type': 'derivational', 'meaning': 'without'},
                'est': {'type': 'derivational', 'meaning': 'superlative'},
                's': {'type': 'inflectional', 'meaning': 'plural'},
                'es': {'type': 'inflectional', 'meaning': 'plural'},
            }
            
            cases = {
                'nominative': 'subject',
                'accusative': 'direct object',
                'dative': 'indirect object',
                'genitive': 'possessive',
            }
            
            text = message.content[len('$morphology '):].strip()
            tokens = nltk.word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            
            # morphemes = []
            reply = []
            for word, pos in pos_tags:
                analysis = []
                analysis.append(f"\n**Word Analysis: {word}**")
                
                # Plural rules
                plural_rules = {
                    'es_words': ['bush', 'box', 'church', 'dish', 'watch'],
                    'irregular_plurals': {
                        'leaves': 'leaf',
                        'lives': 'life',
                        'shelves': 'shelf',
                        'wolves': 'wolf',
                        'children': 'child',
                        'people': 'person',
                        'mice': 'mouse',
                        'geese': 'goose',
                        'teeth': 'tooth',
                        'feet': 'foot',
                    }
                }
                
                # POS Identification
                pos_name = {
                    'NN': 'Noun', 
                    'VB': 'Verb',
                    'JJ': 'Adjective',
                    'RB': 'Adverb',
                    'DT': 'Determiner',
                    'IN': 'Preposition',
                    'PRP': 'Pronoun',
                    'CC': 'Conjunction',
                    'TO': 'Infinitive',
                    'MD': 'Modal',
                    'NEG': 'Negation',
                    'CD': 'Cardinal Number',
                    'UH': 'Interjection',
                    'FW': 'Foreign Word',
                    'SYM': 'Symbol',
                    'LS': 'List Item',
                    'PDT': 'Predeterminer',
                    'POS': 'Possessive Ending',
                    'RP': 'Particle',
                    'WP': 'Wh-pronoun',
                }.get(pos[:2], 'Unknown')
                analysis.append(f"Part of Speech: {pos_name}")
                
                # Base form
                analysis.append(f"Base Form: {word}")
                
                # Track Morphological Process
                process_steps = []
                current_form = str(word)
                base_form = str(lemmatizer.lemmatize(word, self.get_wordnet_pos(pos)))

                                
                # Morpheme breakdown
                root = word
                found_morphemes = []
                
                
                # Document Transformation rules
                if word.endswith('ing'):
                    if base_form.endswith('e'):
                        step = f"{base_form} → {base_form[:-1]} (e-dropping)"
                        process_steps.append(str(step))
                        current_form = base_form[:-1]
                    step = f"{current_form} → {current_form} (add -ing)"
                    process_steps.append(str(step))
                    
                elif word.endswith('ed'):
                    if base_form.endswith('e'):
                        step = f"{base_form} → {base_form[:-1]} (e-dropping)"
                        process_steps.append(str(step))
                        current_form = base_form[:-1]
                    step = f"{current_form} → {current_form + 'ed'} (add -ed)"
                    
                elif word.endswith('ful'):
                    step = f"{base_form} → {base_form[:-3]} (ful to nothing)"
                    process_steps.append(str(step))
                    current_form = base_form[:-3]
                    step = f"{current_form} → {current_form + 'ful'} (add -ful)"
            
                    
                elif word.endswith('s'):
                    if base_form.endswith('y'):
                        step = f"{base_form} → {base_form[:-1]} (y to i)"
                        process_steps.append(str(step))
                        current_form = base_form[:-1]
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                
                elif word.endswith('s') and base_form.endswith('ch'):
                    step = f"{base_form} → {base_form + 'tch'} (ch to tch)"
                    process_steps.append(str(step))
                    current_form = base_form + 'tch'
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                    
                
                elif word.endswith('s') and base_form.endswith('sh'):
                    step = f"{base_form} → {base_form + 'sh'} (sh to sh)"
                    process_steps.append(str(step))
                    current_form = base_form + 'sh'
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                
                elif word.endswith('s') and base_form.endswith('es'):
                    step = f"{base_form} → {base_form + 'x'} (x to x)"
                    process_steps.append(str(step))
                    current_form = base_form + 'x'
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                
                elif word.endswith('s') and base_form.endswith('z'):
                    step = f"{base_form} → {base_form + 'z'} (z to z)"
                    process_steps.append(str(step))
                    current_form = base_form + 'z'
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                
                elif word.endswith('s') and base_form.endswith('s'):
                    step = f"{base_form} → {base_form + 'es'} (s to es)"
                    process_steps.append(str(step))
                    current_form = base_form + 'es'
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                
                elif word.endswith('s') and base_form.endswith('f'):
                    step = f"{base_form} → {base_form[:-1] + 've'} (f to ve)"
                    process_steps.append(str(step))
                    current_form = base_form[:-1] + 've'
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                
                elif word.endswith('s') and base_form.endswith('fe'):
                    step = f"{base_form} → {base_form[:-2] + 've'} (fe to ve)"
                    process_steps.append(str(step))
                    current_form = base_form[:-2] + 've'
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                
                elif word.endswith('s') and base_form.endswith('o'):
                    step = f"{base_form} → {base_form + 'e'} (o to oe)"
                    process_steps.append(str(step))
                    current_form = base_form + 'e'
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                
                elif word.endswith('s') and base_form.endswith('y'):
                    step = f"{base_form} → {base_form[:-1] + 'i'} (y to i)"
                    process_steps.append(str(step))
                    current_form = base_form[:-1] + 'i'
                    step = f"{current_form} → {current_form + 's'} (add -s)"
                                
                if process_steps:
                    analysis.append("\n**Morphological Process: **")
                    analysis.extend([str(step) for step in process_steps])
                
                if word.endswith('es'):
                # Check if word is in irregular plurals
                    if word in plural_rules['irregular_plurals']:
                        root = plural_rules['irregular_plurals'][word]
                    # Check if word needs -es plural
                    elif word[:-2] in plural_rules['es_words']:
                        root = word[:-2]
                    # Handle words ending in -s/-sh/-ch/-x/-z
                    elif any(word[:-2].endswith(x) for x in ['s', 'sh', 'ch', 'x', 'z']):
                        root = word[:-2]
                    else:
                        root = lemmatizer.lemmatize(word, self.get_wordnet_pos(pos))
                elif word.endswith('oes'):
                    if word in plural_rules['irregular_plurals']:
                        root = plural_rules['irregular_plurals'][word]
                    elif word[:-3] in plural_rules['es_words']:
                        root = word[:-3]
                    elif any(word[:-3].endswith(x) for x in ['s', 'sh', 'ch', 'x', 'z']):
                        root = word[:-3]
                    else:
                        root = lemmatizer.lemmatize(word, self.get_wordnet_pos(pos))
                else:
                    root = lemmatizer.lemmatize(word, self.get_wordnet_pos(pos))
                
                
                # Prefix Analysis
                for prefix, meaning in prefixes.items():
                    if word.startswith(prefix):
                        #root = root[len(prefix):]
                        found_morphemes.append(f"Prefix: '{prefix}-': ({meaning})")
                
                for suffix, info in suffixes.items():
                    if word.endswith(suffix):
                        #root = root[:-len(suffix)]
                        found_morphemes.append(f"Suffix: '-{suffix}': ({info['type']}, {info['meaning']})")
                        
                # Root word
                analysis.append(f"Root: {root}")
                
                # Morhpemes Found
                if found_morphemes:
                    analysis.append("Morphemes Found:")
                    for m in found_morphemes:
                        analysis.append(f"- {m}")
                        
                 # Rules applied
                if word.endswith('ing') and not root.endswith('e'):
                    analysis.append("Rule: e-dropping before -ing")
                if word.endswith('ed') and len(root) > 1 and root[-1] == root[-2]:
                    analysis.append("Rule: consonant doubling")
                if word.endswith('ed') and root.endswith('e'):
                    analysis.append("Rule: e-dropping before -ed")
                if word.endswith('s') and root.endswith('y'):
                    analysis.append("Rule: y to i before -s")
                if word.endswith('s') and root.endswith('o'):
                    analysis.append("Rule: o to oe before -s")
                if word.endswith('s') and root.endswith('ch'):
                    analysis.append("Rule: ch to tch before -s")
                if word.endswith('s') and root.endswith('sh'):
                    analysis.append("Rule: sh to sh before -s")
                if word.endswith('s') and root.endswith('x'):
                    analysis.append("Rule: x to x before -s")
                if word.endswith('s') and root.endswith('z'):
                    analysis.append("Rule: z to z before -s")
                if word.endswith('s') and root.endswith('s'):
                    analysis.append("Rule: s to es before -s")
                if word.endswith('s') and root.endswith('f'):
                    analysis.append("Rule: f to ve before -s")
                if word.endswith('s') and root.endswith('fe'):
                    analysis.append("Rule: fe to ve before -s")
                    
                
                reply.extend(analysis)
            
            await message.channel.send('\n'.join(reply))
            
                
        except Exception as e:
            await message.channel.send(f'Sorry! An error occurred: {e}')
            
    async def handle_help(self,message):
        await message.channel.send("Type '$ipa [word or sentence]' for a word/sentence to translate.\n\nType '$translate [from-lang] [to-lang] [word or sentence]' to translate between any two available languages.\n\nThese languages are currently available: Arabic (ar), Chinese (zh), English (en), French (fr), German (de), Hindi (hi), Italian (it), Japanese (ja), Polish (pl), Portuguese (pt), Turkish (tr), Russian (ru), and Spanish (es).\n\nPlease specify the two-letter code of any language used in a translation command.\n\nType '$syllabify [word or sentence]' to get a complete syllabification analysis of any word or sentence. \n\n Type '$tree [sentence]' to get a syntax tree of a sentence. \n\n Type '$logic [sentence]' to get a logical representation of a sentence. \n\n Type '$morphology [word or sentence]' to get a morphological analysis of a word or sentence.")    

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = MyDiscord(intents=intents)
client.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)