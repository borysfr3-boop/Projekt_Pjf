# Projekt_Pjf
Gra typu Tower Defense
Projekt pomysły:
1. Gra Tower Defense w sci fi Obrona ztsacji kosmiczxnej

Scieżka przeciwników na mapie lewa strona przeciwnicy prawa gracz
Mozliwosc uklepszania wież obronnych z unikalnym drzewkiem umiejetnosci (kilka typow wież obronnych)
Z każdą przebytą falą przeciwnicy mają wyższy lvl i zadają więcej hp
Gracz rozmieszcza systemy obronne wokół wyznaczonej trasy, odpierając kolejne fale wrogich jednostek. 
Celem rozgrywki jest jak najdłuższe utrzymanie stacji przy życiu poprzez efektywne zarządzanie zasobami oraz dobór odpowiednich systemów obronnych.
ZAKRES funkcjonalny w szczegolach
- Mapa z ustaloną trasą przeciwników
- System fal przeciwników o rosnącym poziomie trudności
- Co najmniej 3 typy wież obronnych o różnych parametrach
- System ekonomii: nagrody za zestrzelenia i koszty budowy przy ulepszaniach
- System punktów życia stacji ( regeneruue
- Menu gry i panel informacji (fale, HP, kredyty)
- Zapis najlepszego wyniku (high score)
- System ulepszania wież poprzez ulepszanie poziomu oraz wyboru dodatkowych umiejętności (np. poprzez zdobycie określonego lvl)
wykorzystanie :
- Biblioteka PyGame
- Programowanie obiektowe 
Architektura prpgramu
Moduły:
- Game – sterowanie pętlą gry
- Enemy – przeciwnicy
- Tower – klasa bazowa i podklasy typów wież
- Bullet – obsługa pocisków ( może być różny typ pocisku ten co zadaje więcej hp np)
- Map – definicja ścieżki wrogów
- WaveManager – generacja fal
- UI – menu i HUD
- HighscoreManager – zapis wyników
ALGORYTMY
- Ruch przeciwników po punktach kontrolnych
- Wykrywanie przeciwnika w zasięgu wieży przez obliczanie dystansu
- Strzelanie oparte na czasie odnowienia (cooldown)
- Prosta detekcja kolizji pocisk–wróg
- Algorytm generowania fal wrogów
