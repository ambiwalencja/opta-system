from db_models.config import PossibleValues
from sqlalchemy.orm.session import Session

def populate_possible_values(db: Session):

    # Data to insert
    data = [
        {"Variable_ID": 1, "Variable_name": "Dzielnica", "Variable_label": "Dzielnica", "Possible_values": {
            "Bemowo": "radio",
            "Białołęka": "radio",
            "Bielany": "radio",
            "Mokotów": "radio",
            "Ochota": "radio",
            "Praga-Południe": "radio",
            "Praga-Północ": "radio",
            "Rembertów": "radio",
            "Śródmieście": "radio",
            "Targówek": "radio",
            "Ursus": "radio",
            "Ursynów": "radio",
            "Wawer": "radio",
            "Wesoła": "radio",
            "Wilanów": "radio",
            "Włochy": "radio",
            "Wola": "radio",
            "Żoliborz": "radio"
            }},
        {"Variable_ID": 2, "Variable_name": "Status_zawodowy", "Variable_label": "Status zawodowy", "Possible_values": {
            "pracujący": "radio",
            "prowadzący działalność gospodarczą": "radio",
            "bezrobotny": "radio",
            "na urlopie macierzyńskim/wychowawczym": "radio",
            "na emeryturze/rencie": "radio",
            "pobierający zasiłek (np. z pomocy społecznej)": "radio",
            "uczący się": "radio"
            }},
        {"Variable_ID": 3, "Variable_name": "Stan_cywilny", "Variable_label": "Stan cywilny", "Possible_values": {
            "panna / kawaler": "radio",
            "mężatka / żonaty": "radio",
            "rozwiedziona/y / w separacji": "radio",
            "wdowa / wdowiec": "radio",
            "konkubinat": "radio"
            }},
        {"Variable_ID": 4, "Variable_name": "Wyksztalcenie", "Variable_label": "Wykształcenie", "Possible_values": {
            "podstawowe": "radio",
            "gimnazjalne": "radio",
            "ponadgimnazjalne": "radio",
            "zasadnicze zawodowe": "radio",
            "licencjat/inżynier": "radio",
            "wyższe pełne": "radio"
            }},
        {"Variable_ID": 5, "Variable_name": "Plec", "Variable_label": "Płeć", "Possible_values": {
            "Kobieta": "radio",
            "Mężczyzna": "radio"
            }},
        {"Variable_ID": 6, "Variable_name": "Zrodlo_informacji", "Variable_label": "Skąd klient dowiedział się o możliwości wsparcia udzielanego przez organizację?", "Possible_values": {
            "od znajomej/ego": "radio",
            "od rodziny": "radio",
            "z Internetu": "radio",
            "z instytucji": "radio",
            "z innej organizacji pozarządowej": "radio",
            "z ulotki": "radio",
            "ze spotkania informacyjnego": "radio",
            "z zespołu interdyscyplinarnego/grupy roboczej": "radio",
            "z innego źródła (podać jakie)": "input"
            }},
        {"Variable_ID": 7, "Variable_name": "Korzystanie_z_pomocy", "Variable_label": "Czy klient korzysta obecnie z pomocy następujących podmiotów?", "Possible_values": {
            "ośrodek pomocy społecznej": "checkbox",
            "poradnia psych-pedagogiczna": "checkbox",
            "poradnia rodzinna": "checkbox",
            "poradnia odwykowa/DZRPA": "checkbox",
            "placówka ochrony zdrowia": "checkbox",
            "organizacja pozarządowa": "checkbox",
            "w ramach tej samej placówki": "checkbox",
            "inne - jakie?": "input"
            }},
        {"Variable_ID": 8, "Variable_name": "Placowka_kierujaca", "Variable_label": "Czy i kto skierował klienta do placówki pomocowej?", "Possible_values": {
            "zespół interdyscyplinarny/grupa robocza": "radio",
            "ośrodek pomocy społecznej": "radio",
            "poradnia PP": "radio",
            "sąd/kurator": "radio",
            "poradnia uzależnień": "radio",
            "inna placówka ochrony zdrowia": "radio",
            "inna organizacja pozarządowa": "radio",
            "ta sama organizacja pozarządowa": "radio",
            "z własnej inicjatywy": "radio",
            "inne - jakie?": "input"
            }},
        {"Variable_ID": 9, "Variable_name": "Niebieska_karta", "Variable_label": "Czy jest realizowana Procedura Niebieskiej Karty?", "Possible_values": {
            "Tak": "radio",
            "Nie": "radio"
            }},
        {"Variable_ID": 10, "Variable_name": "Grupa_robocza", "Variable_label": "Czy jest grupa robocza?", "Possible_values": {
            "Tak": "radio",
            "Nie": "radio"
            }},
        {"Variable_ID": 11, "Variable_name": "Plan_pomocy", "Variable_label": "Czy jest indywidualny plan pomocy?", "Possible_values": {
            "Tak": "radio",
            "Nie": "radio"
            }},
        {"Variable_ID": 12, "Variable_name": "Narzedzia_prawne", "Variable_label": "Czy zastosowano prawne narzędzia izolacji osoby stosującej przemoc od pokrzywdzonych?", "Possible_values": {
            "Tak": "radio",
            "Nie": "radio"
            }},
        {"Variable_ID": 13, "Variable_name": "Zawiadomienie", "Variable_label": "Czy złożono zawiadomienie o przestępstwie?", "Possible_values": {
            "Tak": "radio",
            "Nie": "radio"
            }},
        {"Variable_ID": 14, "Variable_name": "Postepowanie_cywilne", "Variable_label": "Czy toczy się postępowanie przed sądem cywilnym?", "Possible_values": {
            "Tak": "radio",
            "Nie": "radio"
            }},
        {"Variable_ID": 15, "Variable_name": "Postepowanie_karne", "Variable_label": "Czy toczy się postępowanie przed sądem karnym?", "Possible_values": {
            "Tak": "radio",
            "Nie": "radio"
            }},
        {"Variable_ID": 16, "Variable_name": "Postepowanie_rodzinne", "Variable_label": "Czy toczy się postępowanie przed sądem rodzinnym?", "Possible_values": {
            "Tak": "radio",
            "Nie": "radio"
            }},
        {"Variable_ID": 17, "Variable_name": "Problemy", "Variable_label": "Z jakim problemem klient zgłosił się do poradni?", "Possible_values": {
            "przemoc fizyczna": "checkbox",
            "przemoc psychiczna": "checkbox",
            "przemoc seksualna": "checkbox",
            "przemoc ekonomiczna": "checkbox",
            "zaniedbanie": "checkbox",
            "problemy opiekuńczo-wychowawcze": "checkbox",
            "uzależnienia": "checkbox",
            "problemy materialno-bytowe": "checkbox",
            "niepełnosprawność/choroba": "checkbox",
            "sprawy okołorozwodowe": "checkbox",
            "inne - jakie?": "input"
            }},
        {"Variable_ID": 18, "Variable_name": "Zaproponowane_wsparcie", "Variable_label": "Rodzaj/forma zaproponowanego wsparcia:", "Possible_values": {
            "działania informacyjno-konsultacyjne": "checkbox",
            "konsultacje prawne": "checkbox",
            "konsultacje pedagogiczne": "checkbox",
            "konsultacje psychologiczne": "checkbox",
            "pomoc psychologiczna": "checkbox",
            "grupa wsparcia": "checkbox",
            "warsztat, trening": "checkbox",
            "inne - konsylium psycholog/prawnik": "checkbox",
            "inne - pomoc 'adwokata socjalnego'": "checkbox",
            "inne - konsultacje do grupy wsparcia": "checkbox",
            "inne - konsultacje do grupy rozwojowej": "checkbox",
            "inne - grupa o charakterze rozwojowym.": "checkbox",
            "inne - jakie?": "input"
            }},
        {"Variable_ID": 19, "Variable_name": "Ewaluacja", "Variable_label": "Czy klient wyraził zgodę na udział w badaniu ewaluacyjnym?", "Possible_values": {
            "Tak": "radio",
            "Nie": "radio"
            }},
        {"Variable_ID": 20, "Variable_name": "Status_pacjenta", "Variable_label": "Status klienta w organizacji:", "Possible_values": {
            "przekierowanie do innej placówki": "radio",
            "aktywny, klient w kontakcie": "radio",
            "zakończona pomoc": "radio",
            "rezygnacja": "radio",
            "kontakt zawieszony": "radio",
            "klient powracający": "radio"
            }},
        {"Variable_ID": 21, "Variable_name": "Typ_grupy", "Variable_label": "Typ grupy", "Possible_values": {
            "grupa wsparcia": "radio",
            "warsztat / trening": "radio",
            "grupa rozwojowa": "radio"
            }},
    ]

    # Insert data
    for item in data:
        possible_value = PossibleValues(**item)
        db.add(possible_value)

    db.commit()
    db.close()

# Call the function to populate the table
# populate_possible_values()
