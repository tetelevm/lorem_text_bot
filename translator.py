from abc import ABC, abstractmethod
import requests
from requests.exceptions import ConnectTimeout

from envs import envs


__all__ = [
    "TranslationRequestException",
    "TranslationTimeoutException",
    "translators",
]


YANDEX_TOKEN = envs["YANDEX_TOKEN"]
LINGVANEX_TOKEN = envs["LINGVANEX_TOKEN"]

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
    Usage is done through object call.
    """

    url: str
    headers: dict

    def __call__(self, text: str, from_lang: str = "", to_lang: str = "ru") -> str:
        """
        Makes a request to the translation server and fetches the text
        from the response.
        """

        response = self.send_request(text, from_lang, to_lang)
        translated_text = self.parse_response(response.json())
        return translated_text

    @staticmethod
    def execute_post(*args, **kwargs) -> requests.Response:
        """
        Makes a request, checks for success (if not, it throws an
        exception) and returns the response.
        """

        try:
            response = requests.post(*args, **kwargs)
        except ConnectTimeout:
            msg = f"The translator server is taking too long to respond ({TIMEOUT} seconds)"
            raise TranslationTimeoutException(msg)

        if response.status_code != 200:  # not `.ok`, just 200
            msg = f"Error, response status {response.status_code}"
            raise TranslationRequestException(msg)

        return response

    @abstractmethod
    def send_request(self, text: str, from_lang: str, to_lang: str) -> requests.Response:
        """
        The method for sending the request.
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

    def send_request(self, text: str, from_lang: str, to_lang: str) -> requests.Response:
        body = {
            "targetLanguageCode": to_lang,
            "texts": [text],
        }
        if from_lang:
            body["sourceLanguageCode"] = from_lang
        return self.execute_post(self.url, json=body, headers=self.headers, timeout=TIMEOUT)

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

    def send_request(self, text: str, from_lang: str, to_lang: str) -> requests.Response:
        body = {
            "to": to_lang,
            "text": text,
        }
        if from_lang:
            body["from"] = from_lang
        return self.execute_post(self.url, data=body, headers=self.headers, timeout=TIMEOUT)

    def parse_response(self, response: dict) -> str:
        #  {'err': None, 'result': "Hi, I'm a translation text."}
        return response["result"]


class WatsonTranslator(BaseTranslator):
    """
    Translator via IBM Watson. Oddly enough, it works freely without
    authorization.

    https://www.ibm.com/demos/live/watson-language-translator/self-service/home
    """

    url = 'https://www.ibm.com/demos/live/watson-language-translator/api/translate/text'
    url_detect = 'https://www.ibm.com/demos/live/watson-language-translator/api/translate/detect'
    headers = {}

    def detect_language(self, text: str) -> str:
        """
        IBM Watson does not auto-detect the language when translating,
        it is done by a special request.
        """

        body = {"text": text}
        response = self.execute_post(self.url_detect, json=body, headers=self.headers, timeout=TIMEOUT)

        # {"status": "success", "message": "ok", "payload": {
        #     "languages": [
        #         {"language": {"language": "ru", "name": "Russian"}, "confidence": 0.99962},
        #         {"language": {"language": "sr", "name": "Serbian"}, "confidence": 0.00034},
        #     ]
        # }}
        response_data = response.json()
        return response_data["payload"]["languages"][0]["language"]["language"]

    def send_request(self, text: str, from_lang: str, to_lang: str) -> requests.Response:
        if not from_lang:
            from_lang = self.detect_language(text)
        body = {
            "source": from_lang,
            "target": to_lang,
            "text": text,
        }
        return self.execute_post(self.url, json=body, headers=self.headers, timeout=TIMEOUT)

    def parse_response(self, response: dict) -> str:
        # {'status': 'success', 'message': 'ok', 'payload': {
        #     'translations': [{'translation': "Hi, I'm the text to translate."}],
        #     'word_count': 8, 'character_count': 29}}
        return response["payload"]["translations"][0]["translation"]


translators = {
    "wat": WatsonTranslator(),
    "yan": YandexTranslator(),
    "lin": LingvanexTranstator(),
}
