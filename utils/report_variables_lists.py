single_choice_fields = [
    "Dzielnica",
    "Wyksztalcenie",
    "Plec",
    "Status_zawodowy",
    "Stan_cywilny",
    "Zrodlo_informacji",
    "Placowka_kierujaca",
    "Niebieska_karta",
    "Grupa_robocza",
    "Plan_pomocy",
    "Narzedzia_prawne",
    "Zawiadomienie",
    "Postepowanie_cywilne",
    "Postepowanie_karne",
    "Postepowanie_rodzinne",
    "Liczba_dzieci",
    "Ewaluacja",
    "Status_pacjenta"
]

multiple_choice_fields = [
    "Korzystanie_z_pomocy",
    "Problemy",
    "Zaproponowane_wsparcie"
]

text_fields = [
    "Korzystanie_z_pomocy_inne",
    "Placowka_kierujaca_inne",
    # "Niebieska_karta_inicjator",
    # "Grupa_robocza_sklad",
    # "Plan_pomocy_opis",
    "Problemy_inne",
    "Zaproponowane_wsparcie_inne",
    "Zrodlo_informacji_inne"
]

zaproponowane_wsparcie_indywidualne_options = [
        "działania informacyjno-konsultacyjne",
        "konsultacje prawne",
        "konsultacje pedagogiczne",
        "konsultacje psychologiczne",
        "pomoc psychologiczna",
        "inne - konsylium psycholog/prawnik",
        "inne - pomoc 'adwokata socjalnego'",
        "inne - konsultacje do grupy wsparcia",
        "inne - konsultacje do grupy rozwojowej"
]

zaproponowane_wsparcie_grupowe_options = [
        "grupa wsparcia",
        "warsztat, trening",
        "inne - grupa o charakterze rozwojowym."
]

korzystanie_z_pomocy_options = [
        "ośrodek pomocy społecznej",
        "poradnia psych-pedagogiczna",
        "poradnia rodzinna",
        "poradnia odwykowa/DZRPA",
        "placówka ochrony zdrowia",
        "organizacja pozarządowa",
        "w ramach tej samej placówki",
        "inne - jakie?"
]

typ_wizyty_options = {
        "specjalista ds. przeciwdziałania przemocy": 1,
        "adwokat socjalny": 1,
        "psycholog - konsultacja diagnostyczna": 1,
        "psycholog - konsultacja rodzicielska": 1,
        "prawnik - konsultacja / porada prawna": 1,
        "psycholog/terapeuta - wsparcie": 1,
        "konsultacje do grupy wsparcia i do grupy rozwojowej": 1,
        'indywidualne konsultacje w zespole psycholog-prawnik': 2,
        'indywidualne konsultacje do grupy trening antystresowy 2020': 1
}

WIZYTY_RANGES = [
        ("1-3", 3),
        ("4-20", 20),
        ("21+", float('inf'))
    ]

HOURS_RANGES = [
        ("1-3", 3),
        ("4-10", 10),
        ("11-20", 20),
        ("21+", float('inf'))
    ]

AGE_GROUPS = {
        '18-25': (18, 25),
        '26-35': (26, 35),
        '36-45': (36, 45),
        '46-55': (46, 55),
        '56+': (56, 150)
    }