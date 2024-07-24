import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import aiohttp, asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from database import countries_collection
class Scraper:
    """
    A class to scrape and process country data from a specified URL and store it in MongoDB.
    """
    def __init__(self, url):
        """
        Initializes the Scraper with the base URL.
        """
        self.url = url
        self.response = []
        self.keys = []
        self.metadata = []

    def get_keys(self):
        """
        Retrieves the keys for data fields.
        """
        print('****get_keys')
        country_details = requests.get(f'{self.url}/country/afghanistan')
        soup = BeautifulSoup(country_details.text, 'html.parser')
        info = soup.find_all(class_='indicator-item__headline-mobile')
        for key in info:
            key_text = key.find('a').text.strip().lower() if key.find('a') else key.text.strip()
            part = key_text.split(',')[0].split('(')[0].strip()
            part = part.replace(' ', '_')
            self.keys.append(part)
        return self.keys
    
    async def fetch_page(self, session, url):
        """
        Asynchronously fetches a page and parses it using BeautifulSoup
        """
        try:
            async with session.get(url) as response:
                response_text = await response.text()
                return BeautifulSoup(response_text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
        

    async def fetch_country_details(self, session, country_name, country_url):
        """
        Fetches details of a specific country and returns the data.
        """
        country_soup = await self.fetch_page(session, f'{self.url}{country_url}')

        if not country_soup:
            return None

        values = country_soup.find_all(name='div', class_='indicator-item__col indicator-item__col--middle')
        country_data = {'country_name': country_name}
        for i in range(len(values)):
            key = self.keys[i]
            data = values[i]
            is_empty = data.find("p", class_="indicator-item__data-info-empty")
            if is_empty:
                country_data[key] = None
            else:
                inner_wrapper = data.find("div", class_="indicator-item__data-inner-col-wrapper")
                if inner_wrapper:
                    value = inner_wrapper.find("div", class_="indicator-item__data-info").find("span").text
                    year = inner_wrapper.find("p", class_="indicator-item__data-info-year").text.strip().replace('(', '').replace(')', '')
                    country_data[key] = {
                        'value': value,
                        'year': year
                    }
        return country_data
        
    
    async def get_values(self):
        """
        Fetches values for all countries and stores them in response.
        """
        print('****get_values')
        async with aiohttp.ClientSession() as session:
            soup = await self.fetch_page(session, f'{self.url}/country')
            if not soup:
                return

            sections = soup.find_all('section', class_='nav-item')
            countries = [country for section in sections for country in section.find_all('li')]

            tasks = []
            for country in countries:
                country_name = country.text.strip()
                country_url = country.find('a')['href']
                tasks.append(self.fetch_country_details(session, country_name, country_url))

            country_data = await asyncio.gather(*tasks)
            for data in country_data:
                if country_data:
                    self.response.append(data)

    async def get_metadata(self, header_name):
        """
        Fetches metadata for a specified header and appends it to metadata list.
        """
        print('*****fetching metadata')
        async with aiohttp.ClientSession() as session:
            soup = await self.fetch_page(session, f'{self.url}/country')
            if not soup:
                return

            header = soup.find('h3', string=header_name)
            if header:
                metadata_list = header.find_parent('li').find('ol')
                results = metadata_list.find_all('li', class_='overview-list-item')
                
                tasks = []
                for result in results:
                    name = result.find('a').text
                    url = result.find('a')['href']
                    tasks.append(self.fetch_country_metadata(session, name, url))

                metadata_results = await asyncio.gather(*tasks)
                response_dict = {name: countries for name, countries in metadata_results if countries}

                self.metadata.append({header_name.lower().replace(" ", "_"): response_dict})

    async def fetch_country_metadata(self, session, name, url):
        """
        Fetches country-specific metadata and returns a list of country names.
        """
        country_soup = await self.fetch_page(session, f'{self.url}{url}')
        if not country_soup:
            return name, []

        article = country_soup.find('article', class_='details card')
        if article:
            countries = article.find_all('li', class_='label')
            country_names = [country.text for country in countries]
            return name, country_names
        return name, []

    async def append_all_data(self):
        """
        Fetches metadata and appends relevant data to the response.
        """
        print('****append_all_data')
        metadata_fields = ['Region', 'Income levels']

        tasks = [self.get_metadata(header_name=field) for field in metadata_fields]
        await asyncio.gather(*tasks)

        for country_obj in self.response:
            country_name = country_obj['country_name']
            for meta in self.metadata:
                for key, value in meta.items():
                    for k, v in value.items():
                        if country_name in v:
                            country_obj[key] = k
                            break
    def get_response(self):
        """
        Returns the scraped response data.
        """
        return self.response
    
s=Scraper('https://data.worldbank.org')
s.get_keys()
async def main():
    """
    Main function to run the scraping and data storage process.
    """
    await s.get_values()
    await s.append_all_data()
    result = await countries_collection.insert_many(s.get_response())

if __name__ == '__main__':
    asyncio.run(main())