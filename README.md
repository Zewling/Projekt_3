# Projekt_3
Webscraper
# Výsledky voleb 2017 - Web Scraper

Tento Python skript slouží ke scrapování dat o výsledcích parlamentních voleb v ČR z webu [volby.cz](https://www.volby.cz). Konkrétně se zaměřuje na zvolený okres Ostrava-město, zpracovává údaje za všechny obce a výsledky ukládá do CSV souboru.

---

# Požadavky

- Python 3.8 nebo novější
- Virtuální prostředí (doporučeno)

# Instalace knihoven:
pip install csv   # za csv lze dosadit jakoukoliv jinou potřebnou knihovnu


# Vytvoření requirements.txt
pip freeze > requierements.txt

---

# Spuštění skriptu

Skript se spouští pomocí dvou argumentů:

python main.py <VSTUPNÍ_URL> <NAZEV_SOUBORU.csv>

Konkrétně

python main.py https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ vysledky_Ostrava.csv

---

## Co skript dělá

1. Načte vstupní URL s výběrem krajů.
2. Najde odkaz na okres **Ostrava-město**.
3. Z něj získá odkazy na jednotlivé obce.
4. Pro každou obec vytáhne:
   - Kód obce
   - Název obce
   - Počet voličů
   - Vydané obálky
   - Platné hlasy
   - Hlasy pro jednotlivé politické strany
5. Výstup ukládá do CSV souboru.

---

# Tipy a poznámky

- Před spuštěním se ujisti, že výstupní soubor není otevřený (např. v Excelu), jinak vznikne chyba `PermissionError`.

