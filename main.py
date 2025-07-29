import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import sys
import os

#Odstraní nechtěné znaky z textu
def cisti_text(text):
    return text.strip().replace('\xa0', '').replace(' ', '')

#Z dané základní URL najde odkaz na stránku okresu Ostrava-město.
#Hledá ve 14. tabulce konkrétní řádek obsahující "Ostrava-město".
def ziskej_odkaz_na_okres(zakladni_url):
    response = requests.get(zakladni_url)
    soup = BeautifulSoup(response.text, "html.parser")
    tabulka_14 = soup.find_all("table", class_="table")[13]
    for radek in tabulka_14.find_all("tr"):
        if "Ostrava-město" in radek.text:
            a_tag = radek.find("a", href=lambda href: href and "ps32" in href)
            if a_tag:
                return urljoin(zakladni_url, a_tag["href"])
    return None

#Vrátí seznam obcí z daného okresního odkazu ve formátu (kód, název, URL).
def ziskej_obce_z_okresu(odkaz_na_okres):
    response = requests.get(odkaz_na_okres)
    soup = BeautifulSoup(response.text, "html.parser")
    odkazy = []
    for radek in soup.find_all("tr"):
        bunky = radek.find_all("td")
        if len(bunky) >= 3:
            a_tag = bunky[0].find("a")
            if a_tag and "ps311?" in a_tag.get("href", ""):
                url = urljoin(odkaz_na_okres, a_tag["href"])
                kod_obce = bunky[0].text.strip()
                nazev_obce = bunky[1].text.strip()
                odkazy.append((kod_obce, nazev_obce, url))
    return odkazy

#Z první obce načte seznam názvů politických stran.
def ziskej_nazvy_stran(obec_url):
    response = requests.get(obec_url)
    soup = BeautifulSoup(response.text, "html.parser")
    nazvy_stran = []
    for tabulka in soup.find_all("table"):
        for radek in tabulka.find_all("tr"):
            td = radek.find_all("td")
            if len(td) >= 4:
                nazev = td[1].text.strip()
                if nazev and not nazev.isdigit() and nazev not in nazvy_stran:
                    nazvy_stran.append(nazev)
    return nazvy_stran

# Pro konkrétní obec vrátí řádek s kódem obce, názvem, 
#volebními údaji a počtem hlasů pro jednotlivé strany.
def ziskej_data_obce(kod_obce, nazev_obce, obec_url):
    print(f"Zpracovávám obec: {kod_obce} - {nazev_obce}")  # Výpis do konzole
    soup = BeautifulSoup(requests.get(obec_url).text, "html.parser")
    tds = soup.find_all("td", headers=["sa2", "sa3", "sa6"])
    hodnoty = [cisti_text(td.text) for td in tds]
    hlasy_stran = []
    for tabulka in soup.find_all("table"):
        for radek in tabulka.find_all("tr"):
            td = radek.find_all("td")
            if len(td) >= 3:
                hlas = cisti_text(td[2].text)
                if hlas.isdigit():
                    hlasy_stran.append(hlas)
    return [kod_obce, nazev_obce] + hodnoty + hlasy_stran


# Uloží všechny sebrané výsledky do CSV souboru.
def uloz_vysledky_do_csv(soubor, hlavicka, data):
    try:
        with open(soubor, mode="w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(hlavicka)
            for radek in data:
                writer.writerow(radek)
        print(f"Hotovo! Výsledky byly uloženy do '{soubor}'")
    except PermissionError:
        print("Chyba: Soubor je pravděpodobně otevřený. Zavři ho a spusť skript znovu.")

#Hlavní řídící funkce.
#Zpracuje argumenty, zkontroluje vstupy, získá data a uloží je do CSV.
def main():
    if len(sys.argv) != 3:
        print("Použití: python main.py https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ vysledky_Ostrava.csv")
        sys.exit(1)

    url1 = sys.argv[1]
    arg2 = sys.argv[2]

    # Detekce záměny argumentů
    if url1.lower().endswith(".csv") and arg2.startswith("http"):
        print("Upozornění: Pravděpodobně jste prohodili argumenty. Opraveno automaticky.")
        zakladni_url = arg2
        vystupni_soubor = url1
    else:
        zakladni_url = url1
        vystupni_soubor = arg2

    if zakladni_url != "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ":
        print("Chyba: Neplatná vstupní URL.")
        sys.exit(1)

    odkaz_na_okres = ziskej_odkaz_na_okres(zakladni_url)
    if not odkaz_na_okres:
        print("Chyba: Odkaz na okres Ostrava-město nebyl nalezen.")
        sys.exit(1)

    obce = ziskej_obce_z_okresu(odkaz_na_okres)
    if not obce:
        print("Chyba: Nepodařilo se získat žádné obce z daného odkazu.")
        sys.exit(1)

    hlavicka = ["Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy"]
    hlavicka.extend(ziskej_nazvy_stran(obce[0][2]))
    data = [ziskej_data_obce(kod, nazev, url) for kod, nazev, url in obce]
    uloz_vysledky_do_csv(vystupni_soubor, hlavicka, data)

if __name__ == "__main__":
    main()
