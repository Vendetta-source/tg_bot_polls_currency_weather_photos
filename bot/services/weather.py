import aiohttp


class Weather:
    """
    Получить текущую погоду в заданном городе с помощью API погоды.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = aiohttp.ClientSession()

    async def get_coordinates(self, city):
        location_url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={self.api_key}'
        async with self.session.get(location_url) as response:
            data = await response.json()
            if response.status == 200:
                lat = data[0]['lat']
                lon = data[0]['lon']
                return lat, lon
            else:
                return f'Не удалось получить координаты в городе {city}. ' \
                       f'Ошибка: {data["message"]}'

    async def get_weather(self, city):
        lat, lon = await self.get_coordinates(city)
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric'
        async with self.session.get(url) as response:
            data = await response.json()
            if response.status == 200:
                weather = data['weather'][0]['description']
                temp = data['main']['temp']
                return f'Погода в городе {city}: {weather}, температура: {temp}°C'
            else:
                return f'Не удалось получить погоду в городе {city}. Ошибка: {data["message"]}'

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

