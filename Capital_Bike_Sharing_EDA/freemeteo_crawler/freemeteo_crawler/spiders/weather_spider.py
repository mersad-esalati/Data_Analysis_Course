import scrapy

import urllib.parse as urlparse
from urllib.parse import parse_qs
import itertools

class WeatherSpider(scrapy.Spider):
    name='weathers'

    def __init__(self, s_date, e_date, *args, **kwargs):
        super(WeatherSpider, self).__init__(*args, **kwargs)
        self.s_date = s_date
        self.e_date = e_date


    def start_requests(self):
        url = f'https://ir.freemeteo.com/weather/washington/history/daily-history/?gid=4140963&station=19064&date={self.s_date}&country=us-united-states'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        query = urlparse.urlparse(response.url).query
        date = parse_qs(query)['date'][0]

        for row in response.css('.daily-history tbody')[0].css('tr'):
            s = {}

            # extract date
            s['Date'] = date

            items = row.css('td')
            
            # extract time column
            s['Time'] = items[0].css('::text').get()

            # extract temperature
            s['Temperature'] = items[1].css('b::text').get()

            # extract relative temperature
            s['Relative Temperature'] = items[2].css('::text').get()

            # extract wind speed
            if bool(items[3].css('span')):
                s['Wind'] = items[3].css('span::text').get()
            else:
                s['Wind'] = None
            
            # extract humidity
            s['Rel. Humidity'] = items[5].css('::text').get()

            # extract pressure
            s['Pressure'] = items[7].css('::text').get()

            # extract description
            s['Description'] = items[9].css('span.details::text').get()

            self.log(items[9].css('::text').get())

            # yield s

        if str(date) != self.e_date:
            np = response.css('a.next::attr(href)')[0].get()
            yield response.follow(np, self.parse)
