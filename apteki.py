import os
import time
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
class Apteka:
    def __init__(self, id_kamsoft, nazwa, sciezka):
        self.id_kamsoft = id_kamsoft
        self.nazwa = nazwa
        self.sciezka = sciezka

    def __str__(self):
        return f"Apteka: ID Kamsoft - {self.id_kamsoft}, Nazwa - {self.nazwa}, Ścieżka - {self.sciezka}"

class KatalogAptek:
    def __init__(self):
        self.apteki = []

    def dodaj_apteke(self, apteka):
        self.apteki.append(apteka)

    def znajdz_apteke_po_id(self, id_kamsoft):
        for apteka in self.apteki:
            if apteka.id_kamsoft == id_kamsoft:
                return apteka
        return None

    def wyswietl_apteki(self):
        scieszki_do_sprawdzenia = []
        id_apteki = []
        nazwa = []
        for apteka in self.apteki:
            scieszki_do_sprawdzenia.append(apteka.sciezka)
            id_apteki.append(apteka.id_kamsoft)
        return scieszki_do_sprawdzenia, id_apteki, nazwa

    def zapisz_do_pliku(self, nazwa_pliku):
        with open(nazwa_pliku, "w") as plik:
            for apteka in self.apteki:
                plik.write(f"{apteka.id_kamsoft},{apteka.nazwa},{apteka.sciezka}\n")

    def sprawdz_plik(self, sciezka_katalogu):
        dzisiejsza_data = datetime.date.today()
        wynik = []
        for plik in os.listdir(sciezka_katalogu):
            pelna_sciezka_pliku = os.path.join(sciezka_katalogu, plik)
            if os.path.isfile(pelna_sciezka_pliku):
                data_modyfikacji = datetime.date.fromtimestamp(os.path.getmtime(pelna_sciezka_pliku))
                rozmiar_pliku = os.path.getsize(pelna_sciezka_pliku)
                if data_modyfikacji == dzisiejsza_data and rozmiar_pliku > 10:
                    wynik.append(
                        f"Plik '{plik}' Rozmiar: {rozmiar_pliku} spełnia warunki: data dzisiejsza i rozmiar > 20 bajtów")
        if wynik:  # Jeśli wynik zawiera elementy, to zwracamy listę z wynikami
            return wynik
        else:
            return [
                'Brak']  # Jeśli wynik jest pusty, zwracamy listę z informacją o braku pasujących plików

    def kasowanie_starych_plikow(self, sciezka_katalogu, maksymalny_wiek_dni=60):
        try:
            teraz = datetime.date.today()
            for plik in os.listdir(sciezka_katalogu):
                sciezka_pliku = os.path.join(sciezka_katalogu, plik)
                if os.path.isfile(sciezka_pliku):
                    data_modyfikacji = datetime.date.fromtimestamp(os.path.getmtime(sciezka_pliku))
                    roznica = teraz - data_modyfikacji
                    if roznica.days > maksymalny_wiek_dni:
                        os.remove(sciezka_pliku)
        except Exception as e:
            print(f"Błąd podczas usuwania starych plików: {str(e)}")
    def wczytaj_z_pliku(self, nazwa_pliku):
        self.apteki = []  # Wyczyść istniejącą listę aptek

        try:
            with open(nazwa_pliku, "r") as plik:
                for linia in plik:
                    dane_apteki = linia.strip().split(',')
                    if len(dane_apteki) == 3:
                        id_kamsoft, nazwa, sciezka = map(str.strip, dane_apteki)
                        apteka = Apteka(int(id_kamsoft), nazwa, sciezka)
                        self.dodaj_apteke(apteka)
                    else:
                        print(f"Błąd w linii: {linia}. Pomijanie tej linii.")
        except FileNotFoundError:
            print(f"Plik {nazwa_pliku} nie istnieje.")




    def wyslij_email(self, tworz_komunikat, lp):
        komunikat = ('')

        with open("wynik_do_wyslania.txt", "w") as plik:
            # Iterujemy przez elementy zbioru i zapisujemy je do pliku
            for element in tworz_komunikat:
                plik.write(element + "\n")  # Dodajemy znak nowej linii po każdym elemencie
            lp = str(lp)
            plik.write(lp + "\n")
        # Otwarcie pliku "wynik_do_wyslania.txt" i odczytanie jego zawartości
        with open('wynik_do_wyslania.txt', 'r') as plik:
            komunikat = plik.read()


        # Dane konta e-mail nadawcy
        nadawca_email = 'raporty_klient@poczta.pl'
        nadawca_haslo = 'Practel123'

        # Dane konta e-mail odbiorcy
        odbiorca_email = 'practel@gmail.com'

        # Tworzenie wiadomości e-mail
        wiadomosc = MIMEMultipart()
        wiadomosc['From'] = nadawca_email
        wiadomosc['To'] = odbiorca_email
        wiadomosc['Subject'] = 'Raport z wysylania kopii recept'

        tresc = komunikat
        wiadomosc.attach(MIMEText(tresc, 'plain'))

        # Nawiązanie połączenia z serwerem SMTP
        serwer_smtp = smtplib.SMTP('smtp.poczta.pl', 587)
        serwer_smtp.starttls()
        serwer_smtp.login(nadawca_email, nadawca_haslo)

        # Wysłanie wiadomości e-mail
        serwer_smtp.sendmail(nadawca_email, odbiorca_email, wiadomosc.as_string())
        logowanie_zdarzen(zdarzenie=' - wyslano e-maila')
        # Zamknięcie połączenia
        serwer_smtp.quit()

# Funkcje w programie
def sprawdzam_niewyslane_recepty(katalog):
    logowanie_zdarzen(zdarzenie=' - niewyslane recepty sprawdzenie rozpoczete')
    sciezka = katalog.wyswietl_apteki()[0]
    zestawienie_aptek = {}
    for s in sciezka:
        sciezka_katalogu = s
        x = str(katalog.sprawdz_plik(sciezka_katalogu))
        d1 = {s: x}
        zestawienie_aptek.update(d1)
    lp = 0
    tworz_komunikat = set()

    # Szukam wartosci
    for klucz, wartosc in zestawienie_aptek.items():
        z = str(wartosc)
        y = str("['Brak']")
        if z == y:
            lp = lp + 1
            tworz_komunikat.add(f'Brak przesyłania recept w katalogu: {klucz}')
    logowanie_zdarzen(zdarzenie=' - niewyslane recepty sprawdzenie zakonczone')
    katalog.wyslij_email(tworz_komunikat, lp)
def kasuje_nadmiarowe_recepty():
    logowanie_zdarzen(zdarzenie=' - kasuje nadmiarowe recepty rozpoczete')
    sciezka = katalog.wyswietl_apteki()[0]
    zestawienie_aptek = {}
    for s in sciezka:
        sciezka_katalogu = s
        x = katalog.kasowanie_starych_plikow(sciezka_katalogu, maksymalny_wiek_dni=100)
        d1 = {s: x}
        zestawienie_aptek.update(d1)
    logowanie_zdarzen(zdarzenie=' - kasuje nadmiarowe recepty zakonczone')
def sprawdzam_wyslane_recepty():
    logowanie_zdarzen(zdarzenie=' - wyslane recepty sprawdzenie rozpoczete')
    sciezka = katalog.wyswietl_apteki()[0]
    zestawienie_aptek = {}
    for s in sciezka:
        sciezka_katalogu = s
        x = str(katalog.sprawdz_plik(sciezka_katalogu))
        d1 = {s: x}
        zestawienie_aptek.update(d1)
    lp = 0
    tworz_komunikat = set()
    for klucz, wartosc in zestawienie_aptek.items():
        z = str(wartosc)
        y = str("['Brak']")
        if z != y:
            lp = lp + 1
            tworz_komunikat.add(f'Jest OK w katalogu: {klucz}')
    logowanie_zdarzen(zdarzenie=' - wyslane recepty sprawdzenie zakonczone')
    katalog.wyslij_email(tworz_komunikat, lp)


def logowanie_zdarzen (zdarzenie):
    with open("wynik_do_wyslania.log", "a") as logi:
        teraz = datetime.datetime.now()
        teraz = str(teraz.strftime("%Y-%m-%d %H:%M:%S"))
        logi.write(teraz + zdarzenie + '\n')
def wczytaj_parametry(nazwa_pliku):
    try:
        with open(nazwa_pliku, 'r') as plik:
            for linia in plik:
                czesci = linia.split(',')
                if len(czesci) == 2:
                    godzina_testu, dzien_tygodnia = czesci
        return godzina_testu, dzien_tygodnia
    except FileNotFoundError:
        print(f"Plik {nazwa_pliku} nie istnieje.")
def petla_nieskonczona(start, dzien_tygodnia):
    while True:
        time.sleep(0.5)
        dzisiejsza_data_i_godzina = datetime.datetime.now()
        godzina = dzisiejsza_data_i_godzina.strftime("%H:%M:%S")
        numer_dnia_tygodnia = dzisiejsza_data_i_godzina.weekday()

        if godzina == start:
            sprawdzam_niewyslane_recepty()
            if numer_dnia_tygodnia == dzien_tygodnia:
                sprawdzam_wyslane_recepty()
                kasuje_nadmiarowe_recepty()



# Program do weryfikacji wysyłania recept
if __name__ == "__main__":

    logowanie_zdarzen(zdarzenie=' - uruchomienie programu')
    katalog1 = KatalogAptek()
    katalog1.wczytaj_z_pliku('apteki.txt')
    parametry_pobrane = wczytaj_parametry('dane.ini')
    # 0 - godzina startu 1 dzień tygodnia
    # petla_nieskonczona(parametry_pobrane[0], parametry_pobrane[1])
    print("123")
    sprawdzam_niewyslane_recepty(katalog1)
    time.sleep(5)
    #
    # while True:
    #     print('1 - Sprawdz apteki')
    #     print('2 - Kasuj nadmiarowe recepty')
    #     print('3 - Sprawdz apteki OK')
    #     print('4- Petla nieskonczona')
    #     print('5- Wyświetl apteki')
    #     wybor = input(f'Podaj opcje: ')
    #     if wybor == '0':
    #         break
    #     elif wybor == '1':
    #         sprawdzam_niewyslane_recepty()
    #     elif wybor == '2':
    #         kasuje_nadmiarowe_recepty()
    #     elif wybor == '3':
    #         sprawdzam_wyslane_recepty()
    #     elif wybor == '4':
    #         petla_nieskonczona(parametry_pobrane[0], parametry_pobrane[1])
    #     elif wybor == '5':
    #         print(katalog.wyswietl_apteki()[0])

