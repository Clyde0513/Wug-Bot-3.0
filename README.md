# Wug Bot 3.0

Wug Bot 3.0 is a Discord bot designed to perform various linguistic tasks, including morphological analysis and logical representation of sentences. This bot leverages the Natural Language Toolkit (NLTK) and WordNet for its linguistic capabilities.

## Features

- **Morphological Analysis**: Analyzes the morphology of words in a given sentence, identifying roots, prefixes, suffixes, and grammatical cases.
- **Logical Representation**: Converts sentences into logical representations.

## Requirements

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

## Usage

1. **Run the bot**:
    ```sh
    python wug.py
    ```

2. **Commands**:
    - **Morphological Analysis**: Use the command `$morphology <sentence>` to analyze the morphology of a sentence.
    - **Logical Representation**: Use the command `$logic <sentence>` to get the logical representation of a sentence.

## Example

### Morphological Analysis

```
$morphology The quick brown fox jumps over the lazy dog.

Response:
Morphological Analysis:
Root: The
Prefix: None
Infixes: None
Suffix: None
Case: nominative
-------------------------
Root: quick
Prefix: None
Infixes: None
Suffix: None
Case: nominative
-------------------------
Root: brown
Prefix: None
Infixes: None
Suffix: None
Case: nominative
-------------------------
Root: fox
Prefix: None
Infixes: None
Suffix: None
Case: nominative
-------------------------
Root: jump
Prefix: None
Infixes: None
Suffix: s
Case: verb
-------------------------
Root: 
Prefix: over
Infixes: None
Suffix: er
Case: comparative
-------------------------
Root: the
Prefix: None
Infixes: None
Suffix: None
Case: nominative
-------------------------
Root: laz
Prefix: None
Infixes: None
Suffix: y
Case: nominal
-------------------------
Root: dog
Prefix: None
Infixes: None
Suffix: None
Case: nominative
-------------------------
Root: .
Prefix: None
Infixes: None
Suffix: None
Case: nominative
-------------------------
```

### Logic Analysis 
```
$logic The quick brown fox jumps over the lazy dog.
Logic Representation: D(The) ∧ A(quick) ∧ N(brown) ∧ N(fox) ∧ VBZ(jumps) ∧ P(over) ∧ D(the) ∧ A(lazy) ∧ N(dog) ∧ .(.)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
# Wug-Bot-3.0
A Linguistic bot that translates any English word or sentences into into syntax, IPA, logic, morphological representations, and translate from one language to another (13 languages
