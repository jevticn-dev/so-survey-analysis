# Analiza Stack Overflow Developer Survey 2025

Seminarski rad iz predmeta **Uvod u nauku o podacima** (Prirodno-matematički fakultet, Univerzitet u Kragujevcu).

## Opis projekta

Projekat se bavi analizom podataka iz **Stack Overflow Developer Survey 2025** — godišnje ankete koju Stack Overflow sprovodi među programerima širom sveta. Anketa pokriva demografiju ispitanika, radno iskustvo, korišćene tehnologije, tip zaposlenja i obrazovanja, kao i podatke o kompenzaciji.

**Cilj rada** je izgradnja regresionog modela za predviđanje ukupne godišnje kompenzacije ispitanika na osnovu ostalih obeležja iz ankete. Ciljna promenljiva je `ConvertedCompYearly` — kompenzacija preračunata u dolare, jer prijavljeni iznos u ispitanikovoj valuti (`CompTotal`) nije uporediv između zemalja. Modeluje se njen dekadni logaritam, pošto je sirova raspodela krajnje iskošena.

Rad je išao u pet koraka, ovim redom:

1. **opis skupa** — izvor, struktura ankete, sastav uzorka, nedostajuće vrednosti i kandidati za ciljnu promenljivu,
2. **izbor i provera ciljne promenljive** — u kakvom su odnosu dve kolone o kompenzaciji i koja je upotrebljiva,
3. **čišćenje** — populacija, duplikati, strukturne greške, netipične vrednosti, nedostajuće vrednosti i podela na trening i test skup,
4. **feature engineering** — izvođenje novih promenljivih iz kolona sa višestrukim odgovorima i iz rang-pitanja,
5. **modelovanje** — linearna regresija sa dijagnostikom, Ridge, Lasso i regresija na glavne komponente, uz izbor modela i merenje na test skupu.

Podaci se preuzimaju sa Kaggle-a pomoću biblioteke `kagglehub` i ne čuvaju se u repozitorijumu.

## Rezultat

Izabrani model je **Lasso** (λ = 0,00155), koji od 707 kolona zadržava **423**. Na test skupu, koji ni u jednoj odluci nije korišćen:

| mera | vrednost |
| --- | --- |
| R² (na logaritmu plate) | **0,6720** |
| tipičan promašaj | **23,8%**, odnosno **16.630 dolara** |
| predviđanje u okviru dvostruko | kod **87,6%** ispitanika |
| predviđanje u okviru četvrtine | kod **51,6%** ispitanika |

Da bi se taj broj mogao pročitati, pre pravljenja ijednog modela izmerene su tri referentne tačke (unakrsnom validacijom nad trening skupom): predviđanje konstantom daje **−0,0001**, sama zemlja **0,5429**, a sva anketna obeležja bez ijedne izvedene promenljive **0,6668**. Promenljive izvedene u četvrtom koraku dodaju **+0,0101** preko te poslednje letvice — manje nego što je izgledalo na trening skupu.

Poredak modela na test skupu poklopio se sa poretkom po unakrsnoj validaciji, što potvrđuje da izbori nisu pravljeni prema ishodu.

Model **nije podjednako upotrebljiv na celom rasponu**: u srednjih osamdeset posto plata tipičan promašaj je između 17,7% i 32,2%, dok kod sedamnaest ispitanika sa prijavljenim iznosom ispod hiljadu dolara promašuje 1.199%.

## Tok rada

| Notebook | Šta radi | Rezultat |
| --- | --- | --- |
| `00_dataset_overview.ipynb` | opisuje izvor, strukturu ankete, sastav uzorka, nedostajuće vrednosti i kandidate za ciljnu promenljivu | `column_overview.csv` — pregled svih 170 kolona |
| `01_target_variable.ipynb` | bira ciljnu promenljivu i proverava kako je izvedena | `ConvertedCompYearly`, modeluje se logaritmovana |
| `02_data_cleaning.ipynb` | populacija, duplikati, strukturne greške, netipične vrednosti, nedostajuće vrednosti, podela na trening i test | `train.csv.gz` i `test.csv.gz` — 18.260 ispitanika, 129 kolona |
| `03_feature_engineering.ipynb` | izvodi promenljive iz multi-select kolona i rangiranja, sažima zemlju, proverava preklapanje | `train_features.csv.gz` i `test_features.csv.gz` — 429 kolona |
| `04_modeling.ipynb` | linearna regresija sa dijagnostikom, Ridge, Lasso i regresija na glavne komponente, uz izbor modela i merenje na test skupu | `test_predictions.csv.gz` i `model_coefficients.csv` |

Put kroz podatke: **49.123 ispitanika → 34.106 u populaciji → 19.461 sa prijavljenom platom → 18.260 posle uklanjanja netipičnih vrednosti.** Kolone: **170 → 129 posle čišćenja → 429 posle feature engineeringa**, odnosno 709 kolona modela posle enkodiranja.

Svaka odluka o podacima proverena je merenjem, a nalazi su zapisani u samim notebook-ovima uz motivaciju, kod, rezultat izvršenja i tumačenje.

### Spojena verzija

Notebook-i su rađeni **jedan za drugim, u gornjem redosledu**, i svaki je zaokružena celina koja se čita sama za sebe. Spajanje u jedan dokument urađeno je **na kraju**, kada je sve ostalo bilo gotovo.

Ako je za čitanje zgodnije imati sve na jednom mestu, tu je **`report/final_report.ipynb`** — svih pet koraka u jednom dokumentu, sa neprekidnom numeracijom kroz ceo rad: **43 sekcije i 38 grafika**. Sadržaj analize je isti kao u zasebnim notebook-ovima. Spajanjem su menjani brojevi sekcija i grafika i pozivanja na njih, formulacije koje su govorile o zasebnim notebook-ima („u prethodnom notebook-u" umesto „u prethodnom delu"), i dodata je naslovna celina na početku.

**Napomena:** notebook-i su veliki i pozivanja između sekcija su brojna, pa je moguće da je pri tom preslikavanju numeracije neka referenca nenamerno ostala pogrešna. Ako se negde ne poklapa, merodavni su zasebni notebook-i u `notebooks/`, gde je numeracija ona u kojoj je rad i pisan.

## Izvezene HTML verzije

Folder `html_preview/` sadrži isti sadržaj izvezen u HTML — sa svim ispisima, tabelama i graficima — za čitanje u pregledaču, bez pokretanja Jupyter-a i bez instaliranja zavisnosti:

| fajl | šta je |
| --- | --- |
| `00_dataset_overview.html` | opis skupa podataka |
| `01_target_variable.html` | ciljna promenljiva |
| `02_data_cleaning.html` | čišćenje i priprema |
| `03_feature_engineering.html` | izvođenje novih promenljivih |
| `04_modeling.html` | modelovanje |
| `final_report.html` | svih pet koraka u jednom dokumentu |

## Struktura repozitorijuma

| Folder | Sadržaj |
| --- | --- |
| `sandbox/` | Inicijalno istraživanje dataseta — prva, zaokružena faza rada (osnovni pregled podataka, nedostajuće vrednosti, raspodela ciljne promenljive i prateći izveštaj). Zatvorena celina, ostaje kao trag o polaznoj analizi. |
| `data/raw/` | Sirovi podaci, onako kako se preuzmu sa izvora. Sadržaj se ne verzioniše. |
| `data/processed/` | Očišćen i pripremljen skup podataka, kao i predviđanja i koeficijenti izabranog modela. Verzionišu se, da se rezultati mogu proveriti bez ponovnog pokretanja. |
| `notebooks/` | Radni Jupyter notebook-ovi, po jedan za svaki korak rada. |
| `report/` | `final_report.ipynb` — svih pet koraka spojenih u jedan dokument, sa jedinstvenom numeracijom sekcija i grafika. |
| `html_preview/` | Izvezene HTML verzije svih notebook-a i spojenog dokumenta, za čitanje bez Jupyter-a. |
| `src/` | `data_loader.py` — preuzimanje i učitavanje sirovih podataka. Ostalo se radi u notebook-ovima, jer je svaki korak vezan za svoje objašnjenje. |

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

Notebook-ovi se zatim pokreću iz aktiviranog okruženja:

```bash
jupyter notebook
```

Notebook-i se pokreću **redom, od `00` do `04`**, jer svaki čita ono što je prethodni zapisao u `data/processed/`. Fajlovi iz tog foldera su već u repozitorijumu, pa se svaki notebook može pokrenuti i sam, bez prethodnih.

## Podaci

Podaci ankete © Stack Overflow, iz [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/), pod licencom [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Obrađeni fajlovi u `data/processed/` izvedeni su iz njih i dele se pod istom licencom.

Sirovi podaci se ne čuvaju u repozitorijumu. Preuzimaju se sa Kaggle-a pri prvom pokretanju i smeštaju u `data/raw/`:

```python
from src.data_loader import load_raw

responses, schema = load_raw()
```

Preuzimanje se izvršava samo jednom — svako naredno pokretanje čita lokalnu kopiju iz `data/raw/`.

## Šta ostaje otvoreno

Nalazi i ograničenja izneseni su u zaključcima pojedinačnih koraka; ovo su ona koja se tiču rada u celini:

- **Uzorak nije slučajan uzorak programera** nego onih koji su popunili anketu i prijavili platu, a prijavljivanje plate zavisi od posmatranih obeležja. Model opisuje tu populaciju.
- **63 od 423 koeficijenta procenjena su na manje od pedeset ispitanika**, a dva najjača na po dva čoveka, pa se jačina koeficijenta ne sme čitati bez broja ispitanika iza njega.
- **Interakcije nisu probane**, a nelinearni modeli (stabla i ansambli) su izvan obima predmeta, pa su ostavljeni kao prvi sledeći korak.
