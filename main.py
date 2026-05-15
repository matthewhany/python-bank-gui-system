# ==============================
# Advanced Bank System + Simple GUI
# OOP is unchanged - only GUI and RUN part are used
# ==============================

import json
import datetime
import tkinter as tk
from tkinter import messagebox


# ================= VALIDATION =================

def get_float(msg):
    while True:
        try:
            return float(input(msg))
        except:
            print("Invalid input, try again.")


# ================= ACCOUNT =================

class Account:
    bank_name = "Mini Bank"
    account_counter = 1000

    def __init__(self, name, balance, password, account_number=None):
        if account_number:
            self.account_number = account_number
        else:
            Account.account_counter += 1
            self.account_number = Account.account_counter

        self.name = name
        self.__balance = balance
        self.__password = password
        self.transactions = []

    def check_password(self, password):
        return self.__password == password

    def get_balance(self):
        return self.__balance

    def _set_balance(self, value):
        self.__balance = value

    def add_transaction(self, text):
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions.append(f"[{time}] {text}")

    def deposit(self, amount):
        if amount <= 0:
            print("Invalid amount")
            return False

        self.__balance += amount
        self.add_transaction(f"Deposited {amount}")
        return True

    def withdraw(self, amount):
        if amount <= 0 or amount > self.__balance:
            print("Invalid or insufficient balance")
            return False

        self.__balance -= amount
        self.add_transaction(f"Withdrew {amount}")
        return True


# ================= SAVINGS =================

class SavingsAccount(Account):
    def __init__(self, name, balance, password, interest_rate, account_number=None):
        super().__init__(name, balance, password, account_number)
        self.interest_rate = interest_rate

    def add_interest(self):
        interest = self.get_balance() * self.interest_rate
        self.deposit(interest)


# ================= CURRENT =================

class CurrentAccount(Account):
    def __init__(self, name, balance, password, overdraft_limit, account_number=None):
        super().__init__(name, balance, password, account_number)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if amount <= 0:
            print("Invalid amount")
            return False

        if amount > self.get_balance() + self.overdraft_limit:
            print("Overdraft limit exceeded")
            return False

        new_balance = self.get_balance() - amount
        self._set_balance(new_balance)
        self.add_transaction(f"Withdrew {amount}")
        return True


# ================= BUSINESS =================

class BusinessAccount(Account):
    def __init__(self, name, balance, password, company_name, fee, account_number=None):
        super().__init__(name, balance, password, account_number)
        self.company_name = company_name
        self.fee = fee

    def withdraw(self, amount):
        total = amount + self.fee

        if total > self.get_balance():
            print("Insufficient balance")
            return False

        self._set_balance(self.get_balance() - total)
        self.add_transaction(f"Withdrew {amount} (Fee {self.fee})")
        return True


# ================= BANK SYSTEM =================

class BankSystem:
    def __init__(self):
        self.accounts = []
        self.load_data()

    def save_data(self):
        data = []

        for acc in self.accounts:
            base = {
                "type": acc.__class__.__name__,
                "account_number": acc.account_number,
                "name": acc.name,
                "balance": acc.get_balance(),
                "password": acc._Account__password,
                "transactions": acc.transactions
            }

            if isinstance(acc, SavingsAccount):
                base["interest_rate"] = acc.interest_rate

            elif isinstance(acc, CurrentAccount):
                base["overdraft_limit"] = acc.overdraft_limit

            elif isinstance(acc, BusinessAccount):
                base["company_name"] = acc.company_name
                base["fee"] = acc.fee

            data.append(base)

        with open("bank_data.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        try:
            with open("bank_data.json", "r") as f:
                data = json.load(f)

                max_acc = 1000

                for item in data:
                    t = item["type"]

                    if t == "SavingsAccount":
                        acc = SavingsAccount(
                            item["name"],
                            item["balance"],
                            item["password"],
                            item["interest_rate"],
                            item["account_number"]
                        )

                    elif t == "CurrentAccount":
                        acc = CurrentAccount(
                            item["name"],
                            item["balance"],
                            item["password"],
                            item["overdraft_limit"],
                            item["account_number"]
                        )

                    elif t == "BusinessAccount":
                        acc = BusinessAccount(
                            item["name"],
                            item["balance"],
                            item["password"],
                            item["company_name"],
                            item["fee"],
                            item["account_number"]
                        )

                    else:
                        acc = Account(
                            item["name"],
                            item["balance"],
                            item["password"],
                            item["account_number"]
                        )   

                    acc.transactions = item.get("transactions", [])
                    self.accounts.append(acc)

                    if acc.account_number > max_acc:
                        max_acc = acc.account_number

                Account.account_counter = max_acc

        except:
            pass

    def find_account(self, number):
        for acc in self.accounts:
            if acc.account_number == number:
                return acc
        return None

    def login(self):
        num = int(input("Account Number: "))
        password = input("Password: ")

        acc = self.find_account(num)

        if acc and acc.check_password(password):
            print("Login successful")
            return acc

        print("Invalid credentials")
        return None

    def transfer(self, sender):
        to = int(input("Receiver account number: "))
        amount = get_float("Amount: ")

        receiver = self.find_account(to)

        if not receiver:
            print("Receiver not found")
            return

        if sender.get_balance() < amount:
            print("Insufficient balance")
            return

        sender.withdraw(amount)
        receiver.deposit(amount)

        sender.add_transaction(f"Transferred {amount} to {receiver.account_number}")
        receiver.add_transaction(f"Received {amount} from {sender.account_number}")

        print("Transfer complete")

    def create_account(self):
        name = input("Name: ")
        balance = get_float("Balance: ")
        password = input("Password: ")

        print("1 Savings | 2 Current | 3 Business")
        choice = input("Choose: ")

        if choice == "1":
            rate = get_float("Interest rate: ")
            acc = SavingsAccount(name, balance, password, rate)

        elif choice == "2":
            limit = get_float("Overdraft limit: ")
            acc = CurrentAccount(name, balance, password, limit)

        else:
            company = input("Company name: ")
            fee = get_float("Fee: ")
            acc = BusinessAccount(name, balance, password, company, fee)

        self.accounts.append(acc)
        self.save_data()

        print("Account created. Number:", acc.account_number)


# ================= GUI =================

class BankGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Bank")

        # This makes the window open maximized on laptop/PC screen
        self.root.state("zoomed")

        self.bank = BankSystem()
        self.current_user = None

        self.account_type = tk.StringVar(value="Savings")
        self.show_password = tk.IntVar(value=0)

        self.build_gui()

    def build_gui(self):
        self.user_label = tk.Label(
            self.root,
            text="No user logged in",
            font=("Arial", 12, "bold")
        )
        self.user_label.pack(fill="x", pady=5)

        # ============ Create Account ============

        create_frame = tk.LabelFrame(self.root, text="Create Account", padx=8, pady=8)
        create_frame.pack(fill="x", padx=8, pady=5)

        tk.Label(create_frame, text="Name", width=12, anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        self.name_entry = tk.Entry(create_frame, width=28)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=4)

        tk.Label(create_frame, text="Balance", width=12, anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        self.balance_entry = tk.Entry(create_frame, width=28)
        self.balance_entry.grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(create_frame, text="Password", width=12, anchor="w").grid(row=2, column=0, sticky="w", pady=4)
        self.password_entry = tk.Entry(create_frame, width=28, show="*")
        self.password_entry.grid(row=2, column=1, sticky="w", pady=4)

        tk.Checkbutton(
            create_frame,   
            text="Show Password",
            variable=self.show_password,
            command=self.toggle_password
        ).grid(row=3, column=1, sticky="w", pady=4)

        tk.Label(
            create_frame,
            text="Account Type",
            font=("Arial", 10, "bold")
        ).grid(row=4, column=0, sticky="w", pady=8)

        radio_frame = tk.Frame(create_frame)
        radio_frame.grid(row=5, column=0, columnspan=2, sticky="w")

        tk.Radiobutton(
            radio_frame,
            text="Savings",
            variable=self.account_type,
            value="Savings"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            radio_frame,
            text="Current",
            variable=self.account_type,
            value="Current"
        ).pack(side="left", padx=30)

        tk.Radiobutton(
            radio_frame,
            text="Business",
            variable=self.account_type,
            value="Business"
        ).pack(side="left", padx=30)

        tk.Button(
            create_frame,
            text="Create Account",
            command=self.create_account,
            bg="#2a9d8f",
            fg="white",
            width=22
        ).grid(row=6, column=0, columnspan=6, pady=12)

        # ============ Login ============

        login_frame = tk.LabelFrame(self.root, text="Login", padx=8, pady=8)
        login_frame.pack(fill="x", padx=8, pady=5)

        tk.Label(login_frame, text="Account Number", width=13, anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        self.login_number_entry = tk.Entry(login_frame, width=28)
        self.login_number_entry.grid(row=0, column=1, sticky="w", pady=4)

        tk.Label(login_frame, text="Password", width=13, anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        self.login_password_entry = tk.Entry(login_frame, width=28, show="*")
        self.login_password_entry.grid(row=1, column=1, sticky="w", pady=4 )

        tk.Button(
            login_frame,
            text="Login",
            command=self.login,
            bg="#457b9d",
            fg="white",
            width=14
        ).grid(row=2, column=0, pady=6)

        tk.Button(
            login_frame,
            text="Logout",
            command=self.logout,
            bg="#e76f51",
            fg="white",
            width=14
        ).grid(row=2, column=1, sticky="w", pady=6)

        # ============ Operations ============

        operation_frame = tk.LabelFrame(self.root, text="Operations", padx=8, pady=8)
        operation_frame.pack(fill="x", padx=8, pady=5)

        tk.Label(operation_frame, text="Amount", width=12, anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        self.amount_entry = tk.Entry(operation_frame, width=28)
        self.amount_entry.grid(row=0, column=1, sticky="w", pady=4)

        tk.Button(
            operation_frame,
            text="Deposit",
            command=self.deposit,
            bg="#2a9d8f",
            fg="white",
            width=14
        ).grid(row=1, column=0, pady=8)

        tk.Button(
            operation_frame,
            text="Withdraw",
            command=self.withdraw,
            bg="#f4a261",
            fg="white",
            width=14
        ).grid(row=1, column=1, sticky="w", pady=8)

        tk.Button(
            operation_frame,
            text="Show Balance",
            command=self.show_balance,
            bg="#264653",
            fg="white",
            width=14
        ).grid(row=1, column=2, padx=8, pady=8)

        tk.Button(
            operation_frame,
            text="Delete Account",
            command=self.delete_account,
            bg="#d62828",
            fg="white",
            width=14
        ).grid(row=1, column=3, padx=8, pady=8)

        # ============ Result ============

        result_frame = tk.LabelFrame(self.root, text="Result", padx=5, pady=5)
        result_frame.pack(fill="x", padx=8, pady=5)

        self.result_label = tk.Label(
            result_frame,
            text="Welcome to Simple Bank",
            bg="#eef8ee",
            fg="#1d3557",
            font=("Arial", 12, "bold"),
            height=2,
            relief="solid",
            bd=1
        )
        self.result_label.pack(fill="x")

        # ============ Output with Scrollbar ============

        output_frame = tk.LabelFrame(self.root, text="Output", padx=5, pady=5)
        output_frame.pack(fill="both", expand=True, padx=8, pady=5)

        text_frame = tk.Frame(output_frame)
        text_frame.pack(fill="both", expand=True)

        self.output_text = tk.Text(
            text_frame,
            height=7,
            wrap="word",
            relief="sunken",
            bd=1
        )
        self.output_text.pack(side="left", fill="both", expand=True)

        self.output_scrollbar = tk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self.output_text.yview
        )
        self.output_scrollbar.pack(side="right", fill="y")

        self.output_text.config(yscrollcommand=self.output_scrollbar.set)

        tk.Button(
            output_frame,
            text="Show Transactions",
            command=self.show_transactions,
            bg="#1d3557",
            fg="white",
            width=20
        ).pack(pady=8)

    # ============ Helper Functions ============

    def show_result(self, text):
        self.result_label.config(text=text)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
 
    def toggle_password(self):
        if self.show_password.get() == 1:
            self.password_entry.config(show="")
            self.login_password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
            self.login_password_entry.config(show="*")

    def check_login(self):
        if self.current_user is None:
            self.show_result("Please login first")
            return False
        return True

    def get_amount_from_gui(self):
        try:
            amount = float(self.amount_entry.get())

            if amount <= 0:
                self.show_result("Amount must be greater than zero")
                return None

            return amount

        except:
            self.show_result("Please enter a valid amount")
            return None

    # ============ Button Commands ============

    def create_account(self):
        try:
            name = self.name_entry.get().strip()
            balance = float(self.balance_entry.get())
            password = self.password_entry.get()
            acc_type = self.account_type.get()

            if name == "" or password == "":
                self.show_result("Name and password are required")
                return

            if balance < 0:
                self.show_result("Balance cannot be negative")
                return

            if acc_type == "Savings":
                acc = SavingsAccount(name, balance, password, 0.05)

            elif acc_type == "Current":
                acc = CurrentAccount(name, balance, password, 500)

            else:
                acc = BusinessAccount(name, balance, password, name + " Company", 10)

            self.bank.accounts.append(acc)
            self.bank.save_data()

            self.show_result(f"Account created successfully. Account Number: {acc.account_number}")

        except:
            self.show_result("Please enter a valid balance")

    def login(self):
        try:
            number = int(self.login_number_entry.get())
            password = self.login_password_entry.get()

            acc = self.bank.find_account(number)

            if acc and acc.check_password(password):
                self.current_user = acc
                self.user_label.config(text=f"Logged in: {acc.name} | Account #{acc.account_number}")
                self.show_result("Login successful")
            else:
                self.show_result("Invalid account number or password")

        except:
            self.show_result("Account number must be a number")

    def logout(self):
        self.current_user = None
        self.user_label.config(text="No user logged in")
        self.show_result("Logged out")

    def deposit(self):
        if not self.check_login():
            return

        amount = self.get_amount_from_gui()

        if amount is None:
            return

        ok = self.current_user.deposit(amount)

        if ok:
            self.bank.save_data()
            self.show_result(f"Deposited {amount}. Balance: {self.current_user.get_balance()}")
        else:
            self.show_result("Deposit failed")

    def withdraw(self):
        if not self.check_login():
            return

        amount = self.get_amount_from_gui()

        if amount is None:
            return

        ok = self.current_user.withdraw(amount)

        if ok:
            self.bank.save_data()
            self.show_result(f"Withdrew {amount}. Balance: {self.current_user.get_balance()}")
        else:
            self.show_result("Withdraw failed")

    def show_balance(self):
        if not self.check_login():
            return

        self.show_result(f"Current Balance: {self.current_user.get_balance()}")

    def show_transactions(self):
        if not self.check_login():
            return

        self.output_text.delete("1.0", tk.END)

        if len(self.current_user.transactions) == 0:
            self.output_text.insert(tk.END, "No transactions\n")
        else:
            for trans in self.current_user.transactions:
                self.output_text.insert(tk.END, trans + "\n")

        self.output_text.see(tk.END)
        self.result_label.config(text="Transactions displayed")

    def delete_account(self):
        if not self.check_login():
            return

        answer = messagebox.askyesno(
            "Confirm",
            "Are you sure you want to delete this account?"
        )

        if answer:
            self.bank.accounts.remove(self.current_user)
            self.bank.save_data()
            self.current_user = None
            self.user_label.config(text="No user logged in")
            self.show_result("Account deleted successfully")


# ================= RUN GUI =================

root = tk.Tk()
app = BankGUI(root)
root.mainloop()