import aiohttp


class Currency:
    """
    Получить курс обмена валюты.

    """

    def __init__(self, api_key):
        self.headers = {'apikey': api_key}
        self.session = aiohttp.ClientSession()

    async def get_exchange_rate(self, amount, from_cur, to_cur):
        url = f'https://api.apilayer.com/exchangerates_data/convert?to={to_cur}&from={from_cur}&amount={amount}'
        async with self.session.get(url, headers=self.headers) as response:
            data = await response.json()
            if response.status == 200:
                rate = data['info']['rate']
                result = data['result']
                return f'При переводе из {from_cur} в {to_cur} по курсу {rate} получится: {result} {to_cur}'
            else:
                return f'Не удалось получить курс. Ошибка: {data["error"]["message"]}'

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()
