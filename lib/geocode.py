from OSMPythonTools.nominatim import Nominatim
import googlemaps

class GeoCoding:
    GOOGLE_MAPS="GOOGLE_MAPS"
    OSM = "OSM"
    ZERO_RESULTS = "ZERO_RESULTS"

    transformCity = {
        'South Jakarta': 'Kota Jakarta Selatan',
        'North Jakarta': 'Kota Jakarta Utara',
        'West Jakarta': 'Kota Jakarta Barat',
        'East Jakarta': 'Kota Jakarta Timur',
        'Central Jakarta': 'Kota Jakarta Pusat',
    }

    def __init__(self):
        self.nominatim = Nominatim()
        self.nominatimQueryParams = {
            'countrycodes': 'ID',
            'polygon_geojson': '1',
            'addressdetails': '1'
        }
        self.gmaps = googlemaps.Client(key='AIzaSyC5Q7dmBU_Qaw6ahgr21mHOvX44o78Jvx0')


    def nominatimGeocode(self, q):
        temp = self.nominatim.query(q, params=self.nominatimQueryParams).toJSON()
        return None if len(temp) == 0 else temp
    
    def googleGeocode(self, q):
        temp = self.gmaps.geocode(q)
        return None if len(temp) == 0 else temp
    
    def geocodeQuery(self,q):
        res = {
            'type': self.ZERO_RESULTS,
            'data': None
        }
        temp = self.nominatimGeocode(q)
        if temp==None:
            temp = self.googleGeocode(q)
            if temp!=None:
                res['type'] = self.GOOGLE_MAPS
                res['data'] = temp[0]
        else:
            res['type'] = self.OSM
            res['data'] = temp[0]
        return res

    def processProvince(self, d):
        if d==None:
            return None
        return d if "Jakarta" not in d else d

    def getData(self,data, name):
        return data[name] if name in data else None
    
    def getVillage(self, data):
        if self.getData(data, 'municipality') != None:
            return self.getData(data, 'municipality')
        elif self.getData(data, 'village') != None:
            return self.getData(data, 'village')
        else:
            return None
    
    def getCityOSM(self, data):
        if data==None:
            return data
        return self.transformCity[data] if data in self.transformCity else data
    def osmDataCommonTransform(self, data):
        address = data['address']
        res = {
            'country': self.getData(address, 'country'),
            'country_code': self.getData(address, 'country_code'),
            'province': self.processProvince(self.getData(address, 'city')),
            'city': self.getCityOSM(self.getData(address, 'state_district')),
            'kecamatan': self.getData(address, 'county'),
            'kelurahan': self.getVillage(address),
            'parsed_place_name': self.getData(data, 'display_name'),
            'coordinate': {
                'lat': self.getData(data, 'lat'),
                'lng': self.getData(data, 'lon')
            },
            'type': self.OSM,
            'place_id': str(self.getData(data, 'place_id')),
            'specific_api': {
                'geo_json': self.getData(data, 'geojson'),
                'boundingbox': self.getData(data, 'boundingbox')
            }
        }
        return res
    def getGoogleMapsAddressComponents(self, data):
        res = dict()
        for e in data:
            typePlace = e['types'][0]
            if typePlace=='country':
                res['country'] = e['long_name']
                res['country_code'] = e['short_name']
            elif typePlace=='administrative_area_level_1':
                res['province'] = self.processProvince(e['long_name'])
            elif typePlace == 'administrative_area_level_2':
                res['city'] = e['long_name']
            elif typePlace == 'administrative_area_level_3':
                res['kecamatan'] = e['long_name']
            elif typePlace == 'administrative_area_level_4':
                res['kelurahan'] = e['long_name']
        return res
    def googleMapsDataCommonTransform(self, data):
        address = self.getGoogleMapsAddressComponents(data['address_components'])
        res = {
            'country': self.getData(address, 'country'),
            'country_code': self.getData(address, 'country_code'),
            'province': self.processProvince(self.getData(address, 'province')),
            'city': self.getData(address, 'city'),
            'kecamatan': self.getData(address, 'kecamatan'),
            'kelurahan': self.getData(address, 'kelurahan'),
            'parsed_place_name': self.getData(data, 'formatted_address'),
            'coordinate': {
                'lat': str(self.getData(data['geometry']['location'], 'lat')),
                'lng': str(self.getData(data['geometry']['location'], 'lng'))
            },
            'type': self.GOOGLE_MAPS,
            'place_id': str(self.getData(data, 'place_id')),
            'specific_api': {
                'geometry': self.getData(data, 'geometry'),
            }
        }
        return res
    def geocodeDataCommonTransform(self, data):
        res = None
        if data['type'] == self.OSM:
            res = self.osmDataCommonTransform(data['data'])
        elif data['type'] == self.GOOGLE_MAPS:
            res = self.googleMapsDataCommonTransform(data['data'])
        else:
            return data
        return res
    def geoCodeCommonQuery(self, q):
        return self.geocodeDataCommonTransform(self.geocodeQuery(q))
# a = GeoCoding()
# print(a.nominatimGeocode('polsek duren sawit')[0])
# print(a.geocodeQuery('polsek duren sawit'))

# Use this instead, because it convert to common format for both google maps or open street map
# print(a.geoCodeCommonQuery('polsek duren sawit'))