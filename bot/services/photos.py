import aiohttp
import io


class AnimalsPhotos:
    """
    Получить рандомное изображение животного.
    """

    def __init__(self, api_key):
        self.headers = {
            'X-Api-Key': api_key,
            'Accept': 'image/jpg'
        }
        self.session = aiohttp.ClientSession()
        self.url = 'https://api.api-ninjas.com/v1/randomimage?category=wildlife'

    async def get_image(self):
        async with self.session.get(self.url, headers=self.headers) as response:
            if response.status == 200:
                content = await response.read()
                photo_file = io.BytesIO(content)
                return photo_file

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()
