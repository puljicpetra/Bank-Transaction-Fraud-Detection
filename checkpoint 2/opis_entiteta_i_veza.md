# Specifikacija Konceptualnog Modela Baze Podataka: Bank Transaction Fraud Detection

## 1. Entiteti i Atributi

### 1.1. Kupac (Customer)
   - **Opis:** Predstavlja klijenta banke koji obavlja transakcije.
   - **Atributi:**
     - `CustomerID` (PK, String/UUID): Jedinstveni identifikator kupca
     - `CustomerName` (String): Ime i prezime kupca
     - `Gender` (String): Spol kupca
     - `Age` (Integer): Starost kupca
     - `State` (String): Država prebivališta kupca
     - `City` (String): Grad prebivališta kupca
     - `CustomerContact` (String): Kontakt broj kupca
     - `CustomerEmail` (String): Email adresa kupca
     - `AccountTypeID_FK` (FK, Integer): Strani ključ koji povezuje s entitetom `TipRacuna`
     - `BankBranchID_FK` (FK, Integer): Strani ključ koji povezuje s entitetom `PoslovnicaBanke`

### 1.2. TipRacuna (AccountType)
   - **Opis:** Definira vrstu računa koju kupac posjeduje (npr. Štedni, Poslovni).
   - **Atributi:**
     - `ID` (PK, Integer, AutoIncrement): Jedinstveni numerički identifikator tipa računa
     - `Name` (String, Unique): Naziv tipa računa

### 1.3. PoslovnicaBanke (BankBranch)
   - **Opis:** Predstavlja specifičnu poslovnicu banke u kojoj kupac drži račun.
   - **Atributi:**
     - `ID` (PK, Integer, AutoIncrement): Jedinstveni numerički identifikator poslovnice banke
     - `Name` (String, Unique): Naziv poslovnice banke

### 1.4. Trgovac (Merchant)
   - **Opis:** Predstavlja entitet kod kojeg je transakcija izvršena.
   - **Atributi:**
     - `MerchantID_PK` (PK, String/UUID): Jedinstveni identifikator trgovca
     - `MerchantCategoryID_FK` (FK, Integer): Strani ključ koji povezuje s entitetom `KategorijaTrgovca`

### 1.5. KategorijaTrgovca (MerchantCategory)
   - **Opis:** Klasificira trgovce prema vrsti djelatnosti.
   - **Atributi:**
     - `ID` (PK, Integer, AutoIncrement): Jedinstveni numerički identifikator kategorije trgovca
     - `Name` (String, Unique): Naziv kategorije trgovca

### 1.6. Uređaj (Device)
   - **Opis:** Predstavlja specifični uređaj korišten za obavljanje transakcije.
   - **Napomena:** `Name` se odnosi na vrijednost iz `Transaction_Device`. Budući da isti `Transaction_Device` (npr. "iPhone 12") može pripadati različitim `Device_Type` (npr. "Smartphone"), jedinstvenost se osigurava kombinacijom `Name` i `DeviceTypeID_FK`.
   - **Atributi:**
     - `ID` (PK, Integer, AutoIncrement): Jedinstveni numerički identifikator uređaja
     - `Name` (String): Naziv ili identifikator uređaja korištenog u transakciji
     - `DeviceTypeID_FK` (FK, Integer): Strani ključ koji povezuje s entitetom `TipUredjaja`

### 1.7. TipUređaja (DeviceType)
   - **Opis:** Definira opću vrstu uređaja korištenog za transakciju.
   - **Atributi:**
     - `ID` (PK, Integer, AutoIncrement): Jedinstveni numerički identifikator tipa uređaja
     - `Name` (String, Unique): Naziv tipa uređaja

### 1.8. Lokacija (Location)
   - **Opis:** Predstavlja geografsku lokaciju na kojoj je transakcija izvršena.
   - **Atributi:**
     - `ID` (PK, Integer, AutoIncrement): Jedinstveni numerički identifikator lokacije
     - `Description` (String, Unique): Opis lokacije, može biti kombinacija latitude/longitude ili adrese

### 1.9. Valuta (Currency)
   - **Opis:** Definira valutu u kojoj je transakcija izvršena.
   - **Atributi:**
     - `ID` (PK, Integer, AutoIncrement): Jedinstveni numerički identifikator valute
     - `Code` (String, Unique): Kod valute (npr. USD, EUR, INR)

### 1.10. TipTransakcije (TransactionType)
   - **Opis:** Definira prirodu transakcije (npr. Podizanje, Uplata, Prijenos).
   - **Atributi:**
     - `ID` (PK, Integer, AutoIncrement): Jedinstveni numerički identifikator tipa transakcije
     - `Name` (String, Unique): Naziv tipa transakcije

### 1.11. Transakcija (Transaction)
   - **Opis:** Centralni entitet koji bilježi svaku pojedinačnu bankovnu transakciju i povezuje ostale entitete.
   - **Atributi:**
     - `TransactionID_PK` (PK, String/UUID): Jedinstveni identifikator transakcije
     - `CustomerID_FK` (FK, String/UUID): Strani ključ koji povezuje s entitetom `Kupac`
     - `TransactionDateTime` (DateTime): Datum i vrijeme kada je transakcija izvršena
     - `TransactionAmount` (Float): Novčani iznos transakcije
     - `MerchantID_FK` (FK, String/UUID): Strani ključ koji povezuje s entitetom `Trgovac`
     - `TransactionTypeID_FK` (FK, Integer): Strani ključ koji povezuje s entitetom `TipTransakcije`
     - `AccountBalanceAfterTransaction` (Float): Stanje računa kupca nakon izvršene transakcije
     - `DeviceID_FK` (FK, Integer): Strani ključ koji povezuje s entitetom `Uredjaj`
     - `LocationID_FK` (FK, Integer): Strani ključ koji povezuje s entitetom `Lokacija`
     - `IsFraud` (Boolean): Binarni indikator (0 ili 1) koji označava je li transakcija prijevara
     - `CurrencyID_FK` (FK, Integer): Strani ključ koji povezuje s entitetom `Valuta`
     - `TransactionDescription` (String): Kratki opis transakcije

---

## 2. Veze između Entiteta i Kardinalnost

Ovdje su definirane ključne veze između entiteta i njihova kardinalnost.

1.  **Kupac (Customer) ↔ Transakcija (Transaction)**
    *   **Opis:** Jedan `Kupac` može imati više `Transakcija`. Svaka `Transakcija` pripada točno jednom `Kupcu`.
    *   **Kardinalnost:** 1:N (Jedan Kupac : Više Transakcija)
    *   **Strani ključ:** `Transaction.CustomerID_FK` referencira `Customer.CustomerID`.

2.  **Kupac (Customer) ↔ TipRacuna (AccountType)**
    *   **Opis:** Jedan `Kupac` povezan je s jednim `TipomRacuna`. Jedan `TipRacuna` može biti dodijeljen većem broju `Kupaca`.
    *   **Kardinalnost:** N:1 (Više Kupaca : Jedan TipRacuna)
    *   **Strani ključ:** `Customer.AccountTypeID_FK` referencira `AccountType.ID`.

3.  **Kupac (Customer) ↔ PoslovnicaBanke (BankBranch)**
    *   **Opis:** Jedan `Kupac` povezan je s jednom `PoslovnicomBanke`. Jedna `PoslovnicaBanke` može imati više `Kupaca`.
    *   **Kardinalnost:** N:1 (Više Kupaca : Jedna PoslovnicaBanke)
    *   **Strani ključ:** `Customer.BankBranchID_FK` referencira `BankBranch.ID`.

4.  **Trgovac (Merchant) ↔ Transakcija (Transaction)**
    *   **Opis:** Jedan `Trgovac` može biti uključen u više `Transakcija`. Svaka `Transakcija` se odnosi na jednog `Trgovca`.
    *   **Kardinalnost:** 1:N (Jedan Trgovac : Više Transakcija)
    *   **Strani ključ:** `Transaction.MerchantID_FK` referencira `Merchant.MerchantID_PK`.

5.  **Trgovac (Merchant) ↔ KategorijaTrgovca (MerchantCategory)**
    *   **Opis:** Jedan `Trgovac` pripada jednoj `KategorijiTrgovca`. Jedna `KategorijaTrgovca` može obuhvaćati više `Trgovaca`.
    *   **Kardinalnost:** N:1 (Više Trgovaca : Jedna KategorijaTrgovca)
    *   **Strani ključ:** `Merchant.MerchantCategoryID_FK` referencira `MerchantCategory.ID`.

6.  **Uređaj (Device) ↔ Transakcija (Transaction)**
    *   **Opis:** Jedan `Uređaj` može biti korišten u više `Transakcija`. Svaka `Transakcija` je izvršena pomoću jednog `Uređaja`.
    *   **Kardinalnost:** 1:N (Jedan Uređaj : Više Transakcija)
    *   **Strani ključ:** `Transaction.DeviceID_FK` referencira `Device.ID`.

7.  **Uređaj (Device) ↔ TipUređaja (DeviceType)**
    *   **Opis:** Jedan `Uređaj` pripada jednom `TipuUređaja`. Jedan `TipUređaja` može obuhvaćati više `Uređaja`.
    *   **Kardinalnost:** N:1 (Više Uređaja : Jedan TipUređaja)
    *   **Strani ključ:** `Device.DeviceTypeID_FK` referencira `DeviceType.ID`.

8.  **Lokacija (Location) ↔ Transakcija (Transaction)**
    *   **Opis:** Jedna `Lokacija` može biti mjesto više `Transakcija`. Svaka `Transakcija` se događa na jednoj `Lokaciji`.
    *   **Kardinalnost:** 1:N (Jedna Lokacija : Više Transakcija)
    *   **Strani ključ:** `Transaction.LocationID_FK` referencira `Location.ID`.

9.  **Valuta (Currency) ↔ Transakcija (Transaction)**
    *   **Opis:** Jedna `Valuta` može biti korištena u više `Transakcija`. Svaka `Transakcija` je izvršena u jednoj `Valuti`.
    *   **Kardinalnost:** 1:N (Jedna Valuta : Više Transakcija)
    *   **Strani ključ:** `Transaction.CurrencyID_FK` referencira `Currency.ID`.

10. **TipTransakcije (TransactionType) ↔ Transakcija (Transaction)**
    *   **Opis:** Jedan `TipTransakcije` može opisivati više `Transakcija`. Svaka `Transakcija` pripada jednom `TipuTransakcije`.
    *   **Kardinalnost:** 1:N (Jedan TipTransakcije : Više Transakcija)
    *   **Strani ključ:** `Transaction.TransactionTypeID_FK` referencira `TransactionType.ID`.

---