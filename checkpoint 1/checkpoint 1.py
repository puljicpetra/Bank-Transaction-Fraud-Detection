# Učitavanje potrebnih biblioteka
import pandas as pd

# Učitavanje podataka iz CSV datoteke
PATH = "C:\\Users\\Petra\\Desktop\\FIPU\\3\\SRP\\Bank_Transaction_Fraud_Detection.csv"

# Učitavanje prvih 2000 redova
# data = pd.read_csv(PATH, delimiter=',', nrows=2000)

# Učitavanje cijelog dataseta
data = pd.read_csv(PATH, delimiter=',')

# Ispis prvih 5 redova
print(data.head())

# Ispis dimenzija skupa podataka (potrebno je učitati sve podatke radi analize, ne samo prvih 2000 redova)
print(data.shape)

# Ispis imena stupaca i nedostajućih vrijednosti
print(data.isna().sum())

# Ispis broja jedinstvenih vrijednosti po stupcima
print(data.nunique())

# Ispis tipova podataka po stupcima (analiza kvanitativnih i kvalitativnih varijabli)
print(data.dtypes)

# Ispis broja jedinstvenih vrijednosti po stupcima
for column in data:
    print(data[column].value_counts())
    input("...")

# Ispis imena stupaca
print(data.columns.values)