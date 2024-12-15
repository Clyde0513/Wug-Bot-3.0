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

class MyDiscord(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.other_guild_id = int(os.getenv("OTHER_GUILD_ID"))
        self.other_channel_id = int(os.getenv("OTHER_CHANNEL_ID"))
        
      
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
        
    async def handle_ipa(self,message):
        try:
            text_to_translate = message.content[len('$ipa '):].strip()
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
        # You only have to download these once
        # nltk.download('wordnet') 
        # nltk.download('averaged_perceptron_tagger_eng')
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
                "without", "to"
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
                CP -> C TP
                TP -> DP TBar
                TBar -> T AuxP
                TBar -> T VP
                AuxP -> Aux VP
                VP -> V CP
                VP -> V DP
                VP -> V AP
                VP -> VP PP
                VP -> VP AdvP
                VP -> V
                DP -> D NP
                NP -> AP NP
                NP -> NP PP
                NP -> N
                PP -> P DP
                AP -> A
                AdvP -> Adv 
                DP -> _D_  
                C -> {complementizers_str}
                _D_ -> {misc_DPs_str}
                N -> {nouns_str}
                V -> {verbs_str}
                P -> {prepositions_str}
                T -> {tense_str}
                D  -> {determiners_str}
                A -> {adjectives_str}
                Adv -> {adverbs_str}
                Aux -> {auxiliaries_str}
            """)

            # print(verbs_str)

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
                    print(lemmatized_token)
                    print(f'this tokens label is: {token[1]}\n')
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
            print(f'tokens after filtering: {filtered_tokens}') # why is it not parsing???
                
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
                'JJ': 'A',  # Adjective
                'RB': 'Adv',  # Adverb
                'DT': 'D',  # Determiner
                'IN': 'P',  # Preposition
                'PRP': 'Pron',  # Pronoun
                'CC': 'Conj',  # Conjunction
                'TO': 'Inf',  # Infinitive marker
                'MD': 'Mod'  # Modal
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
    # BUT this model is trash so we are scratchign it for now
    async def handle_morphology(self, message):
        def get_wordnet_pos(treebank_tag):
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
        try:
            text = message.content[len('$morphology '):].strip()
            tokens = nltk.word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            
            morphemes = []
            for word, pos in pos_tags:
                # Simple heuristic-based morphological analysis
                root = word
                suffix = ''
                prefix = ''
                infixes = []
                case = "nominative" # Default case
                

                # Example suffixes
                suffixes = ['ing', 'ed', 's', 'es', 'ly', 'er', 'est', 'able', 'ible', 'ness', 'ment', 'ful', 'less', 'ous', 'tion', 'ation', 'ition', 'al', 'ial', 'ic', 'ical', 'y', 'ty', 'ive', 'ative', 'itive', 'en', 'ify', 'ize', 'ise', 'ward', 'wards', 'wise']
                prefixes = ['un', 're', 'in', 'im', 'il', 'ir', 'dis', 'en', 'em', 'non', 'in', 'im', 'over', 'mis', 'sub', 'pre', 'inter', 'fore', 'de', 'trans', 'super', 'semi', 'anti', 'mid', 'under']
                dative_suffixes = ['to', 'for']
                accusative_suffixes = ['me', 'us', 'him', 'her', 'it', 'them']
                genitive_suffixes = ['my', 'mine', 'our', 'ours', 'your', 'yours', 'his', 'her', 'hers', 'its', 'their', 'theirs']
                reflexive_suffixes = ['self', 'selves']
                possessive_suffixes = ['s', 's\'']
                plural_suffixes = ['s', 'es']
                comparative_suffixes = ['er', 'est']
                superlative_suffixes = ['est']
                adverbial_suffixes = ['ly']
                nominal_suffixes = ['ity', 'ness', 'hood', 'ship', 'dom', 'ism', 'ist', 'ment', 'tion', 'sion', 'ance', 'ence', 'age', 'ery', 'ry', 'al', 'ial', 'ion', 'ation', 'ition', 'ity', 'ty', 'y', 'cy', 'acy', 'ance', 'ence', 'dom', 'ship', 'hood', 'ism', 'ist', 'ment', 'ness', 'ship', 'sion', 'tion', 'ity', 'ty', 'y', 'al', 'ial', 'ic', 'ical', 'ous', 'eous', 'ious', 'ive', 'ative', 'itive', 'en', 'ify', 'ize', 'ise', 'ward', 'wards', 'wise']
                verb_suffixes = ['s', 'es', 'ed', 'ing', 'en', 'ize', 'ise', 'ify', 'ate', 'ise', 'ize', 'en', 'ify', 'ize', 'ise']
                
                # Check for suffixes
                for suf in suffixes:
                    if word.endswith(suf):
                        root = word[:-len(suf)]
                        suffix = suf
                        break

                # Check for prefixes
                for pre in prefixes:
                    if word.startswith(pre):
                        root = root[len(pre):]
                        prefix = pre
                        break

                # Example infix handling (not common in English, but for demonstration)
                if 'infix' in word:
                    parts = word.split('infix')
                    if len(parts) == 2:
                        infixes.append('infix')
                        root = parts[0] + parts[1]
                
                for dative_suf in dative_suffixes:
                    if word.endswith(dative_suf):
                        case = "dative"
                        break
                
                for accusative_suf in accusative_suffixes:
                    if word.endswith(accusative_suf):
                        case = "accusative" 
                        break
                    
                for genitive_suf in genitive_suffixes:
                    if word.endswith(genitive_suf):
                        case = "genitive"
                        break
                
                for reflexive_suf in reflexive_suffixes:
                    if word.endswith(reflexive_suf):
                        case = "reflexive"
                        break
                    
                for possessive_suf in possessive_suffixes:
                    if word.endswith(possessive_suf):
                        case = "possessive"
                        break
                        
                for plural_suf in plural_suffixes:
                    if word.endswith(plural_suf):
                        case = "plural"
                        break
                    
                for comparative_suf in comparative_suffixes:
                    if word.endswith(comparative_suf):
                        case = "comparative"
                        break
                
                for superlative_suf in superlative_suffixes:
                    if word.endswith(superlative_suf):
                        case = "superlative"
                        break
                    
                for adverbial_suf in adverbial_suffixes:
                    if word.endswith(adverbial_suf):
                        case = "adverbial"
                        break
                    
                for nominal_suf in nominal_suffixes:
                    if word.endswith(nominal_suf):
                        case = "nominal"
                        break
                    
                for verb_suf in verb_suffixes:
                    if word.endswith(verb_suf):
                        case = "verb"
                        break
                
                # Lemmatize the root word
                lemma = nltk.WordNetLemmatizer().lemmatize(root, pos=get_wordnet_pos(pos))
                if lemma != root:
                    root = f"{root} ({lemma})"
                morphemes.append((root, prefix, infixes, suffix, case))
            
            # Prepare the response
            response = "Morphological Analysis:\n"
            for root, prefix, infixes, suffix, case in morphemes:
                response += f"Root: {root}\n"
                response += f"Prefix: {prefix if prefix else 'None'}\n"
                response += f"Infixes: {', '.join(infixes) if infixes else 'None'}\n"
                response += f"Suffix: {suffix if suffix else 'None'}\n"
                response += f"Case: {case}\n"
                response += "-------------------------\n"
            
            await message.channel.send(response)
        
        except Exception as e:
            await message.channel.send(f'Sorry! An error occurred: {e}')
            
        

    async def handle_help(self,message):
        await message.channel.send("Type '$ipa [word or sentence]' for a word/sentence to translate.\n\nType '$translate [from-lang] [to-lang] [word or sentence]' to translate between any two available languages.\n\nThese languages are currently available: Arabic (ar), Chinese (zh), English (en), French (fr), German (de), Hindi (hi), Italian (it), Japanese (ja), Polish (pl), Portuguese (pt), Turkish (tr), Russian (ru), and Spanish (es).\n\nPlease specify the two-letter code of any language used in a translation command.\n\nType '$syllabify [word or sentence]' to get a complete syllabification analysis of any word or sentence. \n\n Type '$tree [sentence]' to get a syntax tree of a sentence. \n\n Type '$logic [sentence]' to get a logical representation of a sentence. \n\n Type '$morphology [word or sentence]' to get a morphological analysis of a word or sentence.")    

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = MyDiscord(intents=intents)
client.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)