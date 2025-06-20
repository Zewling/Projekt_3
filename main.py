"""
main.py: Třetí projekt do Engeto Akademie Tester s Pythonem

author: Josef Věrovský
email: pepa.verovsky@seznam.cz / josef.verovsky@outlook.com
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import sys

def cisti_text(text):
    return text.strip().replace('\xa0', '').replace(' ', '')

# Kontrola vstupních argumentů
if len(sys.argv) != 3:
    print("Použití: python main.py https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ vysledky_Ostrava.csv")
    sys.exit(1)

zakladni_url = sys.argv[1]
vystupni_soubor = sys.argv[2]

# Kontrola, že vstupní URL je přesně požadovaná
if zakladni_url != "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ":
    print("Chyba: Neplatná vstupní URL. Musí být přesně: ""https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ""")
    sys.exit(1)


# Načtení základní stránky
response = requests.get(zakladni_url)
soup = BeautifulSoup(response.text, "html.parser")

# Najdeme všechny tabulky s class="table"
tabulky = soup.find_all("table", class_="table")

# 14. tabulka, kde je město Ostrava
tabulka_14 = tabulky[13]
radek_v_tabulce_14 = tabulka_14.find_all("tr")

posledni_radek = None
for radek in radek_v_tabulce_14:
    if "Ostrava-město" in radek.text:
        posledni_radek = radek
        break

a_tag = posledni_radek.find("a", href=lambda href: href and "ps32" in href)
if a_tag:
    relativni_odkaz = a_tag["href"]
    odkaz_na_okres = urljoin(zakladni_url, relativni_odkaz)
    print("URL na okres Ostrava-město:", odkaz_na_okres)
else:
    print("Odkaz na okres Ostrava-město nebyl nalezen.")
    sys.exit(1)

# Načtení nové stránky z odkazu
okres_Ostrava = requests.get(odkaz_na_okres)
soup_okres = BeautifulSoup(okres_Ostrava.text, "html.parser")

# Odkazy na obce + jejich kódy a názvy
odkazy_jednotlivych_obci = []
radky = soup_okres.find_all("tr")
for radek in radky:
    bunky = radek.find_all("td")
    if len(bunky) >= 3:
        a_tag2 = bunky[0].find("a")
        if a_tag2 and "ps311?" in a_tag2.get("href", ""):
            url = urljoin(odkaz_na_okres, a_tag2["href"])
            kod_obce = bunky[0].text.strip()
            nazev_obce = bunky[1].text.strip()
            odkazy_jednotlivych_obci.append((kod_obce, nazev_obce, url))

# Vytvoření CSV
try:
    with open(vystupni_soubor, mode="w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        hlavicka = [
            "Kód obce", "Název obce", "Voliči v seznamu",
            "Vydané obálky", "Platné hlasy"
        ]

        # Získání názvů stran z první obce
        prvni_url = odkazy_jednotlivych_obci[0][2]
        soup_prvni = BeautifulSoup(requests.get(prvni_url).text, "html.parser")
        tabulky_stran = soup_prvni.find_all("table")
        nazvy_stran = []
        for tabulka in tabulky_stran:
            for radek in tabulka.find_all("tr"):
                td = radek.find_all("td")
                if len(td) >= 4:
                    nazev = td[1].text.strip()
                    if nazev and not nazev.isdigit() and nazev not in nazvy_stran:
                        nazvy_stran.append(nazev)
        hlavicka.extend(nazvy_stran)
        writer.writerow(hlavicka)

        # Zpracování každé obce
        for kod_obce, nazev_obce, obec_url in odkazy_jednotlivych_obci:
            print(f"Zpracovávám obec: {kod_obce} - {nazev_obce}")
            obec_soup = BeautifulSoup(requests.get(obec_url).text, "html.parser")

            # Získání údajů: voliči, obálky, platné hlasy
            tds = obec_soup.find_all("td", headers=["sa2", "sa3", "sa6"])
            hodnoty = [cisti_text(td.text) for td in tds]

            # Hlasy pro každou stranu
            hlasy_stran = []
            tabulky_stran = obec_soup.find_all("table")
            for tabulka in tabulky_stran:
                for radek in tabulka.find_all("tr"):
                    td = radek.find_all("td")
                    if len(td) >= 3:
                        hlas = cisti_text(td[2].text)
                        if hlas.isdigit():
                            hlasy_stran.append(hlas)

            writer.writerow([kod_obce, nazev_obce] + hodnoty + hlasy_stran)

        print(f"Hotovo! Výsledky byly uloženy do '{vystupni_soubor}'")

except PermissionError:
    print("Chyba: Soubor je pravděpodobně otevřený. Zavři soubor a spusť skript znovu.")
