"""
Builds the Word report of the initial dataset analysis.

Reads the tables and figures that survey_analysis.py already wrote into
output/, so nothing is recomputed here.
"""

import os
import pandas as pd
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

BASE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE, "output")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

TIM = "Nikola Jevtić, Katarina Tomašević"


def dodaj_naslov_dokumenta(doc):
    naslov = doc.add_paragraph()
    naslov.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = naslov.add_run("Inicijalna eksplorativna analiza dataseta\nStack Overflow Developer Survey 2025")
    run.bold = True
    run.font.size = Pt(18)

    doc.add_paragraph()
    for linija in [
        "Predmet: Uvod u nauku o podacima",
        "Nastavnik: prof. Branko Arsić",
        f"Tim: {TIM}",
        "PMF Kragujevac",
    ]:
        p = doc.add_paragraph(linija)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()


def dodaj_sliku(doc, fname, sirina_cm=15):
    doc.add_picture(os.path.join(FIG_DIR, fname), width=Cm(sirina_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


def dodaj_opis_grafika(doc, tekst):
    p = doc.add_paragraph()
    run = p.add_run(tekst)
    run.italic = True
    run.font.size = Pt(10)


def stilizuj_tabelu(tabela):
    tabela.style = "Light Grid Accent 1"
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell in tabela.rows[0].cells:
        for p in cell.paragraphs:
            for r in p.runs:
                r.bold = True


def main():
    doc = Document()

    stil = doc.styles["Normal"]
    stil.font.size = Pt(11)
    stil.font.name = "Calibri"

    dodaj_naslov_dokumenta(doc)

    # ------------------------------------------------------------------
    doc.add_heading("1. Opis dataseta i izvora", level=1)
    doc.add_paragraph(
        "Stack Overflow Developer Survey je godišnja anketa koju Stack Overflow sprovodi među "
        "razvijačima softvera širom sveta još od 2011. godine i predstavlja jedan od najvećih "
        "javno dostupnih izvora podataka o profilu, tehnologijama i platama u IT industriji. "
        "Izdanje iz 2025. godine sadrži 49.123 odgovora iz 177 zemalja, prikupljenih kroz upitnik "
        "od približno 60 pitanja koja pokrivaju demografiju ispitanika, korišćene tehnologije, "
        "odnos prema AI alatima, kompenzaciju i zadovoljstvo poslom."
    )
    doc.add_paragraph(
        "Dataset je preuzet sa Kaggle platforme (mirror zvaničnog Stack Overflow dataseta, autor "
        "edoardogalli), programski, preko biblioteke kagglehub. Sastoji se iz tri fajla: "
        "survey_results_public.csv sa individualnim odgovorima, survey_results_schema.csv koji "
        "šifre kolona povezuje sa tačnim tekstom pitanja iz ankete, i PDF dokumenta sa kompletnim "
        "upitnikom. Podaci su realni, prikupljeni anketiranjem, bez ikakvog sintetičkog generisanja, "
        "što ih čini pogodnim za rad koji podrazumeva stvarne probleme kvaliteta podataka - "
        "nedostajuće vrednosti, nekonzistentne odgovore i outliere."
    )

    # ------------------------------------------------------------------
    doc.add_heading("2. Osnovne dimenzije i pregled kolona", level=1)
    doc.add_paragraph(
        "Tabela odgovora ima 49.123 reda i 170 kolona. Kolone pokrivaju osam tematskih celina: "
        "osnovnu demografiju (uzrast, obrazovanje, zemlju, radni status), način učenja programiranja, "
        "tehnologije koje ispitanik koristi (jezici, baze podataka, platforme, razvojna okruženja - "
        "najveći deo kolona), odnos prema AI alatima i agentima, kompenzaciju, korišćenje samog "
        "Stack Overflow-a i opšte zadovoljstvo poslom. Većina kolona koje se odnose na tehnologije "
        "i AI alate dolazi u parovima ili trojkama oblika *HaveWorkedWith / *WantToWorkWith / "
        "*Admired, gde je jedna ćelija string sa više vrednosti razdvojenih znakom ';' - o tome više "
        "u odeljku 5."
    )
    doc.add_paragraph(
        "Kompletan spisak svih 170 kolona sa tipom podatka, brojem jedinstvenih vrednosti i "
        "originalnim tekstom pitanja iz ankete je izvezen u column_overview.csv. Ispod je prikazan "
        "podskup kolona koje se koriste u ovoj analizi:"
    )

    kolone_tab = pd.read_csv(os.path.join(OUTPUT_DIR, "column_overview.csv"))
    relevantne = [
        "ResponseId", "MainBranch", "Age", "EdLevel", "Employment", "Country", "YearsCode",
        "WorkExp", "DevType", "RemoteWork", "CompTotal", "ConvertedCompYearly", "AISelect",
        "LanguageHaveWorkedWith", "DatabaseHaveWorkedWith", "JobSat",
    ]
    prikaz = kolone_tab[kolone_tab["kolona"].isin(relevantne)].set_index("kolona").loc[relevantne].reset_index()

    tabela = doc.add_table(rows=1, cols=4)
    stilizuj_tabelu(tabela)
    hdr = tabela.rows[0].cells
    hdr[0].text, hdr[1].text, hdr[2].text, hdr[3].text = "Kolona", "Tip", "Jedinstvenih vr.", "Pitanje iz ankete"
    for _, red in prikaz.iterrows():
        cells = tabela.add_row().cells
        cells[0].text = str(red["kolona"])
        cells[1].text = str(red["tip"])
        cells[2].text = str(red["broj_jedinstvenih"])
        opis = str(red["opis_pitanja"])
        cells[3].text = (opis[:110] + "...") if len(opis) > 110 else opis
        for c in cells:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)

    # ------------------------------------------------------------------
    doc.add_heading("3. Analiza nedostajućih vrednosti", level=1)
    doc.add_paragraph(
        "Samo tri kolone nemaju nijednu nedostajuću vrednost: ResponseId, MainBranch i Age - sve "
        "tri su među prvim pitanjima u anketi i obavezne su. Na suprotnom kraju, 30 kolona ima "
        "preko 90% nedostajućih vrednosti. Kada se pogleda koje su to kolone, obrazac je jasan: "
        "gotovo sve su prateća, uslovna pitanja tipa 'ako ste odgovorili X, opišite detaljnije' "
        "(kolone sa nastavkom WantEntry, HaveEntry ili _TEXT), koja se ispitaniku prikazuju samo ako "
        "je na prethodno pitanje dao određen odgovor. Ovo nije nasumično nedostajanje (MCAR) već "
        "posledica dizajna ankete - kolona nedostaje zato što pitanje jednostavno nije ni "
        "postavljeno tom ispitaniku, što po definiciji spada u MAR (missing at random uslovno na "
        "posmatranu promenljivu - odgovor na prethodno pitanje)."
    )
    dodaj_sliku(doc, "missing_top20.png")
    dodaj_opis_grafika(
        doc,
        "Grafik prikazuje 20 kolona sa najvećim procentom nedostajućih vrednosti. Cilj je bio da se "
        "brzo identifikuju kolone koje praktično nemaju upotrebnu vrednost za analizu u trenutnom "
        "obliku. Zaključak: nedostajanje kod ovih kolona je gotovo u potpunosti objašnjivo skip "
        "logikom ankete, a ne slučajno - i te kolone verovatno neće biti korisne kao samostalne "
        "prediktorske promenljive u glavnom radu.",
    )
    doc.add_paragraph(
        "Situacija je drugačija kod promenljive koju planiramo kao glavni cilj predviđanja - "
        "CompTotal/ConvertedCompYearly - gde nedostajanje nije objašnjivo isključivo skip logikom, "
        "već je verovatno povezano sa samom vrednošću (ispitanici svesno preskaču pitanje o plati). "
        "Ovo je detaljnije obrazloženo u sledećem odeljku, jer direktno utiče na izbor ciljne "
        "promenljive."
    )

    # ------------------------------------------------------------------
    doc.add_heading("4. Ciljna promenljiva", level=1)
    doc.add_paragraph(
        "Kao glavnog kandidata za regresiju posmatramo kompenzaciju ispitanika. Anketa beleži ovu "
        "informaciju kroz dve kolone: CompTotal, sirovi odgovor u dnevnoj valuti ispitanika "
        "(pitanje eksplicitno traži 'godišnju kompenzaciju u vašoj svakodnevnoj valuti'), i "
        "ConvertedCompYearly, istu vrednost preračunatu u američke dolare na godišnjem nivou. Pošto "
        "je uzorak globalan, CompTotal iz različitih zemalja nije direktno uporediv (mešaju se "
        "dinari, evri, rupije, dolari...), pa u analizi koristimo ConvertedCompYearly kao stvarnu "
        "ciljnu promenljivu, a CompTotal pominjemo kao izvorno pitanje iz kog je izvedena."
    )
    doc.add_paragraph(
        "Pre računanja raspodele, suzili smo posmatranu populaciju na ispitanike za koje pitanje o "
        "plati uopšte ima smisla: one koji su odgovorili da su 'developer po profesiji' (MainBranch) "
        "i da su trenutno zaposleni (Employment). Toj populaciji pripada 28.741 ispitanik. Proverili "
        "smo i da li se nedostajanje kompenzacije može objasniti isključivo time što pitanje nije "
        "relevantno za deo ispitanika (studenti, penzioneri, hobisti) - i to samo delimično stoji: "
        "čak i u ovoj suženoj, relevantnoj populaciji, 41,3% ispitanika nije prijavilo kompenzaciju "
        "(16.881 od 28.741 odgovorilo). To ukazuje da je nedostajanje ovde pre svega posledica lične "
        "odluke ispitanika da ne otkrije platu, što je verovatno povezano sa samom vrednošću "
        "(MNAR), a ne čisto tehnička posledica strukture ankete."
    )
    doc.add_paragraph(
        "Prvi, jednostavniji pristup koji planiramo za glavni rad je da model treniramo isključivo "
        "na ispitanicima koji su prijavili platu (complete-case pristup), uz eksplicitno poređenje "
        "karakteristika grupe koja jeste i koja nije prijavila platu, kako bismo bar opisno "
        "proverili da li postoji sistematska razlika (npr. po zemlji ili godinama iskustva) koja bi "
        "ukazivala na pristrasnost uzorka. I posle ovog suženja ostaje 16.881 ispitanik sa "
        "prijavljenom platom, što je i dalje dovoljno za regresioni model. Kao dodatni pravac za "
        "istraživanje u glavnom radu, razmatramo i da li bi imalo smisla iskoristiti preostalih 41% "
        "ispitanika bez prijavljene plate: model bi se prvo istrenirao samo na onima koji su "
        "odgovorili, zatim bi se njime predvidele (labelirale) plate za ostatak uzorka, i na kraju "
        "bismo uporedili da li prošireni skup podataka poboljšava generalizaciju modela u odnosu na "
        "polazni. Ovo bismo tretirali strogo kao eksperiment i jasno naznačili u radu da je deo "
        "podataka u tom slučaju predviđen modelom, a ne prijavljen od strane ispitanika, jer takav "
        "pristup nosi rizik da model samo ponavlja sopstvene greške na širem skupu."
    )
    dodaj_sliku(doc, "comp_before_cleaning.png")
    dodaj_opis_grafika(
        doc,
        "Histogram sirove raspodele ConvertedCompYearly (16.881 ispitanik sa odgovorom, pre "
        "čišćenja) pokazuje zašto je čišćenje neophodno: nekoliko ekstremnih vrednosti (do "
        "33,5 miliona dolara godišnje, verovatno greške pri unosu ili pogrešno preračunata valuta) "
        "razvlače osu x do te mere da je ceo ostatak raspodele nečitljiv, sabijen u jedan stubac uz "
        "levu ivicu. Zaključak: neophodno je ukloniti ekstremne vrednosti pre bilo kakve dalje "
        "analize ili modelovanja.",
    )
    doc.add_paragraph(
        "Za čišćenje smo primenili jednostavno ograničenje na 1. i 99. percentil (125,80 - "
        "441.574,60 USD), čime je uklonjeno 338 ekstremnih vrednosti, a ostalo je 16.543 ispitanika. "
        "Medijana posle čišćenja iznosi 80.000 USD godišnje, prosek 92.328 USD (standardna devijacija "
        "68.327 USD) - prosek je i dalje osetno veći od medijane, što je očekivano za kompenzaciju: "
        "raspodela ostaje desno asimetrična i posle uklanjanja ekstrema, jer manji broj visoko "
        "plaćenih pozicija (npr. u SAD) povlači prosek naviše."
    )
    dodaj_sliku(doc, "comp_after_cleaning.png")
    dodaj_opis_grafika(
        doc,
        "Histogram iste promenljive posle ograničavanja na 1.-99. percentil. Cilj grafika je da "
        "pokaže stvarni oblik raspodele kompenzacije bez uticaja ekstremnih vrednosti. Zaključak: "
        "raspodela je jasno desno asimetrična sa modom oko 70.000-90.000 USD, što odgovara "
        "očekivanjima za globalni uzorak developera i potvrđuje da će transformacija (npr. "
        "logaritamska) verovatno biti korisna u fazi modelovanja.",
    )

    doc.add_paragraph(
        "Kao kandidata za klasifikacioni zadatak razmatramo AISelect - pitanje da li ispitanik "
        "trenutno koristi AI alate u razvoju softvera, sa pet mogućih odgovora."
    )
    dodaj_sliku(doc, "AISelect_distribution.png")
    dodaj_opis_grafika(
        doc,
        "Bar-chart prikazuje broj ispitanika po odgovoru na AISelect. Grafik je napravljen da "
        "proverimo da li su klase dovoljno balansirane za klasifikaciju. Zaključak: klase nisu "
        "izbalansirane - kategorija 'koristim AI alate svakodnevno' (15.863) je skoro devet puta "
        "brojnija od najmanje kategorije 'ne koristim, ali planiram uskoro' (1.795), tako da bi u "
        "glavnom radu klasifikacija verovatno zahtevala ili spajanje kategorija (npr. 'koristi AI' "
        "vs. 'ne koristi'), ili tehnike za rad sa neizbalansiranim klasama.",
    )

    # ------------------------------------------------------------------
    doc.add_heading("5. Multi-select kolone", level=1)
    doc.add_paragraph(
        "Veliki broj kolona (jezici, baze podataka, platforme, alati za razvoj) su multi-select "
        "pitanja gde je ceo odgovor ispitanika sačuvan kao jedan string sa vrednostima odvojenim "
        "znakom ';' (npr. 'Python;SQL;JavaScript'). Za dalji rad ove kolone treba razložiti u "
        "binarne/dummy kolone (jedna kolona po tehnologiji, 1 ako je ispitanik naveo tu tehnologiju, "
        "0 ako nije). Ispod prikazujemo primer takvog parsiranja na dve kolone - programski jezici i "
        "baze podataka - kao najavu punog feature engineeringa koji sledi u glavnom radu."
    )
    dodaj_sliku(doc, "top10_languages.png")
    dodaj_opis_grafika(
        doc,
        "Top 10 programskih jezika po broju ispitanika koji su ih naveli kao jezike sa kojima rade "
        "(LanguageHaveWorkedWith), posle razdvajanja stringa po ';'. Grafik pokazuje da parsiranje "
        "radi ispravno i daje uvid u sastav uzorka. Zaključak: JavaScript, HTML/CSS, SQL i Python "
        "dominiraju, što je u skladu sa prethodnim izdanjima ove ankete i potvrđuje da uzorak "
        "odgovara očekivanom profilu developera.",
    )
    dodaj_sliku(doc, "top10_databases.png")
    dodaj_opis_grafika(
        doc,
        "Isti postupak primenjen na kolonu DatabaseHaveWorkedWith. Cilj je pokazati da se isti "
        "pristup parsiranja može primeniti na bilo koju multi-select kolonu. Zaključak: PostgreSQL i "
        "MySQL su ubedljivo najzastupljenije baze u uzorku, dok je broj različitih baza koje se "
        "pojavljuju dovoljno velik da bi posle dummy-kodiranja dao koristan skup prediktorskih "
        "promenljivih.",
    )

    # ------------------------------------------------------------------
    doc.add_heading("6. Deskriptivna EDA", level=1)
    dodaj_sliku(doc, "top_countries.png")
    dodaj_opis_grafika(
        doc,
        "Top 10 zemalja po broju ispitanika. Grafik je napravljen da proverimo geografsku "
        "raspodelu uzorka. Zaključak: SAD ubedljivo prednjače (7.226 ispitanika), a uzorak je inače "
        "jako neravnomeran po zemljama - ovo je važno imati u vidu kod tumačenja bilo kog nalaza o "
        "kompenzaciji, jer razlike između zemalja mogu da dominiraju nad drugim efektima.",
    )
    dodaj_sliku(doc, "experience_vs_compensation.png")
    dodaj_opis_grafika(
        doc,
        "Boxplot kompenzacije (posle čišćenja outliera) po binovima godina iskustva u programiranju "
        "(YearsCode). Grafik proverava da li postoji očekivana veza između iskustva i plate. "
        "Zaključak: medijana kompenzacije raste skoro monotono sa iskustvom, od oko 12.000 USD za "
        "0-3 godine do preko 100.000 USD za 20+ godina, što je snažan signal da će YearsCode biti "
        "koristan prediktor u regresionom modelu.",
    )
    dodaj_sliku(doc, "compensation_by_education.png")
    dodaj_opis_grafika(
        doc,
        "Boxplot kompenzacije po nivou obrazovanja. Cilj je proveriti da li formalno obrazovanje "
        "pravi razliku u plati. Zaključak: razlike postoje, ali su osetno manje izražene nego kod "
        "godina iskustva - medijane po nivoima obrazovanja se dosta preklapaju, sa donekle višom "
        "medijanom kod profesionalnih diploma (JD, MD, Ph.D). Ovo je u skladu sa uobičajenim "
        "nalazom da je u IT industriji praktično iskustvo bolji prediktor kompenzacije od formalnog "
        "obrazovanja.",
    )

    # ------------------------------------------------------------------
    doc.add_heading("7. Statistički test", level=1)
    doc.add_paragraph(
        "Testirali smo da li postoji statistički značajna razlika u kompenzaciji između ispitanika "
        "koji rade u potpunosti remote i onih koji rade u potpunosti in-person (kolona RemoteWork), "
        "unutar iste suzene populacije zaposlenih profesionalnih developera i posle istog "
        "ograničenja na 1.-99. percentil. Korišćen je Welchov t-test (ne pretpostavlja jednake "
        "varijanse između grupa), sa pragom značajnosti 0,05."
    )
    doc.add_paragraph(
        "Medijana kompenzacije iznosi 93.000 USD za remote ispitanike (n=5.625) naspram 49.011 USD "
        "za in-person ispitanike (n=2.283). Test daje t=22,76 i p<0,001 (p≈6,2×10⁻¹⁰⁹), što je "
        "duboko ispod praga značajnosti - razlika je statistički visoko značajna. Treba naglasiti "
        "da ovaj test sam po sebi ne dokazuje da remote rad uzrokuje veću platu: remote pozicije su "
        "znatno češće u razvijenim, visoko plaćenim tržištima (pre svega SAD), pa je zemlja "
        "verovatan zbunjujući faktor (confounder) koji test u ovom obliku ne kontroliše. U glavnom "
        "radu bi ovo trebalo proveriti npr. ANOVA-om koja uključuje zemlju kao dodatni faktor, ili "
        "poređenjem unutar iste zemlje."
    )

    # ------------------------------------------------------------------
    doc.add_heading("8. Zaključak", level=1)
    doc.add_paragraph(
        "Stack Overflow Developer Survey 2025 nam deluje kao dobar izbor za seminarski rad iz "
        "nekoliko razloga. Uzorak je dovoljno velik (49.123 ispitanika) i geografski raznovrstan "
        "(177 zemalja) da omogući ozbiljnu statističku analizu, a istovremeno je dovoljno 'prljav' - "
        "sa realnim problemima nedostajućih vrednosti, outlierima u kompenzaciji i "
        "multi-select kolonama koje zahtevaju parsiranje - da pruži prostor za primenu tehnika "
        "obrađenih na predmetu, umesto da se svede na trivijalno čišćenje."
    )
    doc.add_paragraph(
        "Kompenzacija (ConvertedCompYearly) se nameće kao prirodan izbor ciljne promenljive za "
        "regresiju, uz jasnu svest o njenom glavnom nedostatku - oko 41% ispitanika u relevantnoj "
        "populaciji nije prijavilo platu, verovatno iz ličnih razloga, što nedostajanje čini "
        "verovatnije MNAR nego slučajnim. Naš polazni plan je da model gradimo na ispitanicima koji "
        "su odgovorili (i dalje preko 16.500 ispitanika), uz opisno poređenje sa grupom koja nije "
        "odgovorila kako bismo bar približno procenili pristrasnost uzorka. Kao dodatni, "
        "istraživački pravac za glavni rad, planiramo da isprobamo i da li se preostalih 41% "
        "podataka može iskoristiti tako što bi se plate za tu grupu predvidele modelom istreniranim "
        "na onima koji su odgovorili, a zatim uporedile performanse modela treniranog na proširenom "
        "skupu sa polaznim - uz jasno navođenje da bi u tom slučaju deo ciljne promenljive bio "
        "generisan modelom, a ne prijavljen od ispitanika."
    )
    doc.add_paragraph(
        "Multi-select kolone (jezici, baze podataka, platforme, i slično) otvaraju dosta prostora "
        "za feature engineering, a demonstrisano parsiranje pokazuje da je taj korak tehnički "
        "jednostavan za sprovesti na širem skupu kolona u glavnom radu. Na osnovu svega navedenog, "
        "smatramo da dataset ispunjava uslove za odobrenje i predlažemo da ga koristimo za dalji rad."
    )

    izlaz = os.path.join(OUTPUT_DIR, "SO_Survey_2025_initial_analysis.docx")
    doc.save(izlaz)
    print("Sacuvano:", izlaz)


if __name__ == "__main__":
    main()
