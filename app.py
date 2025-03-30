from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import requests
import re
from webScraper import fetch_slang_details, get_gif_url

app = Flask(__name__)

def split_text(text, max_length=1600):
    """Splits text while preserving word boundaries and proper formatting."""
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split at punctuation + space
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= max_length:  # +2 for spacing
            current_chunk += f" {sentence}" if current_chunk else sentence
        else:
            chunks.append(current_chunk.strip())  # Add completed chunk
            current_chunk = sentence

    if current_chunk:  # Add last chunk
        chunks.append(current_chunk.strip())

    return chunks

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    response = MessagingResponse()

    if incoming_msg == "start" or incoming_msg=="hello" or incoming_msg=="hi":
        manual_text = (
            "👋 Welcome to the *GenZ Slang Bot*! 🎉\n\n"
            "🔍 To find a slang meaning, just type the slang word and send it.\n"
            "📌 Example: Send *rizz* to get its definition.\n"
            "🔄 Soon, you'll also get synonyms, examples, and even memes!\n\n"
            "Try sending a slang word now! 🚀"
        )
        chunks = split_text(manual_text)
        for chunk in chunks:
            msg = response.message()
            msg.body(chunk)

        msg = response.message()
        msg.media('https://res.cloudinary.com/dv6qjtcnq/image/upload/v1743234015/logo_qwdfir.jpg')

    elif incoming_msg.startswith("gif "):
        slang = incoming_msg.replace("gif ", "").strip()
        gif_url = get_gif_url(slang)

        if gif_url:
            msg = response.message()
            msg.media(gif_url)
        else:
            msg = response.message()
            msg.body(f"❌ Sorry, couldn't find a GIF for *{slang}*. Try another word!")

    else:
        slang_details, gif_url = fetch_slang_details(incoming_msg)
        if slang_details:
            chunks = split_text(slang_details)
            for chunk in chunks:
                msg = response.message()
                msg.body(chunk)
            if gif_url:
                msg = response.message()
                msg.media(gif_url)
        else:
            msg = response.message()
            msg.body("❌ Sorry, I couldn't find that slang.\n🔎 Try another word or check: https://www.dictionary.com/e/slang/")

    return Response(str(response), mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
