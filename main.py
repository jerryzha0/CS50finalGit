
"""
: This project is prepared for CS50P final project
: Would be planning for GST rec test 1 to solve the problem of cleaning large amount of data
: Data sources to review and check:
: - Xero Gneral Ledger with large amount of data,
: - ATO ICA account transactions,
: - BASes lodged
:
:
: Functions could need
: - Xero Gneral Ledger
: == API to get journals, will be two tables, one for accrual and one for cash
: == search for a list of journals created after BAS lodgement date
: == any API to take data from Xero?
: - ATO ICA account
: == tag, date of lodgement for each BASes
: == seperated table to manage BAS range and lodgement dates
: ==
: - BASes lodged

: can we try to create a class for each BAS to have (original, amned 1, amned 2, amned 3, amned):
: - Start date
: - End date
: - due date (effective date)
: - lodgement date
: - value of each label lodged


: a testing file named as test_project.py
"""
import pandas as pd


def main():
    ...


def api_connect_xero():
    ...


def ica_dates_list():
    ...


def xero_after_lodge():
    ...


def main_gst_rec():
    ...


if __name__ == "__main__":
    main()
