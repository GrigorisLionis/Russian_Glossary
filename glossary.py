import random
import os
import unicodedata
import sys
import requests
import json
import time
import yaml
from pathlib import Path

from yaml.loader import SafeLoader
from html import escape
from typing import Dict, List, Union, Optional, Any



def load_conf():

    with open("conf.yml", 'r') as f:
       yaml_data = list(yaml.load_all(f, Loader=SafeLoader))
       return(yaml_data)
    


def load_conf():

    with open("conf.yml", 'r') as f:
       yaml_data = list(yaml.load_all(f, Loader=SafeLoader))
       return(yaml_data)


def load_words(filename,delimiter,length,word_position,translation_position,inflected,cat,words,lemmata):
    with open(filename, 'r',encoding="utf8") as file:
        for line in file:
            elements = line.strip().split(delimiter)
            #print(elements)
            if len(elements) < length or elements[word_position-1]=="bare":
                continue 
            w=elements[word_position-1]
            w=unicodedata.normalize('NFKD',w).capitalize()
            engmeaning=elements[translation_position-1].replace(";",",").split(",") 
            for i in inflected:
                    elements[i-1]=elements[i-1].replace("'","").strip()
                    lemma=elements[i-1]
                    if(lemma==""):
                       continue
                    lemma=unicodedata.normalize('NFKD',lemma).capitalize()   
                    lemmata[lemma]=w
            words[w]={"cat":cat,"translation":engmeaning}
        return words,lemmata    



def load_dictionaries():

    words={}
    lemmata={}
    if not Path("conf.yml").exists():
       print("Error, Configuration file does not exist")
       exit()
    data=load_conf()
    print(data)
    print(len(data))
    path=data[0]["Path"]

    for i in range(1,len(data)):
        filename=data[i]["Filename"]
        delimiter=data[i]["Delimiter"]
        category=data[i]["Category"]
        word_position=data[i]["Word"]
        translation_position=data[i]["Translation"]
        inflected=data[i]["Inflected"]
        length=data[i]["Length"]
    
        if Path(path+filename).exists():
             words,lemmata=load_words(path+filename,delimiter,length,word_position,translation_position,inflected,category,words,lemmata)
  
    return words,lemmata






def download_file_if_missing(filename, download_url):
    """
    Check if a file exists in current directory, download it if missing.
    
    Args:
        filename (str): Name of the file to check/download
        download_url (str): URL to download the file from
    
    Returns:
        bool: True if file exists or was successfully downloaded, False otherwise
    """
    
    # Check if file already exists
    if os.path.exists(filename):
        print(f"File '{filename}' already exists in current directory.")
        return True
    
    print(f"File '{filename}' not found. Downloading from {download_url}...")
    
    try:
        # Send GET request to download the file
        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Write the file in binary mode
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Successfully downloaded '{filename}'")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def check_url(words: List[str], max_retries: int = 3) -> Dict[str, str]:
    """
    Check URLs for a list of words using the Wiktionary API with retry logic.
    """
    if not words:
        return {}
    
    word_list = "|".join(words)
    path = f"https://en.wiktionary.org/w/api.php?action=query&format=json&titles={word_list}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(path, headers={'User-Agent': 'Foo bar'}, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            word_resp = {}
            for page_id in data["query"]["pages"]:
                page_data = data["query"]["pages"][page_id]
                word = page_data["title"]
                normalized_word = unicodedata.normalize('NFKD', word)
                word_resp[normalized_word] = page_id
                
            return word_resp
            
        except (requests.RequestException, KeyError) as e:
            if attempt == max_retries - 1:  # Last attempt
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff


def check_list(words: List[str]) -> Dict[str, str]:
    """
    Check URLs for a list of words, handling large lists by batching.
    
    Args:
        words: List of words to check
        
    Returns:
        Dictionary mapping normalized word titles to page IDs
    """
    if not words:
        return {}
    
    # Wiktionary API has limits on batch size, so we chunk the requests
    batch_size = 50
    
    if len(words) <= batch_size:
        return check_url(words)
    
    # Process in batches and combine results
    first_batch = check_url(words[:batch_size])
    remaining_batch = check_list(words[batch_size:])
    
    return {**first_batch, **remaining_batch}

         


def load_text(filename):
    text=[]
    fulltext=[]
    with open(filename, 'r',encoding="utf8") as f:
         for line in f:
            elements = line.strip().split(" ")
            exp=[]
            for el in elements:
                if len(el)==0:
                   fulltext.append(el)
                   continue
                if el[len(el)-1]==".":
                   exp.append(el[0:(len(el)-1)])
                   exp.append(".")
                else:
                   exp.append(el)
            for el in exp:
                fulltext.append(el)
                if(el=="" or el==" " or el=="." or el==","):
                   continue
                el.strip()
                el=unicodedata.normalize('NFKD',el).capitalize()
                text.append(el)
    return(text,fulltext)



def comp_gloss(text,lemmata):
    glossary=[]

    for l in text:
        if l in lemmata and l not in glossary:
           glossary.append(l)
           
    return(glossary)       
    






def create_html_link(
    word: str, 
    link: str, 
    translation: List[str],
    css_class: Optional[str] = None
) -> str:
    """
    Create an HTML anchor tag for a word with translation as tooltip.
    
    Args:
        word: The word to display as link text
        link: The URL for the hyperlink
        translation: List of translation strings for the title attribute
        css_class: Optional CSS class for the anchor tag
        
    Returns:
        HTML string containing anchor tag or paragraph break for empty word
        
    Examples:
        >>> create_html_link("hello", "https://example.com", ["greeting"])
        '<a href="https://example.com" title="greeting"> hello</a>'
    """
    if not word:
        return "</p><p>"
    
    # Escape user-provided content to prevent XSS
    safe_word = escape(word)
    safe_link = escape(link)
    translation_text = escape("".join(translation))
    
    # Build HTML attributes
    attributes = f'href="{safe_link}" title="{translation_text}"'
    if css_class:
        safe_css_class = escape(css_class)
        attributes += f' class="{safe_css_class}"'
    
    html_link = f'<a {attributes}> {safe_word}</a>'
    
    return html_link
      



def generate_html_text(
    text: List[str],
    lemmata: Dict[str, str],
    words: Dict[str, Dict[str, Any]],
    links: Dict[str, str]
) -> str:
    """
    Generate an HTML document with clickable word links and translations.
    """
    HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Text with Translations</title>
    <style>
        a:link {{ text-decoration: none; color: black; }}
        a:visited {{ text-decoration: none; color: black; }}
        a:hover {{ text-decoration: underline; color: hotpink; }}
        a:active {{ text-decoration: underline; color: black; }}
    </style>
</head>
<body>
    <p>
        {content}
    </p>
</body>
</html>"""
    
    content_parts = []
    
    for word in text:
        translation = []
        link = ""
        
        # Normalize and clean the word
        normalized_word = unicodedata.normalize('NFKD', word).capitalize()
        
        # Remove trailing comma if present
        if len(normalized_word) > 2 and normalized_word.endswith(","):
            normalized_word = normalized_word[:-1]
        
        # Check if word exists in lemmata and has Wiktionary entry
        if normalized_word in lemmata:
            lemma = lemmata[normalized_word]
            lemma_lower = lemma.lower()
            
            # Get translation if available
            translation = words.get(lemma, {}).get("translation", [])
            
            # Create Wiktionary link if valid page exists
            link_id = links.get(lemma_lower, "")
            if link_id.isdigit() and int(link_id) > 0:
                link = f"https://en.wiktionary.org/wiki/{lemma_lower}#Russian"
        
        # Generate HTML link
        html_link = create_html_link(word, link, translation)
        content_parts.append(html_link)
 
    content = "\n        ".join(content_parts)
    return HTML_TEMPLATE.format(content=content)
 
def check_lemmata_links(
    glossary: List[str], 
    lemmata: Dict[str, str]
) -> Dict[str, Any]:
    """
    Check Wiktionary links using list comprehension.
    """
    # Only process words that exist in lemmata
    lemma_list = [
        unicodedata.normalize('NFKD', lemmata[word]).lower()
        for word in glossary
        if word in lemmata
    ]
    
    return check_list(lemma_list) if lemma_list else {}
    
def write_html_simple(content: str, filename: str = "ru.html") -> None:
    """
    Simple HTML file writer with basic error handling.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)  # Using write() instead of print() for files
        print(f"HTML file '{filename}' created successfully")
    except Exception as e:
        print(f"Error: Could not write to '{filename}': {e}")
        raise  # Or handle differently based on your needs

def print_glossary(glossary,lemmata,words) -> None:

    for word in glossary:
       # Safely navigate the nested dictionaries
       lemma = lemmata.get(word)
       if not lemma:
           continue
        
       word_data = words.get(lemma, {})
       translation = word_data.get("translation")
    
       if translation:
          print(f"{lemma}: {translation}")




def main():

    filename=sys.argv[1]
    
    
    """Main function to run the application."""
    try:
       
        words,lemmata = load_dictionaries() 
        text,fulltext=load_text(filename)
        glossary=comp_gloss(text,lemmata)
       

        """
        Output glossary
        """
        print_glossary(glossary,lemmata,words)


        #find links to words
        links=check_lemmata_links(glossary,lemmata)

        """
        Code to write html file
        """ 
        
        html_content=generate_html_text(fulltext,lemmata,words,links)
        write_html_simple(html_content)
        
      
    except FileNotFoundError:
        print(f"Error: File '{CSV_FILE}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
                
