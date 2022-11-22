import requests
import json
from config import keys, payload, headers


# Исключения
class APIException(Exception):
    pass


# Конвертер
class Converter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote == base:
            raise APIException("Валюты должны быть разные")

        try:
            quote_ticker = keys[quote][0]
        except KeyError:
            raise APIException(f"Не удалось обработать валюту <{quote}>")

        try:
            base_ticker = keys[base][0]
        except KeyError:
            raise APIException(f"Не удалось обработать валюту <{base}>")

        try:
            amount_val = float(amount.replace(',', '.'))
        except ValueError:
            raise APIException(f"Не удалось обработать количество валюты <{amount}>")

        url = f"https://api.apilayer.com/exchangerates_data/convert?to={base_ticker}& \
        from={quote_ticker}&amount={amount_val}"
        response = requests.request("GET", url, headers=headers, data=payload)
        result_json = json.loads(response.content)

        return result_json['result']


# Склонение валют
class GetNoun:
    @staticmethod
    def get_noun(num, one, over):
        n = round(num)
        if n % 10 == 1 and n % 100 != 11:
            return one
        return over
