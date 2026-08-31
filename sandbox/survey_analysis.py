"""
Exploratory analysis of the Stack Overflow Developer Survey 2025 dataset.

Downloads the survey data, builds the column overview and missing-value tables,
and writes those tables and all figures into the output/ directory.
"""

import os
import kagglehub
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["font.size"] = 10

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 0. Dataset download
# ---------------------------------------------------------------------------

def preuzmi_dataset():
    path = kagglehub.dataset_download(
        "edoardogalli/stack-overflow-annual-developer-survey-2025"
    )
    print("Path to dataset files:", path)
    return path


# ---------------------------------------------------------------------------
# 1. Loading and basic overview
# ---------------------------------------------------------------------------

def ucitaj_podatke(path):
    # The file is valid UTF-8 (verified by strict-decoding the whole file).
    # utf-8-sig strips the BOM in front of the first column name (ResponseId).
    df = pd.read_csv(os.path.join(path, "survey_results_public.csv"), low_memory=False, encoding="utf-8-sig")
    schema = pd.read_csv(os.path.join(path, "survey_results_schema.csv"), encoding="utf-8-sig")
    return df, schema


def pregled_kolona(df, schema):
    """Build a table of column name, dtype, unique value count and question text."""
    schema_map = schema.drop_duplicates(subset="qname").set_index("qname")["question"]

    redovi = []
    for kol in df.columns:
        redovi.append({
            "kolona": kol,
            "tip": str(df[kol].dtype),
            "broj_jedinstvenih": df[kol].nunique(dropna=True),
            "opis_pitanja": schema_map.get(kol, ""),
        })
    return pd.DataFrame(redovi)


# ---------------------------------------------------------------------------
# 2. Missing value analysis
# ---------------------------------------------------------------------------

def missing_values_tabela(df):
    missing = df.isna().mean().sort_values(ascending=False) * 100
    tab = missing.reset_index()
    tab.columns = ["kolona", "procenat_missing"]
    return tab


def graf_missing_top(missing_tab, n=20, fname="missing_top20.png"):
    top = missing_tab.head(n)
    plt.figure(figsize=(9, 7))
    sns.barplot(data=top, x="procenat_missing", y="kolona", color="#4C72B0")
    plt.xlabel("Procenat nedostajućih vrednosti (%)")
    plt.ylabel("Kolona")
    plt.title(f"Top {n} kolona sa najviše nedostajućih vrednosti")
    plt.tight_layout()
    out = os.path.join(FIG_DIR, fname)
    plt.savefig(out, dpi=150)
    plt.close()
    return out


# ---------------------------------------------------------------------------
# 3. Target variable
# ---------------------------------------------------------------------------

def izdvoj_populaciju_za_kompenzaciju(df):
    """Currently employed professional developers, the subset the compensation
    question applies to."""
    return df[
        (df["MainBranch"] == "I am a developer by profession")
        & (df["Employment"].astype(str).str.contains("Employed", na=False))
    ]


def analiza_kompenzacije(df):
    dev = izdvoj_populaciju_za_kompenzaciju(df)
    comp_raw = dev["ConvertedCompYearly"].dropna()

    lo, hi = comp_raw.quantile([0.01, 0.99])
    comp_clean = comp_raw[(comp_raw >= lo) & (comp_raw <= hi)]

    plt.figure(figsize=(8, 5))
    sns.histplot(comp_raw, bins=60, color="#4C72B0")
    plt.xlabel("Godišnja kompenzacija (USD)")
    plt.ylabel("Broj ispitanika")
    plt.title("Kompenzacija pre čišćenja outliera")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "comp_before_cleaning.png"), dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(comp_clean, bins=60, color="#55A868")
    plt.xlabel("Godišnja kompenzacija (USD)")
    plt.ylabel("Broj ispitanika")
    plt.title("Kompenzacija posle čišćenja outliera (1.-99. percentil)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "comp_after_cleaning.png"), dpi=150)
    plt.close()

    return {
        "n_populacija": len(dev),
        "n_sa_odgovorom": len(comp_raw),
        "procenat_missing": round(dev["ConvertedCompYearly"].isna().mean() * 100, 1),
        "n_posle_ciscenja": len(comp_clean),
        "granice_ciscenja": (round(lo, 2), round(hi, 2)),
        "stats_raw": comp_raw.describe(),
        "stats_clean": comp_clean.describe(),
    }


def analiza_kategorickog_kandidata(df, kolona="AISelect"):
    counts = df[kolona].value_counts(dropna=True)
    plt.figure(figsize=(8, 5))
    sns.barplot(x=counts.values, y=counts.index, color="#C44E52")
    plt.xlabel("Broj ispitanika")
    plt.ylabel("")
    plt.title(f"Raspodela odgovora - {kolona}")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, f"{kolona}_distribution.png"), dpi=150)
    plt.close()
    return counts


# ---------------------------------------------------------------------------
# 4. Multi-select columns
# ---------------------------------------------------------------------------

def top_n_multiselect(df, kolona, n=10):
    razdvojeno = df[kolona].dropna().str.split(";")
    sve_vrednosti = razdvojeno.explode().str.strip()
    top = sve_vrednosti.value_counts().head(n)
    return top


def graf_top_multiselect(top, naziv_kolone, fname):
    plt.figure(figsize=(8, 5))
    sns.barplot(x=top.values, y=top.index, color="#8172B2")
    plt.xlabel("Broj ispitanika koji su naveli")
    plt.ylabel("")
    plt.title(f"Top {len(top)} - {naziv_kolone}")
    plt.tight_layout()
    out = os.path.join(FIG_DIR, fname)
    plt.savefig(out, dpi=150)
    plt.close()
    return out


# ---------------------------------------------------------------------------
# 5. Descriptive EDA
# ---------------------------------------------------------------------------

def top_zemlje(df, n=10):
    top = df["Country"].value_counts().head(n)
    plt.figure(figsize=(8, 5))
    sns.barplot(x=top.values, y=top.index, color="#4C72B0")
    plt.xlabel("Broj ispitanika")
    plt.ylabel("")
    plt.title(f"Top {n} zemalja po broju ispitanika")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "top_countries.png"), dpi=150)
    plt.close()
    return top


def iskustvo_vs_kompenzacija(df):
    dev = izdvoj_populaciju_za_kompenzaciju(df).dropna(subset=["ConvertedCompYearly", "YearsCode"]).copy()
    lo, hi = dev["ConvertedCompYearly"].quantile([0.01, 0.99])
    dev = dev[(dev["ConvertedCompYearly"] >= lo) & (dev["ConvertedCompYearly"] <= hi)]

    dev["YearsCode_num"] = pd.to_numeric(dev["YearsCode"], errors="coerce")
    dev = dev.dropna(subset=["YearsCode_num"])
    binovi = [0, 3, 6, 10, 15, 20, 100]
    labele = ["0-3", "4-6", "7-10", "11-15", "16-20", "20+"]
    dev["iskustvo_bin"] = pd.cut(dev["YearsCode_num"], bins=binovi, labels=labele)

    plt.figure(figsize=(9, 5))
    sns.boxplot(data=dev, x="iskustvo_bin", y="ConvertedCompYearly", color="#4C72B0", showfliers=False)
    plt.xlabel("Godine iskustva u programiranju")
    plt.ylabel("Godišnja kompenzacija (USD)")
    plt.title("Kompenzacija u odnosu na godine iskustva")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "experience_vs_compensation.png"), dpi=150)
    plt.close()
    return dev


def kompenzacija_po_obrazovanju(df):
    dev = izdvoj_populaciju_za_kompenzaciju(df).dropna(subset=["ConvertedCompYearly", "EdLevel"]).copy()
    lo, hi = dev["ConvertedCompYearly"].quantile([0.01, 0.99])
    dev = dev[(dev["ConvertedCompYearly"] >= lo) & (dev["ConvertedCompYearly"] <= hi)]

    poredak = dev.groupby("EdLevel")["ConvertedCompYearly"].median().sort_values(ascending=False).index

    plt.figure(figsize=(9, 6))
    sns.boxplot(data=dev, y="EdLevel", x="ConvertedCompYearly", order=poredak, color="#55A868", showfliers=False)
    plt.xlabel("Godišnja kompenzacija (USD)")
    plt.ylabel("")
    plt.title("Kompenzacija po nivou obrazovanja")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "compensation_by_education.png"), dpi=150)
    plt.close()
    return dev


# ---------------------------------------------------------------------------
# 6. Statistical test
# ---------------------------------------------------------------------------

def test_remote_vs_inperson(df):
    from scipy import stats

    dev = izdvoj_populaciju_za_kompenzaciju(df).dropna(subset=["ConvertedCompYearly", "RemoteWork"]).copy()
    lo, hi = dev["ConvertedCompYearly"].quantile([0.01, 0.99])
    dev = dev[(dev["ConvertedCompYearly"] >= lo) & (dev["ConvertedCompYearly"] <= hi)]

    remote = dev.loc[dev["RemoteWork"] == "Remote", "ConvertedCompYearly"]
    inperson = dev.loc[dev["RemoteWork"] == "In-person", "ConvertedCompYearly"]

    t_stat, p_val = stats.ttest_ind(remote, inperson, equal_var=False)
    return {
        "n_remote": len(remote),
        "n_inperson": len(inperson),
        "medijana_remote": remote.median(),
        "medijana_inperson": inperson.median(),
        "t_stat": t_stat,
        "p_val": p_val,
    }


# ---------------------------------------------------------------------------
# Main - runs every step and writes the tables and figures used by the report
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    path = preuzmi_dataset()
    df, schema = ucitaj_podatke(path)

    print("\n=== KORAK 1: Osnovni pregled ===")
    print("Dimenzije (redovi, kolone):", df.shape)

    kolone_tab = pregled_kolona(df, schema)
    kolone_tab.to_csv(os.path.join(OUTPUT_DIR, "column_overview.csv"), index=False)
    print("Sacuvano: output/column_overview.csv")
    print(kolone_tab.head(15).to_string(index=False))

    print("\n=== KORAK 2: Nedostajuce vrednosti ===")
    missing_tab = missing_values_tabela(df)
    missing_tab.to_csv(os.path.join(OUTPUT_DIR, "missing_values.csv"), index=False)
    print("Sacuvano: output/missing_values.csv")
    print(missing_tab.head(20).to_string(index=False))

    fig_path = graf_missing_top(missing_tab, n=20)
    print("Sacuvan grafik:", fig_path)

    print("\nBroj kolona bez ijedne nedostajuce vrednosti:",
          (missing_tab["procenat_missing"] == 0).sum())
    print("Broj kolona sa >90% nedostajucih vrednosti:",
          (missing_tab["procenat_missing"] > 90).sum())

    print("\n=== KORAK 3: Ciljna promenljiva ===")
    comp_info = analiza_kompenzacije(df)
    print(comp_info)
    ai_counts = analiza_kategorickog_kandidata(df, "AISelect")
    print(ai_counts)

    print("\n=== KORAK 4: Multi-select kolone ===")
    top_lang = top_n_multiselect(df, "LanguageHaveWorkedWith", n=10)
    graf_top_multiselect(top_lang, "programski jezici (LanguageHaveWorkedWith)", "top10_languages.png")
    print(top_lang)

    top_db = top_n_multiselect(df, "DatabaseHaveWorkedWith", n=10)
    graf_top_multiselect(top_db, "baze podataka (DatabaseHaveWorkedWith)", "top10_databases.png")
    print(top_db)

    print("\n=== KORAK 5: Deskriptivna EDA ===")
    top_zemlje(df, n=10)
    iskustvo_vs_kompenzacija(df)
    kompenzacija_po_obrazovanju(df)

    print("\n=== KORAK 6: Statisticki test ===")
    test_rez = test_remote_vs_inperson(df)
    print(test_rez)
