def construct_pdf_url(category, date_str, section, number, doc_type):
    db = "snciv" if (category or "").upper() == "CIVILE" else "snpen"
    try:
        day, month, year = date_str.split('/')
    except Exception:
        day, month, year = "01", "01", "1970"
    formatted_date = f"{year}{month}{day}"

    section_map = {
        "PRIMA": "s10", "SECONDA": "s20", "TERZA": "s30",
        "QUARTA": "s40", "QUINTA": "s50", "SESTA": "s60",
        "SETTIMA": "s70", "UNITE": "su0"
    }
    sec_code = section_map.get((section or "").upper(), "s00")
    t_code = "O" if "ORDINANZA" in (doc_type or "").upper() else "S"
    if "INTERLOCUTORIA" in (doc_type or "").upper():
        t_code = "I"
    return f"https://www.italgiure.giustizia.it/xway/application/nif/clean/hc.dll?verbo=attach&db={db}&id=./{formatted_date}/{db}@{sec_code}@a{year}@n{str(number).zfill(5)}@t{t_code}.clean.pdf"

def parse_card_soup(card_soup, label):
    def get_v(arg):
        found = card_soup.find('span', {'data-arg': arg})
        return found.get_text(strip=True) if found else "N/A"
    return {
        "category": label,
        "id": get_v('id'),
        "section": get_v('szdec'),
        "kind": get_v('kind'),
        "type": get_v('tipoprov'),
        "number": get_v('numcard'),
        "date": get_v('datdep'),
        "ecli": get_v('ecli'),
        "president": get_v('presidente'),
        "relator": get_v('relatore')
    }