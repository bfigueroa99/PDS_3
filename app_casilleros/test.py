def translate_json456(data):
    for i in range(3):
        casillero_id = data[i].get('id')
        availability = data[i].get('availability')
        reserved = data[i].get('reserved')
        confirmed = data[i].get('confirmed')
        loaded = data[i].get('loaded')
        locked = data[i].get('locked')

        if casillero_id in [4,5,6]:
            if availability:
                data[i]['disponible'] = "D"
            if reserved:
                data[i]['disponible'] = "R"
            if confirmed:
                data[i]['disponible'] = "C"
            if loaded:
                data[i]['disponible'] = "A"

            if locked == True:
                data[i]['abierto'] = False
            if locked == False:
                data[i]['abierto'] = True

            data[i].pop('availability', None)
            data[i].pop('reserved', None)
            data[i].pop('confirmed', None)
            data[i].pop('loaded', None)
            data[i].pop('opened', None)
            data[i].pop('locked', None)

    return data



def translate_json654(data):
    casillero_id = data.get('id')
    disponible = data.get('disponible')
    abierto = data.get('abierto')

    if casillero_id in [4,5,6]:
        if disponible == "D":
            data['availability'] = True
            data['reserved'] = False
            data['confirmed'] = False
            data['loaded'] = False
        elif disponible == "R":
            data['availability'] = False
            data['reserved'] = True
            data['confirmed'] = False
            data['loaded'] = False
        elif disponible == "C":
            data['availability'] = False
            data['reserved'] = False
            data['confirmed'] = True
            data['loaded'] = False
        elif disponible == "A":
            data['availability'] = False
            data['reserved'] = False
            data['confirmed'] = False
            data['loaded'] = True

        if abierto == True:
            data['locked'] = False
        elif abierto == False:
            data['locked'] = True

        data['height'] = 26.0
        data['width'] = 43.0

        data.pop('disponible', None)
        data.pop('abierto', None)
        data.pop('o_email', None)
        data.pop('r_email', None)
        data.pop('r_username', None)
        data.pop('o_name', None)
        data.pop('tamano', None)

    return data

# test = {
#     "id": 4,
#     "height": 26.0,
#     "width": 43.0,
#     "availability": True,
#     "reserved": False,
#     "confirmed": False,
#     "loaded": False,
#     "opened": False,
#     "locked": True,
#     "station": 1
# }

# test2 = {
#     'disponible': 'R',
#     'id': 4, 
#     'o_email': 'test@miuandes.cl', 
#     'abierto': False, 
#     'r_email': 'test@miuandes.cl', 
#     'tamano': 'M', 
#     'r_username': 'benja', 
#     'o_name': 'benja2'
# }

# # data = translate_json456(test)
# # print(data)

# data2 = translate_json654(test2)
# print(data2)

import requests

def mostrar_amiwos():
    response = requests.get('https://tsqrmn8j-8000.brs.devtunnels.ms/stations/2/get_lockers_by_station/')
    translated = translate_json456(response.json())
    print(translated)

def reservar_amiwos():
    requests.put("https://tsqrmn8j-8000.brs.devtunnels.ms/lockers/6/update_locked_false/")
    response = requests.get('https://tsqrmn8j-8000.brs.devtunnels.ms/stations/2/get_lockers_by_station/')
    # print(response.json())
    translated = translate_json456(response.json())
    print(translated)

# reservar_amiwos()

def reservar_nosotros():
    json_data = {'disponible': 'D','abierto': False}
    headers = {'Content-Type': 'application/json'}
    print(json_data.type)

    response = requests.post(f'http://161.35.0.111:8000/api/casilleros/actualizar/3', json=json_data, headers=headers)
    print(response.status_code)