from datetime import datetime, time
import sys

import requests
from urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import urllib.parse as urlparse
from urllib.parse import parse_qs
import sqlite3
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


data_start = "20190101"
data_end = "20190631"

# marka,model,rodzaj-pojazdu,podrodzaj-pojazdu,pochodzenie-pojazdu,sposob-produkcji,rok-produkcji,
# data-pierwszej-rejestracji-w-kraju,data-rejestracji-za-granica,pojemnosc-skokwa-silnika,moc-netto-silnika,
# masa-wlasna,liczba-miejsc-ogolem,rodzaj-paliwa,kierownica-po-prawej-stronie,rejestracja-wojewodztwo

def get_voivodeship_dictionary():
    voivodeship_dict = dict()
    LINK = 'https://api.cepik.gov.pl/slowniki/wojewodztwa'
    response = requests.get(LINK, verify= False)
    response_json = response.json()
    response_json_data = response_json['data']
    attributes = response_json_data['attributes']['dostepne-rekordy-slownika']
    for att in attributes:
        voivodeship_dict[att['wartosc-slownika']] = att['klucz-slownika']
    return voivodeship_dict


def get_max_pages(voivodship):
    cepik_link = f"https://api.cepik.gov.pl/pojazdy?wojewodztwo={voivodship}&data-od={data_start}&data-do={data_end}&typ-daty=1" \
                 f"&tylko-zarejestrowane=true&pokaz-wszystkie-pola=false&limit=300"\
                 f"&filter[rodzaj-pojazdu]=samochód osobowy" \
                 f"&fields=marka,model,rodzaj-pojazdu,podrodzaj-pojazdu,pochodzenie-pojazdu,sposob-produkcji,rok-produkcji,data-pierwszej-rejestracji-w-kraju,data-ostatniej-rejestracji-w-kraju,data-rejestracji-za-granica,pojemnosc-skokowa-silnika,moc-netto-silnika,masa-wlasna,liczba-miejsc-ogolem,rodzaj-paliwa,kierownica-po-prawej-stronie,rejestracja-wojewodztwo"
    response = requests.get(cepik_link, verify=False)
    response_json = response.json()
    parsed = urlparse.urlparse(response_json['links']['last'])
    max_page = int(parse_qs(parsed.query)['page'][0])
    return max_page


def get_cars_dataframe(voivodeships):
    # columns = ["marka","model,rodzaj-pojazdu","podrodzaj-pojazdu","pochodzenie-pojazdu","sposob-produkcji","rok-produkcji","data-pierwszej-rejestracji-w-kraju","data-ostatniej-rejestracji-w-kraju","data-rejestracji-za-granica","pojemnosc-skokowa-silnika","moc-netto-silnika","masa-wlasna","liczba-miejsc-ogolem","rodzaj-paliwa","kierownica-po-prawej-stronie","rejestracja-wojewodztwo"]

    page_int = 1
    print('Start voivodeships loop')
    for key in voivodeships:
        df = pd.DataFrame()
        voivodship = voivodeships[key]
        last_page = get_max_pages(voivodship)
        print('downloading data for ', key)
        print('last page is ', last_page)
        for i in range(1, last_page + 1):
            print(f'Im on page number {i} of {last_page}')
            try:
                cepik_link = f"https://api.cepik.gov.pl/pojazdy?wojewodztwo={voivodship}&data-od={data_start}&data-do={data_end}&typ-daty=1" \
                             f"&tylko-zarejestrowane=true&pokaz-wszystkie-pola=true&limit=300&page={i}"\
                             f"&filter[rodzaj-pojazdu]=samochód osobowy"\
                             f"&fields=marka,model,rodzaj-pojazdu,podrodzaj-pojazdu,pochodzenie-pojazdu," \
                             f"sposob-produkcji,rok-produkcji,data-pierwszej-rejestracji-w-kraju," \
                             f"data-ostatniej-rejestracji-w-kraju,data-rejestracji-za-granica," \
                             f"pojemnosc-skokowa-silnika,moc-netto-silnika,masa-wlasna," \
                             f"liczba-miejsc-ogolem,rodzaj-paliwa,kierownica-po-prawej-stronie,rejestracja-wojewodztwo"

                response = requests.get(cepik_link, verify=False)
                response_json = response.json()
                response_json_data = response_json['data']
                # print(response_json_data)

                vehicle_tab = []
                for vehicle in response_json_data:
                    vehivle_dict = vehicle.get("attributes")
                    vehicle_tab.append(vehivle_dict)
                vehicle_dataframe = pd.DataFrame(vehicle_tab)
                df = df.append(vehicle_dataframe, ignore_index=True)

                # print(df)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                pass
        save_name = "woj_"+key+".csv"
        df.to_csv(f'data/'+save_name)

suma = 0
v = get_voivodeship_dictionary()
for key in v:
    suma += get_max_pages(v[key])
    print(f'{key} got pages: {get_max_pages(v[key])}')

print(suma)

voivodeships_dictionary = get_voivodeship_dictionary()
data = get_cars_dataframe(voivodeships_dictionary)
print(data)