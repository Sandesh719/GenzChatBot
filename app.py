from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import requests
import re
from webScraper import fetch_slang_details, get_gif_url,beautify_text
import time

app = Flask(__name__)

def split_text(text, max_length=1600):
    """Splits text while preserving word boundaries and proper formatting."""
    sentences = re.split(r'(?<=[.!?])\s+', text)  
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= max_length:  
            current_chunk += f" {sentence}" if current_chunk else sentence
        else:
            chunks.append(current_chunk.strip())  
            current_chunk = sentence

    if current_chunk:  
        chunks.append(current_chunk)
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
            "🎥 Prefix a word with 'gif ' for GIFs\n"
            "Try it now! 😎Try sending a slang word! 🚀"
        )
        msg = response.message()
        msg.media('https://res.cloudinary.com/dv6qjtcnq/image/upload/v1743234015/logo_qwdfir.jpg')
        msg.body(manual_text)

    elif incoming_msg.startswith("gif "):
        slang = incoming_msg.replace("gif ", "").strip()
        gif_url = get_gif_url(slang)

        if gif_url:
            response.message(f"🎬Here's a GIF for *{slang}*")
            msg = response.message()
            msg.media(gif_url)
        else:
            msg = response.message()
            msg.body(f"❌ Sorry, couldn't find a GIF for *{slang}*. Try another word!")

    else:
        slang_data, gif_url = fetch_slang_details(incoming_msg)
        if slang_data:
            pretty_text1 = beautify_text(slang_data['basic_info'])
            pretty_text2 = beautify_text(slang_data['definition_examples'])
            pretty_text3 = beautify_text(slang_data['usage'])
            msg1 = response.message()
            msg1.body(f"(1/4) {slang_data['basic_info']}")
            time.sleep(0.45)
            msg2 = response.message()
            msg2.body(f"(2/4) {slang_data['definition_examples']}")
            time.sleep(0.3)
            msg3 = response.message()
            msg3.body(f"(3/4) {slang_data['usage']}\n\n🎬Here's a GIF for *{incoming_msg}*")
            time.sleep(0.6)
            if gif_url:
                # msg4 = response.message()
                # msg4.body(f"(4/4) 🎬Here's a GIF for *{incoming_msg}*")
                # time.sleep(0.5)  # Then delay before media
                msg5 = response.message()
                msg5.media(gif_url)
        else:
            msg = response.message()
            msg.body("❌ Sorry, I couldn't find that slang.\n🔎 Try another word or check: https://www.dictionary.com/e/slang/")

    return Response(str(response), mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
