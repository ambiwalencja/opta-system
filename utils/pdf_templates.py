

PDF_TEMPLATE_PACJENT_FORM = """
<html>
<head>
    <style>
        @page { size: a4 portrait; margin: 1cm; }
        body { font-family: Helvetica, sans-serif; font-size: 10pt; }
        h1 { color: #2c3e50; text-align: center; }
        .section { margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .label { font-weight: bold; color: #555; }
        table { width: 100%; }
        td { padding: 5px; }
    </style>
</head>
<body>
    <h1>Karta Pacjenta: {{ p.Imie }} {{ p.Nazwisko }}</h1>
    <div class="section">
        <table>
            <tr>
                <td><span class="label">ID:</span> {{ p.ID_pacjenta }}</td>
                <td><span class="label">Data zgłoszenia:</span> {{ p.Data_zgloszenia }}</td>
            </tr>
            <tr>
                <td><span class="label">Email:</span> {{ p.Email }}</td>
                <td><span class="label">Telefon:</span> {{ p.Telefon }}</td>
            </tr>
            <tr>
                <td><span class="label">Adres:</span> {{ p.Ulica }} {{ p.Nr_domu }}{% if p.Nr_mieszkania %}/{{ p.Nr_mieszkania }}{% endif %}</td>
                <td><span class="label">Kod pocztowy:</span> {{ p.Kod_pocztowy }}</td>
            </tr>
        </table>
    </div>
    <div class="section">
        <h3>Informacje Społeczne</h3>
        <p><span class="label">Wiek:</span> {{ p.Wiek }}</p>
        <p><span class="label">Status zawodowy:</span> {{ p.Status_zawodowy }}</p>
        <p><span class="label">Problemy:</span> {{ p.Problemy }}</p>
    </div>
    <div class="section">
        <h3>Notatka/Diagnoza</h3>
        <p>{{ p.Notatka_diagnoza_sytuacji }}</p>
    </div>
</body>
</html>
"""