
"""
: This project is prepared for CS50P final project
:
"""

import pandas as pd
import sys
import numpy as np


# set working range
start_date = "2022-07-01"
end_date = "2023-06-30"
# confirm which client is working on. Xero is using line security. Each business in Xero called a Tenant.
# With unique ID. This program will only work on one Tenant at a time. Same way tax office will look at it.
# Original data base export included multiple tenants, but I removed other tenants to reduce the file for this project.
# Current sample tenant we will look into is tenant_id below. From accountant point of view, it is a client.
current_client = "e50158a9-2e3b-4896-810c-ab4019a934f9"
# which ATO client transaction file to look at
ato = 'ato_account.csv'  # SCPL


def main():
    # cjnl is the full table of journal header and lines from two CSV files after clean up
    cjnl_fy2023 = load_csv_cjnl()
    cjnl_fy2023.to_csv("cjnl.csv", index=False)  # testing output to see this df. ## to remove after testing

    # prepare data frame with a pivot table view
    bas_table = pd.pivot_table(cjnl_fy2023, values=['gross_amount', 'tax_amount'], index=['fiscal_quarter', 'tax_name'],
                              aggfunc='sum', fill_value=0)
    # interim output for BAS report. Accountant need this for year-end work paper

    bas_table.reset_index(inplace=True)
    # print(bas_table)
    bas_table.to_csv("bas_table.csv", index=False)

    # bring in tax office data
    # bring in lodgement/sync date
    ato_ica_dates = ica_dates_list()
    ato_ica_dates.to_csv("ato_ica_dates.csv", index=False)
    # print(ato_ica_dates)

    # chec if the line created after lodgement
    cjnl_fy2023_period = pd.merge(cjnl_fy2023, ato_ica_dates, on='period_id')
    cjnl_fy2023_period['not_sync'] = (
                cjnl_fy2023_period['journal_create_date'] > cjnl_fy2023_period['Processed Date']).apply(
        lambda x: "ToAmend" if x else "Lodged")
    cjnl_fy2023_nosync = cjnl_fy2023_period[cjnl_fy2023_period['not_sync'].str.contains(
        'ToAmend', case=False, na=False)]
    # export error transactions to csv
    cjnl_fy2023_nosync.to_csv("cjnl_fy2023_nosync.csv", index=False)

    bas_table2 = pd.pivot_table(cjnl_fy2023_period, index=['fiscal_quarter_x', 'tax_name'], columns=['not_sync'],
                               values=['gross_amount', 'tax_amount'], aggfunc='sum', fill_value=0)
    bas_table2 = bas_table2.map(lambda x: '{:,.2f}'.format(x))
    # Output for accountants to see the total amount of variance could be caused by use input in Xero after BAS lodged
    print(bas_table2)
    bas_table2.reset_index(inplace=True)
    bas_table2.to_csv("bas_amend.csv", index=False)

    print("Calculation finished")




def load_csv_cjnl():
    # two CSV file is full file saved from Xero API from a live client file.
    # "xero_cash_journal.csv" is the transaction headers. "xero_cash_journal_lines.csv" is the
    # transaction details.
    try:
        cash_journal = pd.read_csv('xero_cash_journals.csv')
        cash_journal_lines = pd.read_csv('xero_cash_journal_lines.csv')
        cjnl = pd.merge(cash_journal, cash_journal_lines, on='journal_id')
        cjnl_fy2023 = cjnl[(cjnl['journal_date'] >= start_date) & (cjnl['journal_date'] <= end_date)]
        # remove other client files from the data frame
        cjnl_fy2023 = cjnl_fy2023[(cjnl_fy2023['tenant_id'].str.contains(current_client))]
        # remove columns not need
        cjnl_fy2023 = cjnl_fy2023.drop(
            columns=['tenant_id', 'created_at_x', 'created_at_y', 'updated_at_x', 'updated_at_y'])
        cjnl_fy2023['journal_date'] = pd.to_datetime(cjnl_fy2023['journal_date'])  # change to date format
        cjnl_fy2023['quarter'] = cjnl_fy2023['journal_date'].dt.quarter  # add quarter numbers
        cjnl_fy2023['fiscal_quarter'] = cjnl_fy2023['quarter'].apply(
            lambda x: x - 2 if x > 2 else x + 2)  # change to financial year quarter
        # ato_ica_dates['period_id'] = "FY" + ato_ica_dates['fiscal_year'].astype(str) + "Q" +
        # ato_ica_dates['fiscal_quarter'].astype(str)
        cjnl_fy2023['period_id'] = "FY2023Q" + cjnl_fy2023['fiscal_quarter'].astype(str)
    except FileNotFoundError:
        print("File not found from Xero output")
        sys.exit()
    except TypeError as e:
        print(f"Loading Xero Journal TypeError Encountered: {e}")
        sys.exit()
    else:
        return cjnl_fy2023  # output included full journal details and added fiscal year quarter

    # Australia financial year start from 1st Jul end the next year 30th June.
    # This function is to work out which financial year the date fall under.


def fiscal_year(row_date):
    if (row_date.month, row_date.day) < (7, 1):
        return row_date.year
    else:
        return row_date.year + 1


def ica_dates_list():
    try:
        # 1. load csv from ATO download and skip first raw
        # user has to select output range to cover the period required between start_date and end_date
        ato_ica = pd.read_csv(ato, skiprows=2)  # 'ato' pointed to the ica account CSV file

        # 2. change the date format
        ato_ica['Processed Date'] = pd.to_datetime(ato_ica['Processed Date'], format='%d-%b-%y')
        ato_ica['Effective Date'] = pd.to_datetime(ato_ica['Effective Date'], format='%d-%b-%y')

        # 3. filter lines only included "Activity Statement".
        # tax office outputs most of the time stay the same. but need error handle for name changes.
        ato_ica_dates = ato_ica[ato_ica['Description'].str.contains("Activity Statement")].copy()
        # SettingWithCopyWarning took me a long time to understand and fix

        # 4. workout period end dates
        ato_ica_dates['period_text'] = ato_ica_dates['Description'].str[-9:]
        # last 9 char of the BASes showing the period end as "DD MMM YY"
        ato_ica_dates['period_end'] = pd.to_datetime(ato_ica_dates['period_text'], format='%d %b %y')
        # make sure it is a date type

        ato_ica_dates['quarter'] = ato_ica_dates['period_end'].dt.quarter
        # quarter # of the year
        ato_ica_dates['fiscal_quarter'] = ato_ica_dates['quarter'].apply(lambda x: x - 2 if x > 2 else x + 2)
        # quarter # of the financial year
        print(ato_ica_dates)

        # work out financial yaer
        ato_ica_dates['fiscal_year'] = ato_ica_dates['period_end'].apply(fiscal_year)
        ato_ica_dates['period_id'] = "FY" + ato_ica_dates['fiscal_year'].astype(str) + "Q" + ato_ica_dates['fiscal_quarter'].astype(str)

        ## work out original or amnedment
        ato_ica_dates['BAStype']= np.where(ato_ica_dates['Description'].str.contains('Original'),'Original','Amendment')

        # only look for origial dates
        ato_ica_dates = ato_ica_dates[ato_ica_dates['BAStype'].str.contains("Original")]
    except FileNotFoundError:
        print("File not found from ATO output")
        sys.exit()
    except TypeError as e:
        print(f"Loading ATO ICA transaction TypeError Encountered: {e}")
        sys.exit()
    else:
        return ato_ica_dates

def xero_after_lodge():
    ...

def main_gst_rec():
    ...



if __name__ == "__main__":
    main()
