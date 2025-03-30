from twilio.twiml.messaging_response import MessagingResponse
import requests
import re
from bs4 import BeautifulSoup

GIPHY_API_KEY = "Glc0XmulmxPgCC7eKqqp8138hfXvIQut"
def get_gif_url(search_term):
    """Fetch an MP4 URL from Giphy to avoid Twilio's GIF rejection issues."""
    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={search_term}&limit=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]["images"]["original_mp4"]["mp4"]  # ✅ Using MP4 format
    return None

def beautify_text(text):
    """Cleans up and formats text for better readability."""
    text = re.sub(r"([,.!?])([^\s])", r"\1 \2", text)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"(\w)/(\w)", r"\1 / \2", text)
    text = text.replace('"', "“").replace('"', "”")
    return text

def fetch_slang_details(slang):
    """Fetches details about a slang word from Merriam-Webster, including definition, examples, pronunciation, usage, and origin."""
    base_url = "https://www.merriam-webster.com/slang/"
    search_url = f"{base_url}{slang.replace(' ', '-')}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        google_search_url = f"https://www.google.com/search?q={slang}+meaning+slang"
        return (
            (f"❌ *Oops! I couldn't find '{slang}' in my database.*\n\n"
            f"🔎 But you can check out these online slang dictionaries:\n"
            f"📘 Dictionary : https://www.dictionary.com/e/{slang}/\n"
            f"📗 Urban Dictionary: https://www.urbandictionary.com/{slang}\n\n"
            f"Or try searching Google directly: \n({google_search_url})"),None
        )
        
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1", class_="title-lg")
    title = title_tag.text.strip() if title_tag else slang.capitalize()

    pronunciation_tag = soup.find("div", class_="word-attribs")
    if pronunciation_tag:
        pronunciation_text = pronunciation_tag.text.strip().split("|")
        pronunciation = pronunciation_text[1].strip() if len(pronunciation_text) > 1 else pronunciation_text[0].strip()
    else:
        pronunciation = "No pronunciation available."

    pos_tag = pronunciation_tag.find("em") if pronunciation_tag else None
    part_of_speech = pos_tag.text.strip() if pos_tag else "Unknown"

    meaning_tag = soup.find("div", class_="word-meaning")
    meaning = meaning_tag.text.strip() if meaning_tag else "No definition found."

    main_div = soup.find("div", class_="article-body-content-padding")
    if not main_div:
        return "Error: Could not find the main content.", None

    definition_tag = main_div.find("h2")
    definition = definition_tag.find_next("p").get_text(strip=True) if definition_tag else "Definition not found."

    example_tag = definition_tag.find_next("h2") if definition_tag else None
    blockquote_tag = example_tag.find_next("blockquote") if example_tag else None
    examples = []
    if blockquote_tag:
        for i,p in enumerate(blockquote_tag.find_all("p")):
            if i>=2:
                break
            for span in p.find_all("span"):  # Remove Twitter handles
                span.extract()
            cleaned_text = p.get_text(separator=" ", strip=True)
            examples.append(cleaned_text)
    examples_text = "\n".join(f"- {ex}" for ex in examples) if examples else "Examples not found."

    origin_tag = example_tag.find_next("h2") if example_tag else None
    origin = origin_tag.find_next("p").get_text(strip=True) if origin_tag else "Origin not found."

    usage_tag = origin_tag.find_next("h2") if origin_tag else None
    usage = usage_tag.find_next("p").get_text(strip=True) if usage_tag else "Usage not found."

    gif_url = get_gif_url(slang)
    
    image_url = None
    image_div = soup.find("div", class_="wap-categories-img-container")
    if image_div:
        image_element = image_div.find("div", class_="lazyload-container")
        if image_element:
            data_background_image_set = image_element.get("data-background-image-set", "")
            if data_background_image_set:
                start_idx = data_background_image_set.find("url(") + 4
                end_idx = data_background_image_set.find(")", start_idx)
                if start_idx != -1 and end_idx != -1:
                    image_url = data_background_image_set[start_idx:end_idx].strip('"')

    response_text = (
        f"🔥 *Slang*: {title}\n"
        f"🗣️ *Pronunciation*: {pronunciation}\n"
        f"📖 *Meaning*:\n{meaning}\n"
        f"📌 *Part of Speech*: \n{part_of_speech}\n"
        f"📖 *Definition*:\n{definition}\n\n"
        f"📜 *Examples*:\n{examples_text}\n\n\n"
        f"🌍 *Origin*:\n{origin}\n\n\n"
        f"📝 *Usage*:\n{usage}\n"
    )
    response_text = beautify_text(response_text)

    return response_text,gif_url


# https://api.giphy.com/v1/gifs/search?api_key={Glc0XmulmxPgCC7eKqqp8138hfXvIQut}&q={pikachu}&limit=1