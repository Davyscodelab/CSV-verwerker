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

import os
import argparse
import pandas as pd
from datetime import datetime
import logging

# -------------------------
# LOGGING CONFIGURATIE
# -------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bank_export.log",
    filemode="a",
)

# Optioneel: logging ook naar console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logging.getLogger("").addHandler(console)

# -------------------------
# HULPFUNCTIES
# -------------------------

def parse_maand_argument(maand_str):
    """
    Converteert 'MM/YYYY' naar een datetime object.
    """
    try:
        return datetime.strptime(maand_str, "%m/%Y")
    except ValueError:
        logging.error(f"Fout: Ongeldig maandformaat: {maand_str}. Gebruik 'MM/YYYY'.")
        raise


def verwerk_csv_bestanden(map_pad, maand_filter):
    """
    Leest alle CSV-bestanden in map_pad, filtert op maand_filter, 
    behoudt kolommen en exporteert naar exports/.
    """

    logging.info(f"Start verwerking in map: {map_pad}")

    if not os.path.exists(map_pad):
        logging.error(f"Map bestaat niet: {map_pad}")
        return

    # Exportmap
    export_map = os.path.join(map_pad, "exports")
    os.makedirs(export_map, exist_ok=True)

    # Kolommen die behouden worden
    vereiste_kolommen = ["Datum", "Omschrijving", "Bedrag", "Saldo", "Credit", "Debet"]

    # Alle CSV’s inlezen
    csv_bestanden = [f for f in os.listdir(map_pad) if f.lower().endswith(".csv")]
    logging.info(f"Aantal CSV-bestanden gevonden: {len(csv_bestanden)}")

    for bestand in csv_bestanden:
        pad = os.path.join(map_pad, bestand)
        logging.info(f"Verwerken: {bestand}")

        try:
            df = pd.read_csv(pad)
        except Exception as e:
            logging.exception(f"Kon bestand niet inlezen: {pad}")
            continue

        # Check kolommen
        ontbrekend = [k for k in vereiste_kolommen if k not in df.columns]
        if ontbrekend:
            logging.error(f"Ontbrekende kolommen in {bestand}: {ontbrekend}")
            continue

        # Datum parsing
        try:
            df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True)
        except Exception:
            logging.exception(f"Kon 'Datum'-kolom niet converteren in {bestand}")
            continue

        # Filteren op maand/jaar
        df_filtered = df[
            (df["Datum"].dt.month == maand_filter.month)
            & (df["Datum"].dt.year == maand_filter.year)
        ]

        logging.info(
            f"{len(df_filtered)} rijen over na filtering op {maand_filter.strftime('%m/%Y')}"
        )

        # Exporteren
        export_bestand = f"{os.path.splitext(bestand)[0]}_export_{maand_filter.strftime('%m%Y')}.csv"
        export_pad = os.path.join(export_map, export_bestand)

        df_filtered.to_csv(export_pad, index=False)
        logging.info(f"Export voltooid: {export_bestand}")

    logging.info("Alle bestanden verwerkt.")


# -------------------------
# MAIN SCRIPT
# -------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSV verwerker KBC")
    parser.add_argument(
        "--maand",
        type=str,
        help="Formaat MM/YYYY. Laat weg voor huidige maand.",
    )
    parser.add_argument(
        "map_pad",
        type=str,
        nargs="?",
        default=".",
        help="Map waar CSV-bestanden staan (standaard: huidige map)",
    )

    args = parser.parse_args()

    # Bepaal maand
    if args.maand:
        maand_filter = parse_maand_argument(args.maand)
    else:
        # Huidige maand
        maand_filter = datetime.today().replace(day=1)
        logging.info(
            f"Geen maand opgegeven — huidige maand wordt gebruikt: {maand_filter.strftime('%m/%Y')}"
        )

    verwerk_csv_bestanden(args.map_pad, maand_filter)
