# I find it more comfortable to start in a Python script and then write the Markdown afterwards, so that's what this file is.
# Import the required packages.
from curl_cffi import requests
from bs4 import BeautifulSoup
import pandas as pd

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

url = 'https://www.ccny.cuny.edu/registrar/fall'
r = requests.get(url, impersonate="chrome")

soup = BeautifulSoup(r.text, "html.parser")

# List of lists in which to store data scraped from the HTML.
data = []
# Analysis of the HTML of the page reveals that all of the relevant data is stored in a <table> object, and each row is a <tr> object.
rows = soup.find_all("tr")
# The first row contains garbage data, so we delete it.
del rows[0]
# In each row, each column is stored in a <td> object.
for row in rows:
    cols = [" ".join(td.text.split()) for td in row.find_all("td")]
    # Parse dates into a consistent format.
    if "," in cols[0]:
        # If the date contains a comma, this means the year is specified.
        year = int(cols[0][-4:])
    else:
        # Otherwise, the year is 2021.
        year = 2021
    month = months.index(cols[0].split()[0])+1
    # If there's a hyphen, it means there are multiple dates.
    if "-" in cols[0]:
        lday = int(cols[0].split()[1])
        rday = int(cols[0].split()[3])
        lwday = weekdays.index(cols[1].split()[0])
        rwday = weekdays.index(cols[1].split()[2])
        for i in range(0, rday-lday+1):
            day = lday+i
            wday = (lwday+i)%7
            tmpcols = cols[:]
            tmpcols[0] = f"{year:04d}-{month:02d}-{day:02d}"
            tmpcols[1] = weekdays[wday]
            data.append(tmpcols)
    else:
        day = cols[0].split()[1]
        if "," in day:
            day = day.replace(",","")
        day = int(day)
        cols[0] = f"{year:04d}-{month:02d}-{day:02d}"
        data.append(cols)

# Now that we have a list of lists containing the data we want, we can turn it into a DataFrame with the specified column names.
df = pd.DataFrame(data, columns=["date", "day_of_week", "explanation"])
print(df.head())

# Index the DataFrame by date.
df_ind = df.set_index("date")
# Convert index into proper datetime objects.
df_ind.index = pd.to_datetime(df_ind.index)
# Sort DataFrame.
df_ind = df_ind.sort_index()
print(df_ind.head())

# Check if dates work by printing only the dates in September.
print(df_ind["2021-09":"2021-09"])