# Wug Bot 3.0

Wug Bot 3.0 is a Discord bot designed to perform various linguistic tasks, including morphological analysis and logical representation of sentences. This bot leverages the Natural Language Toolkit (NLTK) and WordNet for its linguistic capabilities, as well as the Argos Translation library to handle translations from one language to another (13 languages)

## 🌟 Key Features

🌳 Syntactic Trees: Visualize sentence structures
🌍 Translation: Support for 13 languages
✂️ Syllabification: Break down words into syllables
🔤 IPA Conversion: Text to International Phonetic Alphabet
📝 Morphological Analysis: Identify word components and transformations
🧮 Logical Representation: Convert sentences to logical forms

## 🚀 Requirements

- Python 3.6+
- Discord.py
- NLTK
- WordNet

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/Wug-Bot-3.0.git
    cd Wug-Bot-3.0
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Download NLTK data**:
    ```python
    import nltk
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')
    nltk.download('treebank')
    nltk.download('universal_tagset')
    ```

5. **Set up your .env file**:
    Create a `.env` file in the root directory of the project and add your Discord bot token and other necessary environment variables:
    ```env
    TOKEN=your_discord_bot_token
    GUILD=your_guild_id
    ALLOWED_CHANNELS=allowed_channel_ids
    OTHER_GUILD_ID=other_guild_id
    OTHER_CHANNEL_ID=other_channel_id
    ```

## 💡 Usage Examples

1. **Run the bot**:
    ```sh
    python wug.py
    ```

2. **Commands**:
    - **Morphological Analysis**: Use the command `$morphology <sentence or word>` to analyze the morphology of a sentence.
    - **Logical Representation**: Use the command `$logic <sentence>` to get the logical representation of a sentence.
    - **Syntactic Trees**: Use the command `$syntactic_tree <sentence>` to generate a syntactic tree for a sentence.
    - **Translation**: Use the command `$translate <from_lang> <to_lang> <text>` to translate text from one language to another.
    - **Syllabification**: Use the command `$syllabify <word or sentences>` to break a word into syllables.
    - **IPA Format**: Use the command `$ipa <sentence or word>` to convert the text to the International Phonetic Alphabet (IPA) format.


## Example

### Morphological Analysis

```
$morphology loved.

Word Analysis: loved
Part of Speech: Verb
Base Form: loved

Morphological Process: 
love → lov (e-dropping)
Root: love
Morphemes Found:
Suffix: '-ed': (inflectional, past tense)
Rule: e-dropping before -ed

$morphology carries

Word Analysis: carries
Part of Speech: Verb
Base Form: carries

Morphological Process: 
carry → carr (y to i)
Root: carry
Morphemes Found:
Suffix: '-s': (inflectional, plural)
Suffix: '-es': (inflectional, plural)
Rule: y to i before -s

$morphology heroes

Word Analysis: heroes
Part of Speech: Noun
Base Form: heroes
Root: hero
Morphemes Found:
Suffix: '-s': (inflectional, plural)
Suffix: '-es': (inflectional, plural)
Rule: o to oe before -s

$morphology watches

Word Analysis: watches
Part of Speech: Noun
Base Form: watches
Root: watch
Morphemes Found:
Suffix: '-s': (inflectional, plural)
Suffix: '-es': (inflectional, plural)
Rule: ch to tch before -s
```

### Logic Analysis 
```
$logic The quick brown fox jumps over the lazy dog.
Logic Representation: D(The) ∧ A(quick) ∧ N(brown) ∧ N(fox) ∧ VBZ(jumps) ∧ P(over) ∧ D(the) ∧ A(lazy) ∧ N(dog) ∧ .(.)
```

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.