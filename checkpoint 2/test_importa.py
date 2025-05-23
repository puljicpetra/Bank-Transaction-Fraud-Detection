import unittest
import pandas as pd
import sqlalchemy
from pandas.testing import assert_frame_equal
from sqlalchemy.orm import sessionmaker

class TestBankDatabase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/bank_fraud_db')
        self.connection = self.engine.connect()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.df_csv = pd.read_csv("Bank_Transaction_Fraud_Detection_PROCESSED.csv")
        
        if 'Transaction_DateTime' in self.df_csv.columns:
            self.df_csv['Transaction_DateTime'] = pd.to_datetime(self.df_csv['Transaction_DateTime'])
        else:
             self.df_csv['Transaction_Date'] = pd.to_datetime(self.df_csv['Transaction_Date'])


        self.df_csv['Age'] = pd.to_numeric(self.df_csv['Age'], errors='coerce').astype('Int64')
        self.df_csv['Transaction_Amount'] = pd.to_numeric(self.df_csv['Transaction_Amount'], errors='coerce')
        self.df_csv['Account_Balance'] = pd.to_numeric(self.df_csv['Account_Balance'], errors='coerce')
        self.df_csv['Is_Fraud'] = self.df_csv['Is_Fraud'].astype(bool)


        # Upit na bazu koji dohvaća sve podatke i spaja tablice
        query = """
        SELECT
            t.transaction_id_pk AS "Transaction_ID",
            c.customer_id_pk AS "Customer_ID",
            c.name AS "Customer_Name",
            c.gender AS "Gender",
            c.age AS "Age",
            c.state AS "State",
            c.city AS "City",
            bb.name AS "Bank_Branch",
            at.name AS "Account_Type",
            t.transaction_datetime AS "Transaction_DateTime", -- Ili t.date, t.time ako su odvojeni
            t.amount AS "Transaction_Amount",
            m.merchant_id_pk AS "Merchant_ID",
            mcat.name AS "Merchant_Category",
            tt.name AS "Transaction_Type",
            t.account_balance_after AS "Account_Balance",
            dev.name AS "Transaction_Device", -- Ime uređaja
            dt.name AS "Device_Type",
            loc.description AS "Transaction_Location",
            t.is_fraud AS "Is_Fraud",
            cur.code AS "Transaction_Currency",
            c.contact AS "Customer_Contact",
            t.description AS "Transaction_Description",
            c.email AS "Customer_Email"
        FROM transaction t
        JOIN customer c ON t.customer_id = c.customer_id_pk
        JOIN account_type at ON c.account_type_id = at.id
        JOIN bank_branch bb ON c.bank_branch_id = bb.id
        JOIN merchant m ON t.merchant_id = m.merchant_id_pk
        JOIN merchant_category mcat ON m.category_id = mcat.id
        JOIN transaction_type tt ON t.transaction_type_id = tt.id
        JOIN device dev ON t.device_id = dev.id
        JOIN device_type dt ON dev.device_type_id = dt.id
        JOIN location loc ON t.location_id = loc.id
        JOIN currency cur ON t.currency_id = cur.id
        ORDER BY t.transaction_id_pk ASC; 
        """

        result = self.connection.execute(sqlalchemy.text(query))
        self.db_df = pd.DataFrame(result.fetchall())
        if not self.db_df.empty:
            self.db_df.columns = result.keys()

            # Konverzija tipova za db_df da odgovaraju df_csv
            if 'Transaction_DateTime' in self.db_df.columns:
                 self.db_df['Transaction_DateTime'] = pd.to_datetime(self.db_df['Transaction_DateTime'])
            self.db_df['Age'] = pd.to_numeric(self.db_df['Age'], errors='coerce').astype('Int64')
            self.db_df['Transaction_Amount'] = pd.to_numeric(self.db_df['Transaction_Amount'], errors='coerce')
            self.db_df['Account_Balance'] = pd.to_numeric(self.db_df['Account_Balance'], errors='coerce')
            self.db_df['Is_Fraud'] = self.db_df['Is_Fraud'].astype(bool)
            
            self.db_df = self.db_df[self.df_csv.columns.tolist()]


    def test_row_count(self):
        if self.db_df.empty and not self.df_csv.empty:
            self.fail("Database DataFrame is empty while CSV DataFrame is not.")
        elif not self.db_df.empty and self.df_csv.empty:
             self.fail("CSV DataFrame is empty while Database DataFrame is not.")
        elif self.db_df.empty and self.df_csv.empty:
            pass
        else:
            self.assertEqual(len(self.df_csv), len(self.db_df), "Row counts do not match.")

    def test_columns(self):
        if not self.db_df.empty:
            self.assertListEqual(list(self.df_csv.columns), list(self.db_df.columns), "Column names or order do not match.")

    def test_dataframes_equal(self):
        if not self.db_df.empty and not self.df_csv.empty:
            df_csv_sorted = self.df_csv.sort_values(by='Transaction_ID').reset_index(drop=True)
            db_df_sorted = self.db_df.sort_values(by='Transaction_ID').reset_index(drop=True)
            
            try:
                assert_frame_equal(df_csv_sorted, db_df_sorted, check_dtype=False, rtol=1e-5, atol=1e-8)
            except AssertionError as e:
                print("\nDataFrame comparison failed. Differences:")
                for col in df_csv_sorted.columns:
                    if not df_csv_sorted[col].equals(db_df_sorted[col]):
                        print(f"Column '{col}' differs.")
                self.fail(f"DataFrames are not equal. {e}")


    def tearDown(self):
        self.session.close()
        self.connection.close()

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
