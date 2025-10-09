
# Russian Text Glossary Generator

A Python tool that processes Russian text files and generates interactive glossaries with Wiktionary translations and links.

## Rationale

A great  tool for learning a languge is a word glossary in the beggining of a text. This simple script generates such a glossary for any  given text. 

Moreover, using the text, an interactive html is generated to help the reading process, where the translation is included for each word as a popup, and each word is clickable, with a link to the appropriate wiktionary (english) lemma.  

## Features

- **Automatic Translation Lookup**: Finds English translations for Russian words
- **Interactive HTML Output**: Creates clickable text with Wiktionary links
- **Lemma Recognition**: Handles different word forms by finding dictionary forms

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.9+ installed
3. Install required dependencies:
   ```bash
   pip install requests
4. Install [https://github.com/Badestrand/russian-dictionary](https://github.com/Badestrand/russian-dictionary) files in ./dictionary subdirectory (the files used are verbs.csv,nouns.cvs,adjectives.csv). If /Badestrand/russian-dictionary is installed in diffent path, change Path, in the configuration file

##   Basic Usage
Prerequisites

The following CSV files are used by the Python script:

* ./dictionary/nouns.csv
* ./dictionary/verbs.csv
* ./dictionary/adjectives.csv

### Running the Tool

  ```bash
python3 glossary.py filename.txt
  ```
This will:
* Print a list of translations to the terminal
* Generate an interactive HTML file with the Russian text


### Input Format
Text Files: Your input text file should contain Russian text in UTF-8 encoding:
text
```
Это пример русского текста для обработки.
Программа найдет переводы для каждого слова.
```

### CSV Files
The CSV files shoud contain one line for each word with all its inflected forms.
The files suggeste here, from https://en.openrussian.org as publised in n github directory [Badestrand/russian-dictionary](https://github.com/Badestrand/russian-dictionary)
and have the following structure:
* nouns.csv 
  * Col1     : bare form
  * Col2     : accented form
  * Col3     : english translation
  * Col4     : german translation
  * Col5-9   : flags of the word (gender,etc)
  * Col10-22 : inflected forms of the word
* vervs.csv
  * Col1     : bare form
  * Col2     : accented form
  * Col3     : english translation
  * Col4     : german translation
  * Col5     : partner verb 
  * Col6-18 : inflected forms of the word
* adjectives.csv
  * Col1     : bare form
  * Col2     : accented form
  * Col3     : english translation
  * Col4     : german translation
  * Col5-34  : inflected forms of the adjective

The script reads the csv files and creates a dictionary linking each inflected form with the basic form and its translation. 

Different csv files could be used, by changing the conf.yaml file

#### conf.yaml
 * Path : path of dictionary files, as different entry, not per file

   For each file :
 * Filename : name of the file
 * Category : word category
 * Delimiter : csv file delimiter
 * Word : column of basic word
 * Translation : column of translation
 * Length : columns per line (used for checking invalid lines)
 * Inflected: lis of columns whith inflected forms of the basic word

   


### How it works 

The system processes text through several stages:
1. Data Collection & Validation
    Validates which words have existing Wiktionary entries
    Checks Wiktionary API for valid word entries
    Handles large lists by batching API requests (50 words per batch)

2. Translation Processing
    Maps inflected words to their dictionary forms (lemmas)
    Retrieves translations from dictionary files
    Handles missing entries gracefully

3. HTML Generation

    Creates interactive web pages with clickable words
    Adds Wiktionary links for words with valid entries
    Shows translations as hover tooltips
    Applies clean CSS styling

## Awknowlegments
The russian dictionary suggested here  comes from  [https://en.openrussian.org.](https://en.openrussian.org.) as publised in github directory [Badestrand/russian-dictionary](https://github.com/Badestrand/russian-dictionary) 
The code and a portion of the documentation has been cleaned using a LLM

## Disclaimer
The author has limited knowledge of Russian, and caution is adviced for using this tool

## ToDo 
* Add usage functionality (what and how to output, paths, csv reading)  and package to an app
* Generalize to be language agnostic
* Link to other data sources (eg organic link to wiktionary and not rudimentary)
