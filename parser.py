import requests
from bs4 import BeautifulSoup
import sqlite3

db = sqlite3.connect("/home/pavli/pythonchik/parser/chrome_driver/WRC9.db")
sql = db.cursor()


def get_data(url, a, b, id_series, id_team, id_pilot, id_location, id_record, id_result):

    sql.execute("""CREATE TABLE IF NOT EXISTS series (
        name_series TEXT,
        category TEXT,
        established TEXT,
        current_champion TEXT,
        current_team_champion TEXT,
        lead_series_id TEXT
    )""")
    db.commit()
    sql.execute("""CREATE TABLE IF NOT EXISTS record (
                    position_pilot TEXT, 
                    name_pilot TEXT,
                    championships TEXT,
                    record_id TEXT,
                    lead_series_id TEXT
    )""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS location (
            track_name TEXT,
            date_round TEXT,
            num_round TEXT,
            location_id TEXT,
            lead_series_id TEXT
    )""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS team (
                    name_team TEXT,
                    chassis TEXT,
                    engine TEXT,
                    nums_of_cars TEXT,
                    team_id TEXT,
                    lead_series_id TEXT
    )""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS pilot (
                        name_pilot TEXT,
                        age_pilot TEXT,
                        date_of_birth TEXT,
                        nationality_pilot TEXT,
                        place_of_birth TEXT,
                        pilot_id TEXT,
                        team_id TEXT
    )""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS results (
                            round_res TEXT,
                            date_res TEXT,
                            grand_prix_res TEXT,
                            winner_res TEXT,
                            pole_res TEXT,
                            fastest_lap TEXT,
                            team_res TEXT,
                            res_id TEXT,
                            lead_series_id TEXT
                            
        )""")
    db.commit()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    }
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup)
    name = soup.find(class_="styled__FullName-sc-k520o3-4 gzGznE").text
    name1 = soup.find(class_="styled__ShortName-sc-k520o3-3 knitRy").text
    name = name1+"("+name+")"

    category = soup.find(class_="styled__MainName-sc-k520o3-8 gwCYLB").text
    established = soup.find(class_="styled__MainName-sc-k520o3-8 gwCYLB").next_sibling.next_sibling.text

    current_champion1 = soup.find(class_="styled__NameContainer-sc-k520o3-10 dKXmeJ")
    if current_champion1 == None:
        current_champion = "-"
    else:
        current_champion = soup.find(class_="styled__NameContainer-sc-k520o3-10 dKXmeJ").find("a").text
    current_team_champion1 = soup.find(class_="styled__InfoContainer-sc-k520o3-6 gsLylo").next_sibling.find("a")
    if current_team_champion1 == None:

        current_team_champion = "-"
    else:
        current_team_champion = soup.find(class_="styled__InfoContainer-sc-k520o3-6 gsLylo").next_sibling.find("a").text

        # print(kol_vo," ", name, " ", category," ",established, " ", current_champion, " ", current_team_champion)



    sql.execute("SELECT name_series FROM series")
    sql.execute(f"INSERT INTO series VALUES  (?,?,?,?,?,?)",(name, category, established, current_champion, current_team_champion, id_series))
    db.commit()


    table0 = soup.find(class_="styled__Table-sc-105f2ni-6 dWmtam").find("tbody").find_all("tr")

    pilots = []

    for item in table0:
        car_num = ""
        wrc_tables = item.find_all("td")
        id_team += 1
        name_team = wrc_tables[0].find("span").text
        chassis = wrc_tables[1].find(class_="styled__CarNameWrapper-sc-105f2ni-4 dCWQje").find("span").text
        engine = wrc_tables[2].find(class_="styled__CarNameWrapper-sc-105f2ni-4 dCWQje").find("span").text
        cars_nums = wrc_tables[3].find(class_="styled__DriverCell-sc-105f2ni-2 gXQhvd").find_all("span")
        for item in cars_nums:
            car_num =car_num + item.text + " "
        sql.execute("SELECT name_team FROM team")
        sql.execute(f"INSERT INTO team VALUES  (?,?,?,?,?,?)", (name_team, chassis, engine,car_num, id_team, id_series))
        db.commit()
        pilot_table = wrc_tables[4].find_all("a")

        for item in pilot_table:
            id_pilot +=1
            pilots_url = ("https://motorsportstats.com" + item.get("href"))
            r = requests.get(pilots_url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            name_pilot = soup.find(class_="styled__Name-sc-ixlir0-2 fMmlCh").text
            nationality_pilot = soup.find(class_="styled__NameContainer-sc-ixlir0-5 bLjImC").find(class_="styled__MainName-sc-ixlir0-6 iUZQpw").text
            age_pilot = soup.find(class_="styled__PersonalInfoContainer-sc-ixlir0-12 cINzcH").next_sibling.find(class_="styled__MainName-sc-ixlir0-6 iUZQpw").text
            date_of_birth = soup.find(class_="styled__PersonalInfoContainer-sc-ixlir0-12 cINzcH").find(class_="styled__MainName-sc-ixlir0-6 iUZQpw").text
            place_of_birth = soup.find(class_="styled__PersonalInfoContainer-sc-ixlir0-12 cINzcH").find(class_="styled__MainName-sc-ixlir0-6 iUZQpw").next_sibling.next_sibling.text
            sql.execute("SELECT age_pilot FROM pilot")
            sql.execute(f"INSERT INTO pilot VALUES  (?,?,?,?,?,?,?)", (name_pilot, age_pilot,date_of_birth ,nationality_pilot, place_of_birth,id_pilot ,id_team))
            db.commit()
            #print(name_pilot, "  ", nationality_pilot, "  ", age_pilot, "  ", date_of_birth, "  ", place_of_birth)

    r = requests.get("https://motorsportstats.com/series/"+a+"/calendar/"+b, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find(class_="styled__TableContainer-sc-w4o42v-0 eslyjF").find("tbody").find_all("tr")
    for item in table:
        wrc_tables = item.find_all("td")
        id_location += 1
        round_ser = wrc_tables[0].text
        date = wrc_tables[1].text
        track = wrc_tables[2].find(class_="styled__VenueName-sc-s1tixx-3 jiA-DdQ").find("a").text
        sql.execute("SELECT track_name FROM location")
        sql.execute(f"INSERT INTO location VALUES  (?,?,?,?,?)", (track, date, round_ser, id_location, id_series))
        db.commit()

    r = requests.get("https://motorsportstats.com/series/"+a+"/records/"+b, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    table1 = soup.find(class_="styled__Table-sc-6rpvqu-2 hcWsWV").find("tbody").find_all("tr")
    for item in table1:
        wrc_tables1 = item.find_all("td")
        id_record += 1
        position_pilot = wrc_tables1[0].text

        name_pilot = wrc_tables1[2].find("span").text
        championships = wrc_tables1[3].text
        sql.execute("SELECT championships FROM record")
        sql.execute(f"INSERT INTO record VALUES  (?,?,?,?,?)", (position_pilot,name_pilot, championships, id_record, id_series))
        db.commit()

    r = requests.get("https://motorsportstats.com/series/" + a + "/results/" + b, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    table1 = soup.find(class_="styled__TableContainer-sc-1ifs93o-0 idZIyZ").find("tbody").find_all("tr")
    for item in table1:
        wrc_tables1 = item.find_all("td")
        id_result += 1
        round_res = wrc_tables1[0].text
        date_res = wrc_tables1[1].text
        grand_prix_res =wrc_tables1[2].find(class_="styled__Title-sc-qls9tw-0 eKflDO").text
        winner_res = wrc_tables1[3].find(class_="styled__Title-sc-qls9tw-0 eKflDO").text
        pole_res = wrc_tables1[4].find(class_="styled__Title-sc-qls9tw-0 eKflDO").text
        fastest_lap = wrc_tables1[5].find(class_="styled__Title-sc-qls9tw-0 eKflDO").text
        #fastest_lap="-"
        team_res = wrc_tables1[5].find(class_="styled__Title-sc-qls9tw-0 eKflDO").text

        sql.execute("SELECT round_res FROM results")
        sql.execute(f"INSERT INTO results VALUES  (?,?,?,?,?,?,?,?,?)", (round_res, date_res, grand_prix_res, winner_res, pole_res,fastest_lap,team_res,id_result,id_series))
        db.commit()

a="imsa-sportscar-championship"
b="2022"
id_serie=38
id_team=261
id_pilot=712
id_location=239
id_record=414
id_result=189
get_data("https://motorsportstats.com/series/"+a+"/summary/"+b, a, b, id_serie, id_team, id_pilot, id_location, id_record, id_result)
