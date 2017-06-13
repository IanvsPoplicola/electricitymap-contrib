import arrow
import requests
import json
import pandas
import dateutil

def fetch_production(country_code='TW', session=None):
    
    r = session or requests.session()
    url = 'http://data.taipower.com.tw/opendata01/apply/file/d006001/001.txt'
    response = requests.get(url)
    content = response.content

    content = unicode(response.content,"UTF-8")
    data = json.loads(content)
    
    dumpDate = data['']
    prodData = data['aaData']
    
    tz = 'Asia/Taipei'
    dumpDate = arrow.get(dumpDate, 'YYYY-MM-DD HH:mm').replace(tzinfo=dateutil.tz.gettz(tz))
 
    objData = pandas.DataFrame(prodData);

    objData.columns = ['fueltype','name','capacity','output','percentage','additional']

    objData['fueltype'] = objData.fueltype.str.split('(').str[1]
    objData['fueltype'] = objData.fueltype.str.split(')').str[0]
    objData.drop('additional', axis=1, inplace=True)
    objData.drop('percentage', axis=1, inplace=True)
    
    objData = objData.convert_objects(convert_numeric=True)
    production = pandas.DataFrame(objData.groupby('fueltype').sum())
    production.columns = ['capacity','output']

    coal_production = production.ix['Coal'].output + production.ix['IPP-Coal'].output
    gas_production = production.ix['LNG'].output + production.ix['IPP-LNG'].output
    hydro_production = production.ix['Pumping Gen'].output
    oil_production = production.ix['Oil'].output + production.ix['Diesel'].output

    returndata = {
    		'countryCode': country_code,
        'datetime': dumpDate.datetime,
    		'production': {
    			  'coal': coal_production,
            'gas': gas_production,
            'oil': oil_production,
            'hydro' : hydro_production,
            'nuclear': production.ix['Nuclear'].output,
            'solar': production.ix['Solar'].output,
            'wind': production.ix['Wind'].output,
            'other': production.ix['Co-Gen'].output
        },
        'storage': {
            'hydro': production.ix['Pumping Load'].output
        },
        'source': 'taipower.com.tw'
    }

    return returndata

if __name__ == '__main__':
    print fetch_production()
