import sqlite3
import os


os.remove('tema2.db')

conn = sqlite3.connect('tema2.db')
c = conn.cursor()

c.execute("CREATE TABLE pensiuni (id integer not null unique, nume text not null unique, oras text, descriere text, pret_per_noapte real, stele integer)")
c.execute("INSERT INTO pensiuni VALUES (1, 'Bella Muzica','Brasov','Hotelul Bella Muzica oferă cazare în centrul Braşovului, într-o clădire din secolul al XVI-lea renovată în stil neoclasic. Acesta oferă un restaurant care serveşte preparate mexicane, maghiare şi româneşti.',"\
            "298, 3)")
c.execute("INSERT INTO pensiuni VALUES (2, 'Pensiunea Cardinal','Sibiu','Pensiunea Cardinal este situată în Sibiu, la 1 km de centrul oraşului şi oferă camere în stil clasic cu aer condiţionat şi decorate cu obiecte de design de la începutul secolului al XX-lea.',"\
            "178, 3)")
c.execute("INSERT INTO pensiuni VALUES (3, 'RIN Central Hotel','Bucuresti','Hotelul RIN Central a fost renovat în anul 2011 şi se află în centrul Bucureştiului, la 5 minute de mers cu maşina de Piaţa Unirii. Hotelul oferă camere cu aer condiţionat şi acces gratuit la internet WiFi în toate zonele.',"\
            "336, 4)")
c.execute("INSERT INTO pensiuni VALUES (4, 'Hotel Florentina','Constanta','La numai 500 de metri de gara din Constanţa, Hotelul Florentina oferă camere cu aer condiţionat şi Wi-Fi gratuit. Portul Tomis este situat la 4 km, iar autobuzul public spre plaja Modern opreşte chiar vizavi.',"\
            "114, 2)")


c.execute("CREATE TABLE locatii (id integer not null unique, nume text not null unique, descriere text, distanta real)")
c.execute("INSERT INTO locatii VALUES (1, 'Brasov','Brasov este resedinta si cel mai mare oras al judetului Brasov, Transilvania, Romania. Are o populatie de 283.901 locuitori. Intre 8 septembrie 1950 si 24 decembrie 1960 s-a numit Orasul Stalin, dupa Iosif Stalin, si a fost capitala Regiunii Stalin. A fost declarat municipiu la 17 februarie 1968.',"\
            "307)")
c.execute("INSERT INTO locatii VALUES (2, 'Sibiu','Sibiul, cunoscut si sub denumirea germana Hermannstadt a fost si este unul dintre cele mai reprezentative orase din Romania, atat din punct de vedere turistic, cultural dar si economic. Aici exista cel mai important centru al minoritatii germane din Transilvania, de asemenea si alte minoritati (maghiari, tigani, slovaci si ucrainieni). Desigur, ponderea cea mai mare o are populatia de origine romana (peste 95%), care a stiut sa pastreze si sa imbine celelalte culturi de sus. ',"\
            "412)")
c.execute("INSERT INTO locatii VALUES (3, 'Bucuresti','Bucuresti, Capitala Romaniei este un oras plin de viata, de lumina si in permanenta dezvoltare. A cunoscut multe schimbari, a trecut prin diverse ere si perioade istorice, fiecare lasandu-si amprenta ei aparte in structura orasului, trecand de la cetate (Cetatea Dambovita), la oras la resedinta domneasca, fiind stabilit capitala de catre Vlad Tepes in 1459 apoi trecand prin abdicarea unui rege si sfarsirea unei intregi epoci de regat.',"\
            "389)")
c.execute("INSERT INTO locatii VALUES (4, 'Constanta','Constanta este un oras efervescent, ce imbina istoria milenara cu modernismul. Constanta isi primeste oaspetii cu bratele deschise, cu mult farmec si cu locuri surprinzatoare. Este un oras care celebreaza multiculturalismul, un oras in care civilizatia orientala se intalneste si se impleteste cu cea occidentala pentru a genera un spirit spectaculos si plin de viata.',"\
            "452)")

c.execute("CREATE TABLE gol (id integer , nume text, descriere text, distanta real)")


conn.commit()

conn.close()