from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, ForeignKey, Float, Date, Boolean 
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/bank_fraud_dw"
engine = create_engine(DATABASE_URL, echo=True) 
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

DW_SCHEMA = 'bank_fraud_dw'


# DIMENZIJSKE TABLICE

class DimDate(Base):
    __tablename__ = 'dim_date'

    date_skey = Column(Integer, primary_key=True)
    full_date = Column(Date, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month_of_year = Column(Integer, nullable=False)
    month_name = Column(String(20), nullable=False)
    day_of_month = Column(Integer, nullable=False)
    day_of_week_name = Column(String(20), nullable=False)
    is_weekend = Column(Boolean, nullable=False)

class DimCustomer(Base):
    __tablename__ = 'dim_customer'

    customer_skey = Column(BigInteger, primary_key=True, autoincrement=True)
    original_customer_id = Column(String(50), index=True, nullable=False) # Poslovni ključ
    customer_name = Column(String(150))
    gender = Column(String(20))
    age = Column(Integer)
    city = Column(String(100))
    state = Column(String(100))
    customer_contact = Column(String(50))
    customer_email = Column(String(150))
    
    row_version = Column(Integer, nullable=False, default=1)
    valid_from_date = Column(DateTime, nullable=False)
    valid_to_date = Column(DateTime, nullable=True)

class DimLocation(Base):
    __tablename__ = 'dim_location'

    location_skey = Column(Integer, primary_key=True, autoincrement=True)
    transaction_location_description = Column(String(255), unique=True)
    transaction_city = Column(String(100))
    transaction_state = Column(String(100))

class DimMerchant(Base):
    __tablename__ = 'dim_merchant'

    merchant_skey = Column(BigInteger, primary_key=True, autoincrement=True)
    original_merchant_id = Column(String(50), unique=True, nullable=False) # Poslovni ključ

class DimDevice(Base):
    __tablename__ = 'dim_device'

    device_skey = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(100), nullable=False)
    device_type_name = Column(String(100), nullable=False)

class DimOtherTransactionAttributes(Base):
    __tablename__ = 'dim_other_transaction_attributes'

    other_attributes_skey = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type_name = Column(String(100))
    merchant_category_name = Column(String(100))
    account_type_name = Column(String(100))
    bank_branch_name = Column(String(150))
    currency_code = Column(String(10))


# TABLICA ČINJENICA

class FactTransaction(Base):
    __tablename__ = 'fact_transaction'

    fact_transaction_skey = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Strani ključevi prema dimenzijama (surogat ključevi)
    date_skey_fk = Column(Integer, ForeignKey(f'{DimDate.__tablename__}.date_skey'))
    customer_skey_fk = Column(BigInteger, ForeignKey(f'{DimCustomer.__tablename__}.customer_skey'))
    location_skey_fk = Column(Integer, ForeignKey(f'{DimLocation.__tablename__}.location_skey'))
    merchant_skey_fk = Column(BigInteger, ForeignKey(f'{DimMerchant.__tablename__}.merchant_skey'))
    device_skey_fk = Column(Integer, ForeignKey(f'{DimDevice.__tablename__}.device_skey'))
    other_attributes_skey_fk = Column(Integer, ForeignKey(f'{DimOtherTransactionAttributes.__tablename__}.other_attributes_skey'))
        
    # MJERE
    transaction_amount = Column(Float, nullable=False)
    is_fraud_indicator = Column(Integer, nullable=False)
    transaction_count = Column(Integer, nullable=False, default=1)

    # Degenerirana dimenzija
    original_transaction_id = Column(String(50), nullable=False, index=True)


Base.metadata.create_all(engine)

print(f"Dimenzijski model (Star Schema) za shemu '{DW_SCHEMA}' uspješno kreiran (ili već postoji).")

session.close()