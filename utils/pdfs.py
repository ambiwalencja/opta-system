from fpdf import FPDF

class PatientPDF(FPDF):
    def __init__(self):
        super().__init__()
        # 1. Register the Unicode-compatible font
        # Make sure DejaVuSans.ttf is in your project folder!
        self.add_font('DejaVu', '', 'DejaVuSans.ttf')
        self.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf') # For bold versions

    def header(self):
        # Top "Bar" like a web header
        self.set_fill_color(41, 128, 185)  # Nice Blue
        self.rect(0, 0, 210, 15, 'F') 
        self.set_y(5)
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 5, "KARTA KLIENTA - STOWARZYSZENIE OPTA", ln=True, align="C")
        self.set_text_color(0, 0, 0)
        self.ln(10)

    def draw_card_header(self, title):
        """Creates a section header that looks like a web card header"""
        self.set_font("DejaVu", "B", 11)
        self.set_fill_color(245, 245, 245)
        self.cell(0, 7, f"  {title}", ln=True, fill=True)
        self.set_draw_color(200, 200, 200)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(2)

    def label_value_split(self, label, value, width=95, label_width=45, ln=False):
        """Creates a key-value pair. Two of these fit on one line (190mm total)"""
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(label_width, 8, f"{label}: ", ln=False)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(0, 0, 0)
        self.cell(width - label_width, 8, str(value) if value else "---", ln=ln)
    
    def label_value_split_with_wrap(self, label, value, width=95, label_width=45, ln=False):
        """Creates a key-value pair that supports text wrapping."""
        value_width = width - label_width
        
        # Save the starting position to handle side-by-side columns
        start_x = self.get_x()
        start_y = self.get_y()

        # 1. Draw the Label
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(label_width, 5, f"{label}: ", ln=False)

        # 2. Draw the Value using multi_cell
        self.set_font("DejaVu", "", 9)
        self.set_text_color(0, 0, 0)
        
        # multi_cell automatically wraps text within value_width
        # h=5 is the height of a single line
        self.multi_cell(value_width, 5, str(value) if value else "---", align='L')

        # 3. Handle the "Cursor" position
        # If we want side-by-side (ln=False), we move back up to start_y
        # but move X forward to the next column.
        if not ln:
            self.set_xy(start_x + width, start_y)
        else:
            # If we want a new line, we stay at the bottom of the wrapped text
            self.ln(2)

    def patient_row(self, label, value):
        # Label in Bold
        self.set_font("DejaVu", "B", 10)
        self.cell(40, 8, f"{label}:", ln=False)
        
        # Value in Regular
        self.set_font("DejaVu", "", 10)
        # Ensure value is a string to avoid errors
        text_value = str(value) if value is not None else "---"
        self.cell(0, 8, text_value, ln=True)

    def section_title(self, title):
        self.ln(5)
        self.set_fill_color(230, 230, 230)
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(2)

def generate_patient_pdf(pacjent_data):
    pdf = PatientPDF()
    pdf.add_page()
    
    # ===== DANE PODSTAWOWE I KONTAKTOWE =====
    pdf.draw_card_header("Dane Podstawowe i Kontaktowe")
    
    pdf.label_value_split_with_wrap("Imię i nazwisko", f'{pacjent_data.Imie} {pacjent_data.Nazwisko}', ln=False)
    pdf.label_value_split_with_wrap("ID Pacjenta", pacjent_data.ID_pacjenta, ln=True)
    
    pdf.label_value_split_with_wrap("Płeć", pacjent_data.Plec or "---", ln=False)
    pdf.label_value_split_with_wrap("Wiek", pacjent_data.Wiek or "---", ln=True)
    
    pdf.label_value_split_with_wrap("Stan cywilny", pacjent_data.Stan_cywilny or "---", ln=False)
    pdf.label_value_split_with_wrap("Wykształcenie", pacjent_data.Wyksztalcenie or "---", ln=True)
    
    pdf.label_value_split_with_wrap("Liczba dzieci", pacjent_data.Liczba_dzieci or "---", ln=False)
    pdf.label_value_split_with_wrap("Status zawodowy", pacjent_data.Status_zawodowy or "---", ln=True)
    
    pdf.label_value_split_with_wrap("Email", pacjent_data.Email or "---", ln=False)
    pdf.label_value_split_with_wrap("Telefon", pacjent_data.Telefon or "---", ln=True)
    
    pdf.label_value_split_with_wrap("Dzielnica", pacjent_data.Dzielnica or "---", ln=False)
    pdf.label_value_split_with_wrap("Ulica", pacjent_data.Ulica or "---", ln=True)
    
    address_parts = []
    if pacjent_data.Nr_domu:
        address_parts.append(f"nr {pacjent_data.Nr_domu}")
    if pacjent_data.Nr_mieszkania:
        address_parts.append(f"m. {pacjent_data.Nr_mieszkania}")
    address = ", ".join(address_parts) if address_parts else "---"
    pdf.label_value_split_with_wrap("Nr domu/mieszkania", address, ln=False)
    pdf.label_value_split_with_wrap("Kod pocztowy", pacjent_data.Kod_pocztowy or "---", ln=True)

    # ===== INFORMACJE O ZGŁOSZENIU =====
    pdf.draw_card_header("Informacje o zgłoszeniu")
    
    pdf.label_value_split_with_wrap("Data zgłoszenia", pacjent_data.Data_zgloszenia or "---", ln=False)
    pdf.label_value_split_with_wrap("Data ostatniej wizyty", pacjent_data.Data_ostatniej_wizyty or "---", ln=True)
    
    pdf.label_value_split_with_wrap("Źródło informacji", pacjent_data.Zrodlo_informacji or "---", width = 190, ln=True)
    if pacjent_data.Zrodlo_informacji_inne:
        pdf.label_value_split_with_wrap("Źródło informacji (inne)", pacjent_data.Zrodlo_informacji_inne, width = 190, ln=True)
    
    pdf.label_value_split_with_wrap("Placówka kierująca", pacjent_data.Placowka_kierujaca or "---", width = 190, ln=True)
    if pacjent_data.Placowka_kierujaca_inne:
        pdf.label_value_split_with_wrap("Placówka kierująca (inne)", pacjent_data.Placowka_kierujaca_inne, ln=True)
    
    korzystanie_z_pomocy = pacjent_data.Korzystanie_z_pomocy
    if korzystanie_z_pomocy and isinstance(korzystanie_z_pomocy, list):
        korzystanie_text = ", ".join(str(x) for x in korzystanie_z_pomocy)
    else:
        korzystanie_text = korzystanie_z_pomocy or "---"
    pdf.label_value_split_with_wrap("Korzystanie z pomocy", korzystanie_text, ln=True)
    
    if pacjent_data.Korzystanie_z_pomocy_inne:
        pdf.label_value_split_with_wrap("Korzystanie z pomocy (inne)", pacjent_data.Korzystanie_z_pomocy_inne, ln=True)

    # ===== DIAGNOZA I PLAN POMOCY =====
    pdf.draw_card_header("Diagnoza i plan pomocy")
    
    problemy = pacjent_data.Problemy
    if problemy and isinstance(problemy, list):
        problemy_text = ", ".join(str(x) for x in problemy)
    else:
        problemy_text = problemy or "---"
    pdf.label_value_split_with_wrap("Problemy", problemy_text, ln=True)
    
    if pacjent_data.Problemy_inne:
        pdf.label_value_split_with_wrap("Problemy (inne)", pacjent_data.Problemy_inne, ln=True)
    
    # Long text field - use full width
    pdf.patient_row("Notatka - Diagnoza sytuacji", pacjent_data.Notatka_diagnoza_sytuacji or "---")
    
    zaproponowane_wsparcie = pacjent_data.Zaproponowane_wsparcie
    if zaproponowane_wsparcie and isinstance(zaproponowane_wsparcie, list):
        wsparcie_text = ", ".join(str(x) for x in zaproponowane_wsparcie)
    else:
        wsparcie_text = zaproponowane_wsparcie or "---"
    pdf.label_value_split_with_wrap("Zaproponowane wsparcie", wsparcie_text, width = 190, label_width=65, ln=True)
    
    if pacjent_data.Zaproponowane_wsparcie_inne:
        pdf.label_value_split_with_wrap("Zaproponowane wsparcie (inne)", pacjent_data.Zaproponowane_wsparcie_inne, width = 190, label_width=65, ln=True)

    # ===== NIEBIESKA KARTA =====
    pdf.draw_card_header("Niebieska karta")
    
    pdf.label_value_split_with_wrap("Niebieska karta", "Tak" if pacjent_data.Niebieska_karta else "Nie", ln=False)
    niebieska_inicjator = pacjent_data.Niebieska_karta_inicjator if pacjent_data.Niebieska_karta_inicjator else "---"
    pdf.label_value_split_with_wrap("Inicjator", niebieska_inicjator, ln=True)
    
    pdf.label_value_split_with_wrap("Grupa robocza", "Tak" if pacjent_data.Grupa_robocza else "Nie", ln=False)
    grupa_sklad = pacjent_data.Grupa_robocza_sklad if pacjent_data.Grupa_robocza_sklad else "---"
    pdf.label_value_split_with_wrap("Skład grupy", grupa_sklad, ln=True)
    
    pdf.label_value_split_with_wrap("Plan pomocy", "Tak" if pacjent_data.Plan_pomocy else "Nie", ln=False)
    plan_opis = pacjent_data.Plan_pomocy_opis if pacjent_data.Plan_pomocy_opis else "---"
    pdf.label_value_split_with_wrap("Opis planu", plan_opis, ln=True)
    
    pdf.label_value_split_with_wrap("Narzędzia prawne", "Tak" if pacjent_data.Narzedzia_prawne else "Nie", ln=False)
    pdf.label_value_split_with_wrap("Zawiadomienie", "Tak" if pacjent_data.Zawiadomienie else "Nie", ln=True)

    # ===== POSTĘPOWANIE SĄDOWE =====
    pdf.draw_card_header("Postępowanie sądowe")
    
    pdf.label_value_split_with_wrap("Postępowanie cywilne", "Tak" if pacjent_data.Postepowanie_cywilne else "Nie", ln=False)
    pdf.label_value_split_with_wrap("Postępowanie karne", "Tak" if pacjent_data.Postepowanie_karne else "Nie", ln=True)
    
    pdf.label_value_split_with_wrap("Postępowanie rodzinne", "Tak" if pacjent_data.Postepowanie_rodzinne else "Nie", ln=True)

    # ===== STATUS PACJENTA =====
    pdf.draw_card_header("Status pacjenta")
    
    pdf.label_value_split_with_wrap("Status", pacjent_data.Status_pacjenta or "---", ln=False)
    zakonczenia = pacjent_data.Data_zakonczenia if pacjent_data.Data_zakonczenia else "---"
    pdf.label_value_split_with_wrap("Data zakończenia", zakonczenia, ln=True)
    
    pdf.ln(5)
    
    # Return the bytes
    return pdf.output()

class PacjentListPDF(FPDF):
    def __init__(self, filters_text=None):
        super().__init__(orientation='L') # Landscape is better for tables
        self.add_font('DejaVu', '', 'DejaVuSans.ttf')
        self.add_font('DejaVu', 'B', 'DejaVuSans.ttf')
        self.filters_text = filters_text

    def header(self):
        # Header Bar
        self.set_fill_color(41, 128, 185)
        self.rect(0, 0, 297, 15, 'F') # 297mm for Landscape A4
        self.set_y(5)
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 5, "RAPORT PACJENTÓW - STOWARZYSZENIE OPTA", ln=True, align="C")
        
        # Filters Info
        if self.filters_text:
            self.set_y(17)
            self.set_text_color(100, 100, 100)
            self.set_font("DejaVu", "", 9)
            self.multi_cell(0, 5, f"Filtry: {self.filters_text}")
        
        self.set_text_color(0, 0, 0)
        self.set_y(28)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f"Strona {self.page_no()}/{{nb}}", align="C")


def generate_patient_list_pdf(pacjenci_data, search_term=None, filters=None):
    # TODO - sprawdzić to wszystko
    # 2. Setup PDF
    filter_desc = f"Szukaj: {search_term} | Filtry: {', '.join(filters) if filters else 'Brak'}"
    pdf = PacjentListPDF(filters_text=filter_desc)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 9)

    # 3. Create Table Data
    # The first row is the header
    table_data = [
        ("ID", "Imię", "Nazwisko", "Data zgł.", "Email", "Telefon", "Dzielnica", "Status")
    ]

    for p in pacjenci_data:
        table_data.append((
            str(p.ID_pacjenta),
            str(p.Imie),
            str(p.Nazwisko),
            str(p.Data_zgloszenia),
            str(p.Email or "-"),
            str(p.Telefon or "-"),
            str(p.Dzielnica),
            str(p.Status_pacjenta or "-")
        ))

    # 4. Render Table
    with pdf.table(
        borders_layout="HORIZONTAL_LINES",
        cell_fill_color=(245, 245, 245),
        cell_fill_mode="ROWS",
        line_height=7,
        text_align=("LEFT", "LEFT", "LEFT", "LEFT", "LEFT", "LEFT", "LEFT", "LEFT"),
        width=280 # Total width in Landscape
    ) as table:
        for data_row in table_data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

    # 5. Return Response
    return pdf.output()
