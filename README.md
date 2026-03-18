# CSV verwerker
Dit script verwerkt CSV-bankuittreksels (KBC-formaat) automatisch.
Het leest alle CSV's in de map, filtert op een gekozen maand, 
en slaat het resultaat op in een submap `exports/`.

## Wat doet het?
- Behoudt enkel de relevante kolommen: Datum, Omschrijving, Bedrag, Saldo, Credit en Debet
- Filtert op maand en jaar
- Exporteert naar: `bestandsnaam_export_MMYYYY.csv`

## Gebruik

### Met het .bat bestand (Windows)
Dubbelklik op `bank_export.bat` — het script vraagt zelf om een maand.

### Via command line
```bash
python bank_export.py                  # huidige maand
python bank_export.py --maand 04/2025  # specifieke maand
python bank_export.py --maand 04/2025 /pad/naar/map  # andere map
```

## Vereisten
- Python 3
- pandas (`pip install pandas`)

## Notities
Ontwikkeld met een handje hulp van Claude (Anthropic).
