import pandas as pd
from datetime import datetime

CSV_FILE_PATH = "C:\\Users\\Petra\\Desktop\\FIPU\\3\\SRP\\Bank_Transaction_Fraud_Detection.csv"

# Učitavanje CSV datoteke
df = pd.read_csv(CSV_FILE_PATH, delimiter=',')
print(f"CSV size before: {df.shape}")

# Osnovno čišćenje
# Uklanjanje redaka s nedostajućim vrijednostima
print("Missing values before dropna:\n", df.isnull().sum())
df.dropna(inplace=True)
print(f"CSV size after dropna: {df.shape}")

# Konverzija datuma i vremena
try:
    # Spoji stringove datuma i vremena
    datetime_str = df['Transaction_Date'] + ' ' + df['Transaction_Time']
    df['Transaction_DateTime'] = pd.to_datetime(datetime_str, dayfirst=True)
    print("Transaction_DateTime created successfully with dayfirst=True or explicit format.")
except Exception as e:
    print(f"Error combining date and time, attempting alternative parsing: {e}")
    print("Keeping Transaction_Date and Transaction_Time separate for now if combination failed.")


# Provjera tipova podataka
print("\nData types before potential corrections:\n", df.dtypes)
if df['Age'].dtype == 'object':
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    df.dropna(subset=['Age'], inplace=True)
    df['Age'] = df['Age'].astype(int)

if df['Transaction_Amount'].dtype == 'object':
    # Ukloni znakove valute ili tisućice ako postoje
    if isinstance(df['Transaction_Amount'].iloc[0], str):
        df['Transaction_Amount'] = df['Transaction_Amount'].replace({'\$': '', ',': ''}, regex=True)
    df['Transaction_Amount'] = pd.to_numeric(df['Transaction_Amount'], errors='coerce')
    df.dropna(subset=['Transaction_Amount'], inplace=True)

if df['Account_Balance'].dtype == 'object':
    if isinstance(df['Account_Balance'].iloc[0], str):
        df['Account_Balance'] = df['Account_Balance'].replace({'\$': '', ',': ''}, regex=True)
    df['Account_Balance'] = pd.to_numeric(df['Account_Balance'], errors='coerce')
    df.dropna(subset=['Account_Balance'], inplace=True)


# Brisanje originalnih stupaca za datum i vrijeme ako je kombinacija uspjela
if 'Transaction_DateTime' in df.columns:
    df = df.drop(columns=['Transaction_Date', 'Transaction_Time'])

# Ispis prvih redaka dataframe-a
print("\nProcessed DataFrame head:\n", df.head())
print(f"CSV size after processing: {df.shape}")

# Spremanje predprocesiranog skupa podataka u novu CSV datoteku
PROCESSED_CSV_PATH = "Bank_Transaction_Fraud_Detection_PROCESSED.csv"
df.to_csv(PROCESSED_CSV_PATH, index=False)
print(f"\nProcessed data saved to {PROCESSED_CSV_PATH}")