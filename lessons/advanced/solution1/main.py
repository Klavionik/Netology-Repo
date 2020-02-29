from datetime import datetime

from lessons.advanced.solution1.application.db.people import get_employees
from lessons.advanced.solution1.application.salary import calculate_salary

if __name__ == '__main__':
    print(datetime.today().date())
    get_employees()
    calculate_salary()
