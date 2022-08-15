from abc import ABC, abstractmethod
from typing import Dict, List, Final

import aiohttp
from asyncio.exceptions import TimeoutError

from envs import envs


__all__ = [
    "TranslationRequestException",
    "TranslationTimeoutException",
    "shared_languages",
    "text_translator",
]


shared_languages: Final[tuple] = ("en", "ru", "el", "de", "ja", "fi")

YANDEX_TOKEN: Final[str] = ""  # envs["YANDEX_TOKEN"]  # the translator is disabled, so no token
LINGVANEX_TOKEN: Final[str] = envs["LINGVANEX_TOKEN"]

TIMEOUT = 10


class TranslationRequestException(Exception):
    """
    Exception for an unsuccessful request.
    """
    pass


class TranslationTimeoutException(Exception):
    """
    Server does not respond for more than `TIMEOUT` seconds.
    """
    pass


class BaseTranslator(ABC):
    """
    A basic class for all translators.
    The descendants store the url, the headers and contain methods for
    requesting and parsing the response.
    Usage is done through object call. Works asynchronously.
    """

    url: str
    headers: dict

    async def __call__(self, text: str, from_lang: str = "", to_lang: str = "ru") -> str:
        """
        Makes a request to the translation server and fetches the text
        from the response.
        """

        response_json = await self.send_request(text, from_lang, to_lang)
        translated_text = self.parse_response(response_json)
        return translated_text

    @staticmethod
    async def execute_post(*args, **kwargs) -> dict:
        """
        Makes a request, checks for success (if not, it throws an
        exception) and returns the response.
        """

        session = aiohttp.ClientSession()
        try:
            async with session.post(*args, **kwargs) as response:
                if response.status != 200:  # not `.ok`, just 200
                    msg = f"Error, response status {response.status}"
                    raise TranslationRequestException(msg)
                return await response.json()
        except TimeoutError:
            msg = f"The translator server is taking too long to respond ({TIMEOUT} seconds)"
            raise TranslationTimeoutException(msg)
        finally:
            await session.close()

    @abstractmethod
    async def send_request(self, text: str, from_lang: str, to_lang: str) -> dict:
        """
        The method for sending the request. Must call the `.execute_post`
        method.
        """
        pass

    @abstractmethod
    def parse_response(self, response: dict) -> str:
        """
        A method for parsing the json structure of a response.
        """
        pass


class YandexTranslator(BaseTranslator):
    """
    Translator via Yandex.Translator. Requires a token for authorization.

    https://translate.yandex.ru/
    """

    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {"Authorization": f"Api-Key {YANDEX_TOKEN}"}

    async def send_request(self, text: str, from_lang: str, to_lang: str) -> dict:
        body = {
            "targetLanguageCode": to_lang,
            "texts": [text],
        }
        if from_lang:
            body["sourceLanguageCode"] = from_lang
        return await self.execute_post(self.url, json=body, headers=self.headers, timeout=TIMEOUT)

    def parse_response(self, response: dict) -> str:
        # {'translations': [{'text': "Hi, I'm a text for translation."}]}
        return response["translations"][0]["text"]


class LingvanexTranstator(BaseTranslator):
    """
    Translator via LingvaNex.
    The token and api are provided by another developer, who asked to
    mention it, but did not provide a link to the Github.

    https://lingvanex.com/demo/
    """

    url = "https://api-b2b.backenster.com/b1/api/v3/translate"
    headers = {"authorization": f"Bearer {LINGVANEX_TOKEN}"}

    async def send_request(self, text: str, from_lang: str, to_lang: str) -> dict:
        body = {
            "to": to_lang,
            "text": text,
        }
        if from_lang:
            body["from"] = from_lang
        return await self.execute_post(self.url, data=body, headers=self.headers, timeout=TIMEOUT)

    def parse_response(self, response: dict) -> str:
        #  {'err': None, 'result': "Hi, I'm a translation text."}
        return response["result"]


class WatsonTranslator(BaseTranslator):
    """
    Translator via IBM Watson. Oddly enough, it works freely without
    authorization.

    https://www.ibm.com/demos/live/watson-language-translator/self-service/home
    """

    url = "https://www.ibm.com/demos/live/watson-language-translator/api/translate/text"
    url_detect = "https://www.ibm.com/demos/live/watson-language-translator/api/translate/detect"
    headers = {}

    async def detect_language(self, text: str) -> str:
        """
        IBM Watson does not auto-detect the language when translating,
        it is done by a special request.
        """

        response_data = await self.execute_post(
            self.url_detect,
            data={"text": text},
            headers=self.headers,
            timeout=TIMEOUT
        )

        # {"status": "success", "message": "ok", "payload": {
        #     "languages": [
        #         {"language": {"language": "ru", "name": "Russian"}, "confidence": 0.99962},
        #         {"language": {"language": "sr", "name": "Serbian"}, "confidence": 0.00034},
        #     ]
        # }}
        return response_data["payload"]["languages"][0]["language"]["language"]

    async def send_request(self, text: str, from_lang: str, to_lang: str) -> dict:
        if not from_lang:
            from_lang = await self.detect_language(text)
        body = {
            "source": from_lang,
            "target": to_lang,
            "text": text,
        }
        return await self.execute_post(self.url, data=body, headers=self.headers, timeout=TIMEOUT)

    def parse_response(self, response: dict) -> str:
        # {'status': 'success', 'message': 'ok', 'payload': {
        #     'translations': [{'translation': "Hi, I'm the text to translate."}],
        #     'word_count': 8, 'character_count': 29}}
        return response["payload"]["translations"][0]["translation"]


class TextTranslator:
    defaults_translator = "lin"
    default_from = ""
    default_to = "ru"
    translators: Dict[str, BaseTranslator]
    translator_names: List[str]

    def __init__(self):
        self.translators = {
            # "wat": WatsonTranslator(),
            # "yan": YandexTranslator(),
            "lin": LingvanexTranstator(),
        }
        self.translator_names = list(self.translators)

    async def __call__(self, text: str, translator_name: str, from_lang: str, to_lang: str) -> str:
        translator = self.translators[translator_name]
        return await translator(text, from_lang, to_lang)


text_translator = TextTranslator()


if __name__ == "__main__":
    import asyncio

    test_text = "I am a text in English, and I am needed for the test."
    for name in text_translator.translator_names:
        coro = text_translator(
            test_text,
            name,
            text_translator.default_from,
            text_translator.default_to
        )
        translation_result = asyncio.run(coro)
        print(translation_result)
