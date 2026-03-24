from fpdf import FPDF

class PatientPDF(FPDF):
    def __init__(self):
        super().__init__()
        # 1. Register the Unicode-compatible font
        # Make sure DejaVuSans.ttf is in your project folder!
        self.add_font('DejaVu', '', 'DejaVuSans.ttf')
        self.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf') # For bold versions

    # def header(self):
    #     self.set_font("DejaVu", "B", 15)
    #     self.cell(0, 10, "KARTA PACJENTA", border=True, ln=True, align="C")
    #     self.ln(5)

    def header(self):
        # Top "Bar" like a web header
        self.set_fill_color(41, 128, 185)  # Nice Blue
        self.rect(0, 0, 210, 30, 'F') 
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 16)
        self.cell(0, 10, "SYSTEM REJESTRACJI PACJENTÓW", ln=True, align="C")
        self.set_text_color(0, 0, 0)
        self.ln(15)

    def draw_card_header(self, title):
        """Creates a section header that looks like a web card header"""
        self.set_font("DejaVu", "B", 11)
        self.set_fill_color(245, 245, 245)
        self.cell(0, 10, f"  {title}", ln=True, fill=True)
        self.set_draw_color(200, 200, 200)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(2)

    def label_value_split(self, label, value, width=95, ln=False):
        """Creates a key-value pair. Two of these fit on one line (190mm total)"""
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(25, 8, f"{label}: ", ln=False)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(0, 0, 0)
        self.cell(width - 25, 8, str(value) if value else "---", ln=ln)

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
    
    pdf.label_value_split("Imię i nazwisko", f'{pacjent_data.Imie} {pacjent_data.Nazwisko}', ln=False)
    pdf.label_value_split("ID Pacjenta", pacjent_data.ID_pacjenta, ln=True)
    
    pdf.label_value_split("Płeć", pacjent_data.Plec or "---", ln=False)
    pdf.label_value_split("Wiek", pacjent_data.Wiek or "---", ln=True)
    
    pdf.label_value_split("Stan cywilny", pacjent_data.Stan_cywilny or "---", ln=False)
    pdf.label_value_split("Wykształcenie", pacjent_data.Wyksztalcenie or "---", ln=True)
    
    pdf.label_value_split("Liczba dzieci", pacjent_data.Liczba_dzieci or "---", ln=False)
    pdf.label_value_split("Status zawodowy", pacjent_data.Status_zawodowy or "---", ln=True)
    
    pdf.label_value_split("Email", pacjent_data.Email or "---", ln=False)
    pdf.label_value_split("Telefon", pacjent_data.Telefon or "---", ln=True)
    
    pdf.label_value_split("Dzielnica", pacjent_data.Dzielnica or "---", ln=False)
    pdf.label_value_split("Ulica", pacjent_data.Ulica or "---", ln=True)
    
    address_parts = []
    if pacjent_data.Nr_domu:
        address_parts.append(f"nr {pacjent_data.Nr_domu}")
    if pacjent_data.Nr_mieszkania:
        address_parts.append(f"m. {pacjent_data.Nr_mieszkania}")
    address = ", ".join(address_parts) if address_parts else "---"
    pdf.label_value_split("Nr domu/mieszkania", address, ln=False)
    pdf.label_value_split("Kod pocztowy", pacjent_data.Kod_pocztowy or "---", ln=True)

    # ===== INFORMACJE O ZGŁOSZENIU =====
    pdf.draw_card_header("Informacje o zgłoszeniu")
    
    pdf.label_value_split("Data zgłoszenia", pacjent_data.Data_zgloszenia or "---", ln=False)
    pdf.label_value_split("Data ostatniej wizyty", pacjent_data.Data_ostatniej_wizyty or "---", ln=True)
    
    pdf.label_value_split("Źródło informacji", pacjent_data.Zrodlo_informacji or "---", ln=True)
    if pacjent_data.Zrodlo_informacji_inne:
        pdf.label_value_split("Źródło informacji (inne)", pacjent_data.Zrodlo_informacji_inne, ln=True)
    
    pdf.label_value_split("Placówka kierująca", pacjent_data.Placowka_kierujaca or "---", ln=True)
    if pacjent_data.Placowka_kierujaca_inne:
        pdf.label_value_split("Placówka kierująca (inne)", pacjent_data.Placowka_kierujaca_inne, ln=True)
    
    korzystanie_z_pomocy = pacjent_data.Korzystanie_z_pomocy
    if korzystanie_z_pomocy and isinstance(korzystanie_z_pomocy, list):
        korzystanie_text = ", ".join(str(x) for x in korzystanie_z_pomocy)
    else:
        korzystanie_text = korzystanie_z_pomocy or "---"
    pdf.label_value_split("Korzystanie z pomocy", korzystanie_text, ln=True)
    
    if pacjent_data.Korzystanie_z_pomocy_inne:
        pdf.label_value_split("Korzystanie z pomocy (inne)", pacjent_data.Korzystanie_z_pomocy_inne, ln=True)

    # ===== DIAGNOZA I PLAN POMOCY =====
    pdf.draw_card_header("Diagnoza i plan pomocy")
    
    problemy = pacjent_data.Problemy
    if problemy and isinstance(problemy, list):
        problemy_text = ", ".join(str(x) for x in problemy)
    else:
        problemy_text = problemy or "---"
    pdf.label_value_split("Problemy", problemy_text, ln=True)
    
    if pacjent_data.Problemy_inne:
        pdf.label_value_split("Problemy (inne)", pacjent_data.Problemy_inne, ln=True)
    
    # Long text field - use full width
    pdf.patient_row("Notatka - Diagnoza sytuacji", pacjent_data.Notatka_diagnoza_sytuacji or "---")
    
    zaproponowane_wsparcie = pacjent_data.Zaproponowane_wsparcie
    if zaproponowane_wsparcie and isinstance(zaproponowane_wsparcie, list):
        wsparcie_text = ", ".join(str(x) for x in zaproponowane_wsparcie)
    else:
        wsparcie_text = zaproponowane_wsparcie or "---"
    pdf.label_value_split("Zaproponowane wsparcie", wsparcie_text, ln=True)
    
    if pacjent_data.Zaproponowane_wsparcie_inne:
        pdf.label_value_split("Zaproponowane wsparcie (inne)", pacjent_data.Zaproponowane_wsparcie_inne, ln=True)

    # ===== NIEBIESKA KARTA =====
    pdf.draw_card_header("Niebieska karta")
    
    pdf.label_value_split("Niebieska karta", "Tak" if pacjent_data.Niebieska_karta else "Nie", ln=False)
    niebieska_inicjator = pacjent_data.Niebieska_karta_inicjator if pacjent_data.Niebieska_karta_inicjator else "---"
    pdf.label_value_split("Inicjator", niebieska_inicjator, ln=True)
    
    pdf.label_value_split("Grupa robocza", "Tak" if pacjent_data.Grupa_robocza else "Nie", ln=False)
    grupa_sklad = pacjent_data.Grupa_robocza_sklad if pacjent_data.Grupa_robocza_sklad else "---"
    pdf.label_value_split("Skład grupy", grupa_sklad, ln=True)
    
    pdf.label_value_split("Plan pomocy", "Tak" if pacjent_data.Plan_pomocy else "Nie", ln=False)
    plan_opis = pacjent_data.Plan_pomocy_opis if pacjent_data.Plan_pomocy_opis else "---"
    pdf.label_value_split("Opis planu", plan_opis, ln=True)
    
    pdf.label_value_split("Narzędzia prawne", "Tak" if pacjent_data.Narzedzia_prawne else "Nie", ln=False)
    pdf.label_value_split("Zawiadomienie", "Tak" if pacjent_data.Zawiadomienie else "Nie", ln=True)

    # ===== POSTĘPOWANIE SĄDOWE =====
    pdf.draw_card_header("Postępowanie sądowe")
    
    pdf.label_value_split("Postępowanie cywilne", "Tak" if pacjent_data.Postepowanie_cywilne else "Nie", ln=False)
    pdf.label_value_split("Postępowanie karne", "Tak" if pacjent_data.Postepowanie_karne else "Nie", ln=True)
    
    pdf.label_value_split("Postępowanie rodzinne", "Tak" if pacjent_data.Postepowanie_rodzinne else "Nie", ln=True)

    # ===== STATUS PACJENTA =====
    pdf.draw_card_header("Status pacjenta")
    
    pdf.label_value_split("Status", pacjent_data.Status_pacjenta or "---", ln=False)
    zakonczenia = pacjent_data.Data_zakonczenia if pacjent_data.Data_zakonczenia else "---"
    pdf.label_value_split("Data zakończenia", zakonczenia, ln=True)
    
    pdf.ln(5)
    
    # Return the bytes
    return pdf.output()


