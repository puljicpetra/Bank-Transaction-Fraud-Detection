# Checkpoint 3: Dizajn Dimenzijskog Modela Podataka

## 1. Odabir Poslovnog Procesa i Granularnosti

*   **Poslovni proces:** Analiza pojedinačnih bankovnih transakcija radi identifikacije i razumijevanja obrazaca prijevara.
*   **Granularnost tablice činjenica:** Svaki redak u tablici činjenica (`FactTransaction`) predstavljat će jednu pojedinačnu bankovnu transakciju.

## 2. Identifikacija Mjera (Činjenica)

Za tablicu činjenica `FactTransaction` definirane su sljedeće mjere:

1.  **`TransactionAmount`**: Numerička vrijednost iznosa transakcije. Ovo je glavna aditivna mjera.
2.  **`IsFraudIndicator`**: Cjelobrojna vrijednost (1 ako je transakcija prijevara, 0 ako nije). Omogućuje sumiranje broja prijevara i ukupnog iznosa prijevarnih transakcija.
3.  **`TransactionCount`**: Implicitna mjera, uvijek postavljena na 1 za svaki redak u tablici činjenica. Koristi se za jednostavno prebrojavanje transakcija.

## 3. Identifikacija Dimenzija

Definirano je sljedećih 6 glavnih dimenzija koje pružaju kontekst transakcijama:

1.  **`DimCustomer` (Kupac):** Atributi vezani za kupca koji je izvršio transakciju (npr. `OriginalCustomerID`, `CustomerName`, `Gender`, `Age`, `City`, `State`). Implementirana kao Sporo Mijenjajuća Dimenzija (SCD) Tip 2.
2.  **`DimDate` (Datum):** Atributi vezani za vrijeme transakcije (npr. `FullDate`, `Year`, `Quarter`, `Month`, `Day`).
3.  **`DimLocation` (Lokacija Transakcije):** Atributi vezani za geografsku lokaciju gdje se transakcija dogodila (npr. `TransactionLocationDescription`, `TransactionCity`, `TransactionState`).
4.  **`DimMerchant` (Trgovac):** Atributi vezani za trgovca kod kojeg je transakcija obavljena (npr. `OriginalMerchantID`).
5.  **`DimDevice` (Uređaj):** Atributi vezani za uređaj korišten za transakciju (npr. `DeviceName`, `DeviceTypeName`).
6.  **`DimOtherTransactionAttributes` (Ostali Atributi Transakcije - Junk Dimenzija):** Objedinjuje nekoliko manjih, često tekstualnih atributa niskog kardinaliteta kako bi se smanjio broj dimenzija i pojednostavila tablica činjenica. Uključuje: `TransactionTypeName`, `MerchantCategoryName`, `AccountTypeName`, `BankBranchName`, `CurrencyCode`.

## 4. Definiranje Hijerarhija i Degenerirane Dimenzije

*   **Hijerarhije:**
    1.  **`DimDate`**: `Year` -> `Quarter` -> `MonthOfYear` -> `DayOfMonth`
    2.  **`DimCustomer`**: `State` -> `City` (za lokaciju prebivališta kupca)
    3.  (Potencijalna) **`DimLocation`**: `TransactionState` -> `TransactionCity` (za lokaciju transakcije)
    4.  (Potencijalna) **`DimDevice`**: `DeviceTypeName` -> `DeviceName`
*   **Degenerirana Dimenzija:**
    *   **`OriginalTransactionID`**: Nalazi se direktno u tablici činjenica `FactTransaction` i predstavlja originalni identifikator transakcije iz izvornog sustava.

## 5. Odabir Sheme: Star Schema

Odabrana je **Star Schema** zbog svoje jednostavnosti, lakšeg razumijevanja i generalno boljih performansi za OLAP upite u usporedbi sa Snowflake shemom. Model se sastoji od centralne tablice činjenica (`FactTransaction`) i dimenzijskih tablica koje su direktno povezane s njom.

**Struktura Tablica (Pregled):**

*   **`FactTransaction`**:
    *   PK: `FactTransactionSKey`
    *   FKs: `DateSKey_FK`, `CustomerSKey_FK`, `LocationSKey_FK`, `MerchantSKey_FK`, `DeviceSKey_FK`, `OtherAttributesSKey_FK`
    *   Mjere: `TransactionAmount`, `IsFraudIndicator`, `TransactionCount`
    *   Degenerirana: `OriginalTransactionID`
*   **`DimDate`**: PK: `DateSKey`, Atributi: `FullDate`, `Year`, `Quarter`, `MonthOfYear`, `MonthName`, `DayOfMonth`, `DayOfWeekName`, `IsWeekend`
*   **`DimCustomer` (SCD Tip 2)**: PK: `CustomerSKey`, `OriginalCustomerID`, `CustomerName`, `Gender`, `Age`, `City`, `State`, `CustomerContact`, `CustomerEmail`, `RowVersion`, `ValidFromDate`, `ValidToDate`
*   **`DimLocation`**: PK: `LocationSKey`, `TransactionLocationDescription`, `TransactionCity`, `TransactionState`
*   **`DimMerchant`**: PK: `MerchantSKey`, `OriginalMerchantID`
*   **`DimDevice`**: PK: `DeviceSKey`, `DeviceName`, `DeviceTypeName`
*   **`DimOtherTransactionAttributes`**: PK: `OtherAttributesSKey`, `TransactionTypeName`, `MerchantCategoryName`, `AccountTypeName`, `BankBranchName`, `CurrencyCode`

## 6. Napredne Mogućnosti Izvedbe

*   **Sporo Mijenjajuće Dimenzije (SCD):** Implementiran je SCD Tip 2 za dimenziju `DimCustomer` kako bi se pratila povijest promjena atributa kupca. To uključuje dodavanje surogat ključa, verzije retka, te datuma valjanosti (`ValidFromDate`, `ValidToDate`).
*   **Junk Dimenzija:** Kreirana je `DimOtherTransactionAttributes` kao Junk dimenzija za grupiranje više atributa niskog kardinaliteta, čime se optimizira struktura tablice činjenica.

## 7. Implementacija Sheme

Struktura dimenzijskog modela (prazne tablice) implementirana je u MySQL bazi podataka pod nazivom `bank_fraud_dw` koristeći Python i SQLAlchemy. Skripta `dimenzijski_model.py` sadrži definicije SQLAlchemy klasa koje odgovaraju gore opisanim tablicama.

## 8. EER Dijagram Star Scheme

Generiran je EER dijagram iz baze `bank_fraud_dw` pomoću MySQL Workbench "Reverse Engineer" funkcije, koji vizualno prikazuje implementiranu Star Schemu.