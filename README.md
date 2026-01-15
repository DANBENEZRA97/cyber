# Introduction To Cyber Security - Queue Management System - Manual Instructions

## Requirements

- Python 3.10+ (מומלץ)

## How to Run:

1. Clone The repository to folder of your own choice
2. Run: 
   python main.py

## GUI - Controls and Events  

Controls:

- Entry: Customer ID (Input)
- Entry: Full Name (Input)
- Entry: Phone (Input)
- Entry: Priority (Input)
- Combobox: Service (Choice)
- Button: Create Ticket (Button)
- Button: Call Next (Button)
- Button: Finish Selected (Button)
- Button: Cancel Selected (Button)
- Listbox: Queue list
- Text: Ticket Info / Audit Log

Events:

- User Tab:
1. fill the fields and "Join Queue" will sign to Queue.

- Admin Tab:
1. fill the fields and "Create Ticket" will sign to Queue.
2. Double-Click on user will display hi's information (Audit).
3. Update the priority of customers by changing the Box value (0/1), click the exact customer, 'Set Priority'.
4. Call Next, Finish, Cancel.