import base64
import csv
import datetime
import random
import uuid
from collections import namedtuple
from dataclasses import dataclass
from io import StringIO

from dateutil.relativedelta import relativedelta
from faker import Faker

faker = Faker()


@dataclass
class Transaction:
    department_id: int = None                   # Optional. Unsigned
    trans_id: str = None                        # Remote FMS identity
    trans_name: str = None
    trans_post_date: str = None                 # Use YYYY-MM-DD format
    ext_project_id: str = None
    ext_project_name: str = None
    ext_grant_id: str = None
    ext_grant_name: str = None
    account_number: str = None                  # AKA General Ledger Code
    dollar_amount: float = None                 # Omit any currency symbols and numeric separators: [-]999999999999.0000
    trans_perf_period_start_date: str = None    # Optional. Use YYYY-MM-DD format
    trans_perf_period_end_date: str = None      # Optional. Use YYYY-MM-DD format
    dollar_class: str = None                    # A list of transaction classification identifiers like '101,101'
    dollar_trans_number: str = None             # A list of strings like 'Inv 2441,Inv 9211'

    def to_list(self) -> list:
        return [
            self.department_id if self.department_id is not None else "",
            self.trans_id,
            self.trans_name,
            self.trans_post_date,
            self.ext_project_id,
            self.ext_project_name,
            self.ext_grant_id,
            self.ext_grant_name,
            self.account_number,
            self.dollar_amount,
            self.trans_perf_period_start_date if self.trans_perf_period_start_date is not None else "",
            self.trans_perf_period_end_date if self.trans_perf_period_end_date is not None else "",
            self.dollar_class,
            self.dollar_trans_number,
        ]

    @staticmethod
    def header() -> list:
        return [
            "departmentID",
            "transID",
            "transName",
            "transPostDate",
            "extProjectID",
            "extProjectName",
            "extGrantID",
            "extGrantName",
            "accountNumber",
            "dollarAmount",
            "transPerfPeriodStartDate",
            "transPerfPeriodEndDate",
            "dollarClass",
            "dollarTransNumber",
        ]


TransactionClassification = namedtuple("TransactionClassification", ["id", "type", "name", "weight", "default_trans_name"])
TRANS_CLASS = [
    TransactionClassification(101, "expense", "Payroll/Direct Labor", 5, None),
    TransactionClassification(102, "expense", "Indirect Costs", 5, "Administrative Expenses"),
    TransactionClassification(103, "expense", "Payment to Subrecipient", 3, None),
    TransactionClassification(104, "expense", "Payment to Vendor", 2, None),
    TransactionClassification(105, "expense", "Other", 3, "Other Expenses"),
    TransactionClassification(106, "expense", "Encumbrances", 1, "Encumbrance"),
    TransactionClassification(201, "income", "Reimbursement", 5, "Program Reimbursement"),
    TransactionClassification(202, "income", "Advance", 2, "Program Advance"),
    TransactionClassification(203, "income", "Program Income", 2, "Program Income"),
    TransactionClassification(204, "income", "Other", 3, "Other Income"),
]
TRANS_CLASS_WEIGHTS = [trans_class.weight for trans_class in TRANS_CLASS]
FISCAL_YEARS = [datetime.date.today().year - i for i in range(5)]


def generate_transactions(count: int) -> list:
    """
    Generates a mixture of transactions with somewhat realistic data.
    :param count: The number of transactions to generate
    :return: A list of Transaction instances
    """
    transactions = list()
    for _ in range(count):
        transaction_class = random.choices(TRANS_CLASS, weights=TRANS_CLASS_WEIGHTS, k=1)[0]
        transaction = Transaction()
        transaction.trans_id = faker.ean13()
        transaction.trans_post_date = make_random_trans_post_date()
        if random.choice([True, False]):
            set_trans_perf_dates(transaction)
        if transaction_class.id == 101:
            transaction.trans_name = f"Payroll: {faker.name()}"
            transaction.dollar_amount = round(random.uniform(500.00, 5000.00), 2)
        elif transaction_class.id == 103:
            transaction.trans_name = f"Subrecipient Payment: {faker.name()}"
        elif transaction_class.id == 104:
            transaction.trans_name = f"Vendor Payment: {faker.company()}"
        else:
            transaction.trans_name = transaction_class.default_trans_name
            transaction.dollar_amount = round(random.uniform(1000.00, 50000.00), 2)
        transaction.ext_project_id = "N/A"
        transaction.ext_project_name = ""
        transaction.ext_grant_id = str(base64.standard_b64encode(uuid.uuid4().bytes), "utf-8")
        transaction.ext_grant_name = f"Project Grant {faker.first_name()} FY{random.choice(FISCAL_YEARS)}"
        if transaction_class.type == "expense":
            transaction.account_number = f"6{faker.ean8()}"
        elif transaction_class.type == "income":
            transaction.account_number = f"4{faker.ean8()}"
        transaction.dollar_class = str(transaction_class.id)
        transaction.dollar_trans_number = str(random.randrange(1000, 9999))
        transactions.append(transaction)
    return transactions


def transactions_as_csv(transactions: list) -> str:
    """
    Compose CSV content from a list of transactions
    """
    handle = StringIO()
    writer = csv.writer(handle)
    writer.writerow(Transaction.header())
    for transaction in transactions:
        writer.writerow(transaction.to_list())
    return handle.getvalue()


def set_trans_perf_dates(transaction: Transaction) -> None:
    """
    Use the trans_post_date as a clue for the appropriate performance period.
    It should be a few months ago until the end of the month prior to the post date.
    :param transaction: The transaction will be filled
    """
    end_of_performance_period = datetime.date.fromisoformat(transaction.trans_post_date).replace(day=1) - datetime.timedelta(days=1)
    start_of_performance_period = end_of_performance_period.replace(day=1) - relativedelta(months=random.randint(1, 7))
    transaction.trans_perf_period_start_date = start_of_performance_period.isoformat()
    transaction.trans_perf_period_end_date = end_of_performance_period.isoformat()


def make_random_id() -> str:
    result = ""
    for _ in range(10):
        result += str(random.randrange(0, 10))
    return result


def make_random_trans_post_date() -> str:
    trans_date = faker.date_between(datetime.date(2010, 1, 1), datetime.date.today())
    return trans_date.isoformat()
