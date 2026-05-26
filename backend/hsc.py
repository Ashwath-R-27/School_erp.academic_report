import requests
from bs4 import BeautifulSoup
from db import get_db
import csv

db=get_db()
cursor=db.cursor()
dats=[]

with open('hsc_list.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        dats.append(row)

icou=0

for mem in dats:

    # Session
    session = requests.Session()

    # Open website first
    main_url = "https://tnresults.nic.in/2026_HSCtnresults/2026_5341hsc.htm"

    session.get(main_url)

    # Inputs
    reg_no = mem[0]
    dob = mem[1]
    sec=mem[2]
    grp=mem[3]

    # Result URL
    post_url = "https://tnresults.nic.in/2026_HSCtnresults/2026_9994hsc.asp"

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

    for row in rows:

        cols = row.find_all("td")
        # Subject rows only
        if len(cols) == 6:

            subject = cols[0].get_text(strip=True)
            total = cols[4].get_text(strip=True)

            # Skip heading and total row
            if subject not in ["Subject", "TOTAL"]:

                results.append(int(total))

    cutoff=((results[2]+results[3])/2)+results[5]
    results.append(sum(results))
    results.append(cutoff)
    results.insert(0,name)
    results.insert(0,sec)
    results.insert(0,reg_no)

    # Storing marks in DB

    query=f"INSERT INTO hsc_result_{grp} VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query,results)
    icou+=1
    if icou%5==0:
        print(icou,"datas saved!")
db.commit()
db.close()
print("All datas have been saved successfully!")