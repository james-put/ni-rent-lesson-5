import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.manager import Manager
from src.models import Parameters
from src.models import Bill

def exercise_1():
    parameters = Parameters()
    manager = Manager(parameters)
    
    assert manager.get_apartment_costs('A1', 2024, 3) == 450.0
    
    assert manager.get_apartment_costs('apart-polanka', 2026, 3) == 450.0
    
    assert manager.get_apartment_costs('apart-polanka', 2024, 3) == 450.0

def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0
    

if __name__ == '__main__':
    print('Some tests.')
    print(exercise_1())