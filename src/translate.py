# from googletrans import Translator
from deep_translator import GoogleTranslator
import json
from pydantic import BaseModel, Field

# translator = Translator()

# pydantic BaseModel class required for json response from together AI models
class ISO_code(BaseModel):
    text_language: str = Field(description="The language of the user text")
    ISO_code: str = Field(description="ISO 639-1 code of the text_language")

# google translator code
def translate_text(text, source='en', target='en'):
    # translation = translator.translate(text, src=text_iso, dest='en').text
    translation = GoogleTranslator(source=source, target=target).translate(text)
    # return json.dumps({'original_text':text, 'text_language':text_iso, 'english_text':translation})
    return translation
