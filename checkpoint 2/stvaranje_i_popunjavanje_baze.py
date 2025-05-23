import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, UniqueConstraint # <<< ISPRAVKA: Dodan UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

CSV_FILE_PATH = "Bank_Transaction_Fraud_Detection_PROCESSED.csv"

df = pd.read_csv(CSV_FILE_PATH, delimiter=',')
print(f"CSV size: {df.shape}")

# Osiguravanje da 'Transaction_DateTime' postoji i da je ispravnog tipa
if 'Transaction_DateTime' not in df.columns and 'Transaction_Date' in df.columns and 'Transaction_Time' in df.columns:
    try:
        datetime_str = df['Transaction_Date'] + ' ' + df['Transaction_Time']
        df['Transaction_DateTime'] = pd.to_datetime(datetime_str, dayfirst=True)
        print("Transaction_DateTime created from separate Date and Time columns.")
        df.drop(columns=['Transaction_Date', 'Transaction_Time'], inplace=True, errors='ignore')
    except Exception as e:
        print(f"Could not combine Transaction_Date and Transaction_Time: {e}. Ensure they are parsable.")
elif 'Transaction_DateTime' in df.columns:
     df['Transaction_DateTime'] = pd.to_datetime(df['Transaction_DateTime'])

print("DataFrame head after ensuring Transaction_DateTime:")
print(df.head())

Base = declarative_base()

# --- Definiranje sheme baze ---

class AccountType(Base):
    __tablename__ = 'account_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    customers = relationship("Customer", back_populates="account_type")

class BankBranch(Base):
    __tablename__ = 'bank_branch'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)
    customers = relationship("Customer", back_populates="bank_branch")

class Customer(Base):
    __tablename__ = 'customer'
    customer_id_pk = Column(String(50), primary_key=True)
    name = Column(String(150))
    gender = Column(String(20))
    age = Column(Integer)
    state = Column(String(100))
    city = Column(String(100))
    contact = Column(String(50))
    email = Column(String(150))
    account_type_id = Column(Integer, ForeignKey('account_type.id'))
    bank_branch_id = Column(Integer, ForeignKey('bank_branch.id'))

    account_type = relationship("AccountType", back_populates="customers")
    bank_branch = relationship("BankBranch", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer")

class MerchantCategory(Base):
    __tablename__ = 'merchant_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    merchants = relationship("Merchant", back_populates="category")

class Merchant(Base):
    __tablename__ = 'merchant'
    merchant_id_pk = Column(String(50), primary_key=True)
    category_id = Column(Integer, ForeignKey('merchant_category.id'))

    category = relationship("MerchantCategory", back_populates="merchants")
    transactions = relationship("Transaction", back_populates="merchant")

class DeviceType(Base):
    __tablename__ = 'device_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    devices = relationship("Device", back_populates="device_type")

class Device(Base):
    __tablename__ = 'device'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    device_type_id = Column(Integer, ForeignKey('device_type.id'))

    device_type = relationship("DeviceType", back_populates="devices")
    transactions = relationship("Transaction", back_populates="device")
    __table_args__ = (UniqueConstraint('name', 'device_type_id', name='uq_device_name_type'),)


class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(255), nullable=False, unique=True)
    transactions = relationship("Transaction", back_populates="location")

class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, unique=True)
    transactions = relationship("Transaction", back_populates="currency")

class TransactionType(Base):
    __tablename__ = 'transaction_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    transactions = relationship("Transaction", back_populates="transaction_type_details")

class Transaction(Base):
    __tablename__ = 'transaction'
    transaction_id_pk = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey('customer.customer_id_pk'))
    transaction_datetime = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    merchant_id = Column(String(50), ForeignKey('merchant.merchant_id_pk'))
    transaction_type_id = Column(Integer, ForeignKey('transaction_type.id'))
    account_balance_after = Column(Float)
    device_id = Column(Integer, ForeignKey('device.id'))
    location_id = Column(Integer, ForeignKey('location.id'))
    is_fraud = Column(Boolean, nullable=False)
    currency_id = Column(Integer, ForeignKey('currency.id'))
    description = Column(String(255))

    customer = relationship("Customer", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    transaction_type_details = relationship("TransactionType", back_populates="transactions")
    device = relationship("Device", back_populates="transactions")
    location = relationship("Location", back_populates="transactions")
    currency = relationship("Currency", back_populates="transactions")

# --- Stvaranje konekcije i tablica ---

engine = create_engine('mysql+pymysql://root:root@localhost:3306/bank_fraud_db' , echo=False)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# --- Popunjavanje tablica ---

print("Populating lookup tables...")
# AccountType
account_types_map = {}
for name in df['Account_Type'].unique():
    if pd.notna(name):
        at = AccountType(name=name)
        session.add(at)
session.commit()
for at_obj in session.query(AccountType).all():
    account_types_map[at_obj.name] = at_obj.id
print("AccountType populated.")

# BankBranch
bank_branches_map = {}
for name in df['Bank_Branch'].unique():
    if pd.notna(name):
        bb = BankBranch(name=name)
        session.add(bb)
session.commit()
for bb_obj in session.query(BankBranch).all():
    bank_branches_map[bb_obj.name] = bb_obj.id
print("BankBranch populated.")

# MerchantCategory
merchant_categories_map = {}
for name in df['Merchant_Category'].unique():
    if pd.notna(name):
        mc = MerchantCategory(name=name)
        session.add(mc)
session.commit()
for mc_obj in session.query(MerchantCategory).all():
    merchant_categories_map[mc_obj.name] = mc_obj.id
print("MerchantCategory populated.")

# DeviceType
device_types_map = {}
for name in df['Device_Type'].unique():
    if pd.notna(name):
        dt = DeviceType(name=name)
        session.add(dt)
session.commit()
for dt_obj in session.query(DeviceType).all():
    device_types_map[dt_obj.name] = dt_obj.id
print("DeviceType populated.")

# Location
locations_map = {}
for desc in df['Transaction_Location'].unique():
    if pd.notna(desc):
        loc = Location(description=desc)
        session.add(loc)
session.commit()
for loc_obj in session.query(Location).all():
    locations_map[loc_obj.description] = loc_obj.id
print("Location populated.")

# Currency
currencies_map = {}
for code in df['Transaction_Currency'].unique():
    if pd.notna(code):
        cur = Currency(code=code)
        session.add(cur)
session.commit()
for cur_obj in session.query(Currency).all():
    currencies_map[cur_obj.code] = cur_obj.id
print("Currency populated.")

# TransactionType
transaction_types_map = {}
for name in df['Transaction_Type'].unique():
    if pd.notna(name):
        tt = TransactionType(name=name)
        session.add(tt)
session.commit()
for tt_obj in session.query(TransactionType).all():
    transaction_types_map[tt_obj.name] = tt_obj.id
print("TransactionType populated.")

print("Populating main tables...")
# Customer (jedinstveni kupci)
# Filtriraj DataFrame da se dobiju samo jedinstveni kupci na temelju Customer_ID
unique_customers_df = df.drop_duplicates(subset=['Customer_ID'])
customers_added_count = 0
for index, row in unique_customers_df.iterrows():
    customer_id = row['Customer_ID']
    if pd.notna(customer_id):
        customer = Customer(
            customer_id_pk=customer_id,
            name=row.get('Customer_Name'),
            gender=row.get('Gender'),
            age=int(row['Age']) if pd.notna(row['Age']) else None,
            state=row.get('State'),
            city=row.get('City'),
            contact=row.get('Customer_Contact'),
            email=row.get('Customer_Email'),
            account_type_id=account_types_map.get(row['Account_Type']),
            bank_branch_id=bank_branches_map.get(row['Bank_Branch'])
        )
        session.add(customer)
        customers_added_count +=1
session.commit()
print(f"Customers populated: {customers_added_count} unique customers.")

# Merchant (jedinstveni trgovci)
unique_merchants_df = df.drop_duplicates(subset=['Merchant_ID'])
merchants_added_count = 0
for index, row in unique_merchants_df.iterrows():
    merchant_id = row['Merchant_ID']
    if pd.notna(merchant_id):
        merchant = Merchant(
            merchant_id_pk=merchant_id,
            category_id=merchant_categories_map.get(row['Merchant_Category'])
        )
        session.add(merchant)
        merchants_added_count +=1
session.commit()
print(f"Merchants populated: {merchants_added_count} unique merchants.")

# Device (kombinacija Transaction_Device i Device_Type)
unique_devices_df = df.drop_duplicates(subset=['Transaction_Device', 'Device_Type'])
devices_map = {} # Ključ će biti (transaction_device_name, device_type_name) -> vrijednost će biti ID
devices_added_count = 0
for index, row in unique_devices_df.iterrows():
    dev_name = row['Transaction_Device']
    dev_type_name = row['Device_Type']
    if pd.notna(dev_name) and pd.notna(dev_type_name):
        dev = Device(
            name=dev_name,
            device_type_id=device_types_map.get(dev_type_name)
        )
        session.add(dev)
        devices_added_count +=1
session.commit()
for device_obj in session.query(Device).all():
    devices_map[(device_obj.name, device_obj.device_type.name)] = device_obj.id
print(f"Devices populated: {devices_added_count} unique devices.")


# Transaction (glavna tablica)
if 'Transaction_DateTime' not in df.columns or df['Transaction_DateTime'].isnull().any():
    print("ERROR: Transaction_DateTime column is missing or contains nulls. Cannot proceed with Transaction population.")
    session.rollback()
else:
    print("Populating Transactions. This may take a while...")
    transaction_count = 0
    for index, row in df.iterrows():
        customer_fk = row['Customer_ID']
        merchant_fk = row['Merchant_ID']
        transaction_id_val = row['Transaction_ID']
        
        if not (pd.notna(customer_fk) and pd.notna(merchant_fk) and pd.notna(transaction_id_val)) :
            print(f"Skipping row {index} due to missing critical FK or PK: Customer_ID={customer_fk}, Merchant_ID={merchant_fk}, Transaction_ID={transaction_id_val}")
            continue

        transaction_datetime_val = row['Transaction_DateTime']
        if pd.isna(transaction_datetime_val):
            print(f"Skipping row {index} due to NaT in Transaction_DateTime for Transaction_ID: {transaction_id_val}")
            continue

        is_fraud_val = row['Is_Fraud']
        if pd.notna(is_fraud_val):
            is_fraud_bool = bool(int(is_fraud_val))
        else:
            is_fraud_bool = False 

        device_key = (row['Transaction_Device'], row['Device_Type'])
        device_id_val = devices_map.get(device_key)
        if device_id_val is None and pd.notna(row['Transaction_Device']) and pd.notna(row['Device_Type']):
            print(f"Warning: Device ID not found in map for key {device_key}. Transaction_ID: {transaction_id_val}. Device might not have been added if it's a new combination not in unique_devices_df due to other NaNs.")


        transaction = Transaction(
            transaction_id_pk=transaction_id_val,
            customer_id=customer_fk,
            transaction_datetime=transaction_datetime_val,
            amount=float(row['Transaction_Amount']) if pd.notna(row['Transaction_Amount']) else 0.0,
            merchant_id=merchant_fk,
            transaction_type_id=transaction_types_map.get(row['Transaction_Type']),
            account_balance_after=float(row['Account_Balance']) if pd.notna(row['Account_Balance']) else None,
            device_id=device_id_val,
            location_id=locations_map.get(row['Transaction_Location']),
            is_fraud=is_fraud_bool,
            currency_id=currencies_map.get(row['Transaction_Currency']),
            description=row.get('Transaction_Description')
        )
        session.add(transaction)
        transaction_count += 1
        if transaction_count % 5000 == 0:
            try:
                session.commit()
                print(f"Committed {transaction_count} transactions...")
            except Exception as e:
                print(f"Error during commit at {transaction_count} transactions: {e}")
                session.rollback()
                break

    try:
        session.commit()
        print(f"Final commit. Transactions populated: {transaction_count} transactions.")
    except Exception as e:
        print(f"Error during final commit: {e}")
        session.rollback()

session.close()
print("Database schema created and populated (or attempted).")