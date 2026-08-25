import uuid
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

# from enterprise_knowledge_analytics_agent.config import get_settings
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.models import (
    Department,
    Employee,
    ExpenseItem,
    ExpenseReport,
)

NAMESPACE = uuid.UUID("5a9d4b16-1741-4b2e-b75f-92f85b7e34b1")

DEPARTMENTS = [
    ("ENG", "Engineering", "CC-100"),
    ("SALES", "Sales", "CC-200"),
    ("MKT", "Marketing", "CC-300"),
    ("FIN", "Finance", "CC-400"),
    ("HR", "Human Resources", "CC-500"),
    ("OPS", "Operations", "CC-600"),
]

EMPLOYEES = [
    ("Avery", "Morgan"),
    ("Jordan", "Lee"),
    ("Taylor", "Patel"),
    ("Casey", "Rivera"),
    ("Riley", "Chen"),
    ("Morgan", "Davis"),
    ("Cameron", "Brown"),
    ("Quinn", "Wilson"),
    ("Parker", "Martin"),
    ("Reese", "Clark"),
    ("Skyler", "Young"),
    ("Rowan", "Hall"),
]


def stable_id(record_type: str, natural_key: str) -> uuid.UUID:
    """Create the same UUID every time for the same logical record."""

    return uuid.uuid5(NAMESPACE, f"{record_type}:{natural_key}")


def seed_analytics_data() -> dict[str, int]:
    """Insert or update the deterministic synthetic analytics dataset."""

    # settings = get_settings()
    engine = create_database_engine()
    department_ids: list[uuid.UUID] = []
    employee_ids: list[uuid.UUID] = []

    with Session(engine) as session:
        for code, name, cost_center in DEPARTMENTS:
            department_id = stable_id("department", code)
            department_ids.append(department_id)

            session.merge(
                Department(
                    id=department_id,
                    code=code,
                    name=name,
                    cost_center=cost_center,
                    is_active=True,
                )
            )

        for employee_index, (first_name, last_name) in enumerate(EMPLOYEES):
            department_index = employee_index // 2
            department_id = department_ids[department_index]
            employee_number = f"EMP-{employee_index + 1:04d}"
            employee_id = stable_id("employee", employee_number)
            employee_ids.append(employee_id)

            session.merge(
                Employee(
                    id=employee_id,
                    employee_number=employee_number,
                    department_id=department_id,
                    display_name=f"{first_name} {last_name}",
                    job_title="Business Operations Specialist",
                    hire_date=date(2021 + employee_index % 4, 1 + employee_index % 12, 15),
                    employment_status="active",
                    work_email=(f"{first_name}.{last_name}@example.invalid".lower()),
                    annual_salary=Decimal(
                        70_000 + department_index * 5_000 + employee_index % 2 * 2_500
                    ),
                )
            )

        expense_item_count = 0
        expense_report_count = 0

        for employee_index, employee_id in enumerate(employee_ids):
            department_index = employee_index // 2

            for report_cycle in range(2):
                report_number = f"ER-2025-{expense_report_count + 1:04d}"
                report_id = stable_id("expense-report", report_number)
                month = ((expense_report_count * 2) % 12) + 1
                submitted_date = date(
                    2025,
                    month,
                    10 + employee_index % 10,
                )

                session.merge(
                    ExpenseReport(
                        id=report_id,
                        report_number=report_number,
                        employee_id=employee_id,
                        purpose="Synthetic domestic business travel",
                        status="paid",
                        submitted_date=submitted_date,
                        approved_date=submitted_date + timedelta(days=2),
                        trip_start_date=submitted_date - timedelta(days=7),
                        trip_end_date=submitted_date - timedelta(days=3),
                    )
                )

                expenses = [
                    (
                        "airfare",
                        "Example Air",
                        Decimal(250 + department_index * 55 + report_cycle * 30),
                    ),
                    (
                        "hotel",
                        "Example Hotel",
                        Decimal(400 + department_index * 80 + report_cycle * 45),
                    ),
                    (
                        "meals",
                        "Example Restaurant",
                        Decimal(120 + department_index * 15 + report_cycle * 10),
                    ),
                ]

                for category, merchant, amount in expenses:
                    item_key = f"{report_number}:{category}"
                    session.merge(
                        ExpenseItem(
                            id=stable_id("expense-item", item_key),
                            report_id=report_id,
                            expense_date=submitted_date - timedelta(days=5),
                            category=category,
                            merchant=merchant,
                            description=f"Synthetic {category} expense",
                            amount=amount,
                            currency="USD",
                            receipt_provided=True,
                            reimbursable=True,
                        )
                    )
                    expense_item_count += 1

                expense_report_count += 1

        session.commit()

    engine.dispose()

    return {
        "departments": len(DEPARTMENTS),
        "employees": len(EMPLOYEES),
        "expense_reports": expense_report_count,
        "expense_items": expense_item_count,
    }


def main() -> None:
    """Run the analytics seed operation."""

    counts = seed_analytics_data()
    for table_name, count in counts.items():
        print(f"{table_name}: {count}")


if __name__ == "__main__":
    main()
