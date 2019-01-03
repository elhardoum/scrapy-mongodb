# -*- coding: utf-8 -*-
import scrapy

MONGO_CONNECTION_URI = 'mongodb://app:27017'
DATABASE_NAME = 'infocif'
MAIN_COLLECTION = 'data'
# IMAGES_COLLECTION = 'images'

class Spidey(scrapy.Spider):
    name = "quotes"
    start_urls = []
    company = None
    company_id = None
    data = {}

    def __init__(self, **kwargs):
        if not 'company' in kwargs or not kwargs['company']:
            raise Exception("You must supply a company slug(id) via -a argument (e.g -a company='leonardo-azpiri-sa')")
        else:
            company = kwargs['company']
            self.start_urls = [
                'http://www.infocif.es/ficha-empresa/%s' % company,
                'http://www.infocif.es/telefono-direccion/espana/%s' % company,
                # f'http://www.infocif.es/cargos-administrador/{company}',
            ]

    def parse(self, response):
        request_url = response.request._get_url()
        index = self.start_urls.index( request_url ) if request_url in self.start_urls else -1
        data = {}
        company_id = response.xpath("//div[@id='page']//div[contains(concat(' ', normalize-space(@class), ' '), ' casocabecera ')]/img/@alt").extract_first()

        from re import search, sub

        if company_id:
            company_id = company_id.strip()
            matches = search( '^[a-zA-Z0-9]+', company_id )

            try: company_id = matches.group(0).strip()
            except Exception: company_id = None

        if 'http://www.infocif.es/general/includes/ajax_listado_mas_cargos.asp' == request_url:
            selectors = [
                "//td[contains(concat(' ', normalize-space(@class), ' '), 'etEs')]/preceding-sibling::*[1]/text()[3]",
                "//td[contains(concat(' ', normalize-space(@class), ' '), 'etEs')]",
                "//td[contains(concat(' ', normalize-space(@class), ' '), 'etEs')]/following-sibling::*[1]/text()",
                "//td[contains(concat(' ', normalize-space(@class), ' '), 'etEs')]/following-sibling::*[2]/text()",
                "//td[contains(concat(' ', normalize-space(@class), ' '), 'etEs')]/following-sibling::*[3]/text()",
            ]
            payload = [[],[],[],[],[]]

            _idx=-1
            for sel in selectors:
                _idx += 1
                for x in response.xpath( sel ).extract():
                    text = x.strip()
                    if 1 == _idx: text = sub( '<[^>]+>', '', text )
                    payload[ _idx ].append( text )

            data = []
            for x in range( 0, len(payload[0]) ):
                data.append({
                    'fn': payload[0][x],
                    's': payload[1][x],
                    'p': payload[2][x],
                    'd': payload[3][x],
                    'v_num': payload[4][x],
                    })
            index = 2

        elif 0 == index:
            data = {
                'd': response.xpath("//div[@id='page']//div[contains(concat(' ', normalize-space(@class), ' '), ' casocabecera ')]//h1/text()").extract_first().strip(),
                'logo': {
                    'u': response.xpath("//div[@id='page']//div[contains(concat(' ', normalize-space(@class), ' '), ' casocabecera ')]/img/@src").extract_first().strip(),
                },
                'r_n': response.xpath("//div[@id='page']//div[contains(concat(' ', normalize-space(@class), ' '), ' casocabecera ')]//div[contains(concat(' ', normalize-space(@class), ' '), ' fs18')]/span/text()").extract_first().strip(),
                'tr': 'fa-arrow-down' if 'fa-arrow-down' in response.xpath("//div[@id='page']//div[contains(concat(' ', normalize-space(@class), ' '), ' casocabecera ')]//div[contains(concat(' ', normalize-space(@class), ' '), ' fs18')]/span[2]/i/@class").extract_first().strip() else 'fa-arrow-up',
                'cif': response.xpath("//div[@id='collapsecargos']//*[contains(normalize-space(text()),'CIF')]/following-sibling::*[1]/text()").extract_first().strip(),
                'c_d': response.xpath(u"//div[@id='collapsecargos']//*[contains(normalize-space(text()),'Antigüedad')]/following-sibling::*[1]/text()").extract_first().strip(),
                'ph': response.xpath(u"//div[@id='collapsecargos']//*[contains(normalize-space(text()),'Teléfono')]/following-sibling::*[1]/text()").extract_first().strip(),
                'web': response.xpath("//div[@id='collapsecargos']//*[contains(normalize-space(text()),'Web')]/following-sibling::*[1]/a/text()").extract_first().strip(),
                's': response.xpath("//div[@id='collapsecargos']//*[contains(normalize-space(text()),'Sector')]/following-sibling::*[1]/text()").extract_first().strip(),
                'emp_n': response.xpath(u"//div[@id='collapsecargos']//*[contains(normalize-space(text()),'Nº de empleados')]/following-sibling::*[1]/text()").extract_first().strip(),
                'pos': response.xpath("//div[@id='collapsecargos']//*[contains(normalize-space(text()),'Cargos directivos')]/text()").extract_first().strip().replace('Cargos directivos - ', ''),
                'fn': response.xpath("//div[@id='collapsecargos']//*[contains(normalize-space(text()),'Cargos directivos - Presidente')]/following-sibling::*[1]/text()").extract_first().strip(),
                'mat': response.xpath("//div[@id='collapsecargos']//*[contains(normalize-space(text()),'Matriz')]/following-sibling::*[1]/text()").extract_first().strip(),
            }

            data['c_d'] = sub( r'^[^\(]+', '', data['c_d'] ).replace('(','').replace(')','')

        elif 1 == index:
            data = {
                'provinces': [
                    { 'p1': response.xpath("//div[@id='page']//div[contains(normalize-space(text()),'Seleccionar provincia:')]/following-sibling::*//div[contains(concat(' ', normalize-space(@class), ' '), ' mb10 ')][1]/a/text()").extract_first().strip() },
                    { 'p2': response.xpath("//div[@id='page']//div[contains(normalize-space(text()),'Seleccionar provincia:')]/following-sibling::*//div[contains(concat(' ', normalize-space(@class), ' '), ' mb10 ')][2]/a/text()").extract_first().strip() }
                ]
            }

        if not self.company_id and company_id:
            self.company_id = company_id
            post = {'nif':self.company_id, 'limiteactual':'0', 'estadoactual':'1', 'mostrar':'cargos'}
            yield scrapy.http.FormRequest('http://www.infocif.es/general/includes/ajax_listado_mas_cargos.asp', callback=self.parse, formdata=post)

        yield data
            
        self.data[index] = data

        if 3 == len( self.data ):
            self.persist_data()

    def persist_data(self):
        from pymongo import MongoClient

        client = MongoClient(MONGO_CONNECTION_URI)
        db = client[ DATABASE_NAME ]
        data = db[MAIN_COLLECTION]
        images = db[IMAGES_COLLECTION]

        # store image
        # result = images.insert_one( { 'base64': self.imagetobase64( self.data[0]['logo']['u'] ) } )
        # if result and hasattr(result, 'inserted_id') and result.inserted_id:
        #     self.data[0]['logo']['u_id'] = result.inserted_id

        self.data[0]['logo']['base64'] = self.imagetobase64( self.data[0]['logo']['u'] )

        result = data.insert_one({
            'information': self.data[0],
            'admins': self.data[2],
            'offices': self.data[1],
        })

        if result and hasattr(result, 'inserted_id') and result.inserted_id:
            print ( "Successful insert!" )
        else:
            print( "Failed insert!", self.data ) 

    def imagetobase64(self, url):
        import urllib2
        import base64
        contents = urllib2.urlopen(url).read()
        return base64.b64encode(contents)
