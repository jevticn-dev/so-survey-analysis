# Analiza Stack Overflow Developer Survey 2025

Seminarski rad iz predmeta **Uvod u nauku o podacima** (Prirodno-matematički fakultet, Univerzitet u Kragujevcu).

## Opis projekta

Projekat se bavi analizom podataka iz **Stack Overflow Developer Survey 2025** — godišnje ankete koju Stack Overflow sprovodi među programerima širom sveta. Anketa pokriva demografiju ispitanika, radno iskustvo, korišćene tehnologije, tip zaposlenja i obrazovanja, kao i podatke o kompenzaciji.

**Cilj rada** je izgradnja regresionog modela za predviđanje ukupne godišnje kompenzacije ispitanika (kolona `CompTotal`) na osnovu ostalih obeležja iz ankete. Put do modela obuhvata:

1. čišćenje podataka i obradu nedostajućih vrednosti,
2. eksplorativnu analizu podataka (EDA) i ispitivanje veza između obeležja i ciljne promenljive,
3. feature engineering (transformacije, kodiranje kategorijskih obeležja, obrada višestrukih odgovora),
4. treniranje i poređenje regresionih modela, uz evaluaciju i interpretaciju rezultata.

Podaci se preuzimaju sa Kaggle-a pomoću biblioteke `kagglehub` i ne čuvaju se u repozitorijumu.

## Struktura repozitorijuma

| Folder | Sadržaj |
| --- | --- |
| `sandbox/` | Inicijalno istraživanje dataseta — prva, zaokružena faza rada (osnovni pregled podataka, nedostajuće vrednosti, raspodela ciljne promenljive i prateći izveštaj). Zatvorena celina, ostaje kao trag o polaznoj analizi. |
| `data/raw/` | Sirovi podaci, onako kako se preuzmu sa izvora. Sadržaj se ne verzioniše. |
| `data/processed/` | Očišćen i pripremljen skup podataka, spreman za analizu i modelovanje. |
| `notebooks/` | Radni Jupyter notebook-ovi, organizovani po tematskim celinama (npr. nedostajuće vrednosti, analiza kompenzacije, feature engineering). |
| `src/` | Python moduli sa funkcijama koje se koriste na više mesta (učitavanje i čišćenje podataka, feature engineering, modeli). |
| `report/` | Finalni izveštaj i konsolidovani notebook koji hronološki prati sadržaj izveštaja. |

## Pokretanje

Potreban je Python 3.10 ili noviji.

```bash
# 1. Kreiranje i aktiviranje virtuelnog okruženja
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 2. Instalacija zavisnosti
pip install -r requirements.txt
```

Ako `requirements.txt` još nije dostupan, osnovne zavisnosti mogu se instalirati direktno:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn statsmodels jupyter kagglehub
```

Notebook-ovi se zatim pokreću iz aktiviranog okruženja:

```bash
jupyter notebook
```

## Napomena

Repozitorijum se razvija postepeno, kako rad napreduje. Sekcije sa opisom metodologije, nalazima eksplorativne analize i zaključcima modela biće dodavane u README i u finalni izveštaj tokom rada.
