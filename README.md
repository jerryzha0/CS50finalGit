Back ground
In Australia, business is operated with GST (Goods and Services). GST is good source of Feberal Tax but created 
a lot extra work for businesses and tax agents to check the transactions. Each year accountant will spend hours to 
check and find out where the errors is. In a nutcell, businesses report GST payable on quarterly bases 28 days 
after the quarter, say Jan - March Quarter will be reported on the 28th April. It is more like a "sync" request to 
ATO data via a report called BAS. Accountant could need to check and correct the report via re-sync (amended BAS) 
because could still create transactions after the date synced, or the initial transaction created with errors.

Xero is the accounting software we are using in this project. Xero provided limited API access to the database, 
but enough to speed up of the accounting functions. 

This project is prepared for CS50P final project
Would be planning for GST rec test 1 to solve the problem of cleaning large amount of data
Data sources to review and check:
 - Xero Gneral Ledger with large amount of data,
 - ATO ICA account transactions,
 - BASes lodged


Test files provided in CSV
 - xero_cash_journal_lines.csv: journal details from the header database
 - xero_cash_journal.csv: journal header records
 - ato_account_SCPL.csv: ATO Data downloaded form tax office. 


 can we try to create a class for each BAS to have (original, amned 1, amned 2, amned 3, amned):
 - Start date
 - End date
 - due date (effective date)
 - lodgement date
 - value of each label lodged


 a testing file named as test_project.py