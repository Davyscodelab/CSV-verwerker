"""
bank_export.py
--------------
Verwerkt alle CSV-bankuittreksels (KBC-formaat) in een opgegeven map.
- Behoudt enkel: Datum, Omschrijving, Bedrag, Saldo, Credit, Debet
- Filtert op de huidige maand (of een opgegeven maand)
- Slaat exports op in submap 'exports/' met naam: bestandsnaam_export_MMYYYY.csv

Gebruik:
    python bank_export.py /pad/naar/map
    python bank_export.py /pad/naar/map --maand 04/2025
"""

import pandas as pd
import argparse
import sys
from pathlib import Path
from datetime import datetime
#pandas is een library om data in een tabel te zetten.
#df staat voor dataframe, dat is de tabel
KOLOMMEN = ["Datum", "Omschrijving", "Bedrag", "Saldo", "Credit", "Debet"]


def is_bankbestand(pad: Path) -> bool:
    """Controleert of een CSV de verwachte bankkolommen heeft."""
    try:
        df = pd.read_csv(pad, sep=",", dtype=str, nrows=1)
        return all(k in df.columns for k in KOLOMMEN)
    except Exception:
        return False


def lees_csv(pad: Path) -> pd.DataFrame:
    df = pd.read_csv(pad, sep=",", dtype=str)
    return df[KOLOMMEN].copy()


def filter_op_maand(df: pd.DataFrame, maand_str: str) -> pd.DataFrame:
    df = df.copy()
    df["_datum"] = pd.to_datetime(df["Datum"], format="%d/%m/%Y", errors="coerce")
    target = pd.to_datetime(maand_str, format="%m/%Y")
    masker = (df["_datum"].dt.month == target.month) & \
             (df["_datum"].dt.year  == target.year)
    return df[masker].drop(columns=["_datum"])


def verwerk_bestand(pad: Path, maand_str: str, uitvoer_map: Path) -> None:
    print(f"\n📄 Verwerken: {pad.name}")

    df = lees_csv(pad)
    df_gefilterd = filter_op_maand(df, maand_str)

    if df_gefilterd.empty:
        print(f"   ⚠️  Geen rijen gevonden voor {maand_str} — overgeslagen.")
        return

    mm, yyyy = maand_str.split("/")
    uitvoer_naam = f"{pad.stem}_export_{mm}{yyyy}.csv"
    uitvoer_pad  = uitvoer_map / uitvoer_naam

    df_gefilterd.to_csv(uitvoer_pad, index=False, sep=",")
    print(f"   ✅ {len(df_gefilterd)} rij(en) → {uitvoer_naam}")


def main():
    parser = argparse.ArgumentParser(description="KBC CSV-export verwerker")
    parser.add_argument("map", nargs="?", default=None, help="Map met invoer-CSV bestanden (standaard: map van het script)")
    parser.add_argument(
        "--maand",
        default=None,
        help="Maand om te filteren, formaat MM/YYYY (standaard: huidige maand)",
    )
    args = parser.parse_args()

    invoer_map = Path(args.map) if args.map else Path(__file__).parent
    if not invoer_map.is_dir():
        print(f"❌ Opgegeven pad is geen map: {invoer_map}")
        sys.exit(1)

    maand_str = args.maand or datetime.now().strftime("%m/%Y")

    uitvoer_map = invoer_map / "exports"
    uitvoer_map.mkdir(exist_ok=True)

    print(f"📂 Map      : {invoer_map}")
    print(f"📅 Maand    : {maand_str}")
    print(f"💾 Exports  : {uitvoer_map}")

    # Alle CSV's in de map — exports-submap automatisch uitgesloten
    csv_bestanden = [
        p for p in invoer_map.glob("*.csv")
        if p.parent == invoer_map and is_bankbestand(p)
    ]

    if not csv_bestanden:
        print("\n⚠️  Geen geldige bankbestanden gevonden in de map.")
        sys.exit(0)

    print(f"\n🔍 {len(csv_bestanden)} bankbestand(en) gevonden.")

    for bestand in sorted(csv_bestanden):
        verwerk_bestand(bestand, maand_str, uitvoer_map)

    print("\n✅ Klaar! Druk op Enter om af te sluiten.")
    input()


if __name__ == "__main__":
    main()
    # Als dit script direct uitgevoerd wordt, start dan de hoofdfunctie