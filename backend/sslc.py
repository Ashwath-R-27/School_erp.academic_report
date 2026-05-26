import requests
from bs4 import BeautifulSoup
from db import get_db
import csv

db=get_db()
cursor=db.cursor()

dats=[]

with open('sslc_list.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        dats.append(row)

icou=0

for mem in dats:
    sec=mem[2]
    # Session
    session = requests.Session()

    # Open website first
    main_url = "https://tnresults.nic.in/2026_SSLCtnresults/2026_8022sslc.htm"

    session.get(main_url)

    # Inputs
    reg_no = mem[0]
    dob = mem[1]

    # Result URL
    post_url = "https://tnresults.nic.in/2026_SSLCtnresults/2026_7669sslc.asp"

    # Form data
    payload = {
        "regno": reg_no,
        "dob": dob,
        "B1": "Get Marks"
    }

    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": main_url
    }

    # Submit form
    response = session.post(
        post_url,
        data=payload,
        headers=headers
    )

    # Parse result page
    soup = BeautifulSoup(response.text, "html.parser")

    #Student Name

    name = ""

    first_b = soup.find("b")

    if first_b:
        text = first_b.get_text(strip=True)

        # Remove register number part
        name = text.split("(")[0].strip()

    # Get all rows
    rows = soup.find_all("tr")

    # Store results
    results = []

    j=0

    for row in rows:

        cols = row.find_all("td")

        if len(cols) == 2:

            subject = cols[0].get_text(strip=True).upper()
            mark = cols[1].get_text(strip=True)

            # Skip unwanted rows
            if subject in ["SUBJECT", "TOTAL", "RESULT", "OPTIONAL"]:
                continue

            # Science row fix
            if ")" in mark:
                mark = mark.split(")")[-1].strip()

            # Keep only numbers
            mark = mark.replace("\xa0", "").strip()

            if mark.isdigit():
                results.append(int(mark))

    results.append(sum(results))
    results.insert(0, name)
    results.insert(0, reg_no)
    results.insert(1,sec)

    # Storing marks in DB

    query="INSERT INTO sslc_result VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query,results)
    icou+=1
    if icou%5==0:
        print(icou,"datas saved!")
db.commit()
db.close()
print("All datas have been saved successfully!")