import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.manager import Manager
from src.models import Parameters, Bill, Apartment, Tenant


def test_exercise_1():
    parameters = Parameters()
    manager = Manager(parameters)
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-04-15',
        settlement_year=2024,
        settlement_month=3,
        amount_pln=450.0,
        type='rent'
    ))
    
    assert manager.get_apartment_costs('A1', 2024, 3) is None
    assert manager.get_apartment_costs('apart-polanka', 2026, 3) == 0.0
    assert manager.get_apartment_costs('apart-polanka', 2024, 3) == 450.0


def test_invalid_month():
    parameters = Parameters()
    manager = Manager(parameters)

    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', 2024, 13)
    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', 2024, 0)


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


def test_apartment_settlement():
    parameters = Parameters()
    manager = Manager(parameters)
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1000.0,
        type='rent'
    ))
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-20',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=250.0,
        type='electricity'
    ))

    settlement = manager.create_apartment_settlement('apart-polanka', 2024, 2)
    assert settlement is not None
    assert settlement.apartment == 'apart-polanka'
    assert settlement.year == 2024
    assert settlement.month == 2
    assert settlement.total_bills_pln == 1250.0
    assert settlement.total_due_pln == 1250.0

    empty_settlement = manager.create_apartment_settlement('apart-polanka', 2024, 6)
    assert empty_settlement is not None
    assert empty_settlement.apartment == 'apart-polanka'
    assert empty_settlement.total_bills_pln == 0.0
    assert empty_settlement.total_due_pln == 0.0

    none_settlement = manager.create_apartment_settlement('A1', 2024, 2)
    assert none_settlement is None


def test_tenant_settlements():
    parameters = Parameters()
    manager = Manager(parameters)

    manager.apartments = {
        'apt-2': Apartment(key='apt-2', name='Apt 2', location='Poznan', area_m2=50.0, rooms={}),
        'apt-1': Apartment(key='apt-1', name='Apt 1', location='Poznan', area_m2=30.0, rooms={}),
        'apt-0': Apartment(key='apt-0', name='Apt 0', location='Poznan', area_m2=40.0, rooms={})
    }
    manager.tenants = {
        't1': Tenant(name='Jan', apartment='apt-2', room='r1', rent_pln=1000.0, deposit_pln=1000.0, date_agreement_from='2024-01-01', date_agreement_to='2024-12-31'),
        't2': Tenant(name='Anna', apartment='apt-2', room='r2', rent_pln=1000.0, deposit_pln=1000.0, date_agreement_from='2024-01-01', date_agreement_to='2024-12-31'),
        't3': Tenant(name='Piotr', apartment='apt-1', room='r1', rent_pln=1500.0, deposit_pln=1500.0, date_agreement_from='2024-01-01', date_agreement_to='2024-12-31')
    }
    manager.bills = [
        Bill(apartment='apt-2', date_due='2024-03-10', settlement_year=2024, settlement_month=2, amount_pln=600.0, type='electricity'),
        Bill(apartment='apt-1', date_due='2024-03-10', settlement_year=2024, settlement_month=2, amount_pln=500.0, type='rent'),
        Bill(apartment='apt-0', date_due='2024-03-10', settlement_year=2024, settlement_month=2, amount_pln=400.0, type='rent')
    ]

    s2 = manager.create_apartment_settlement('apt-2', 2024, 2)
    t_s2 = manager.create_tenant_settlements(s2)
    assert len(t_s2) == 2
    assert t_s2[0].year == 2024
    assert t_s2[0].month == 2
    assert t_s2[0].bills_pln == 300.0
    assert t_s2[1].bills_pln == 300.0
    assert t_s2[0].balance_pln == -300.0

    s1 = manager.create_apartment_settlement('apt-1', 2024, 2)
    t_s1 = manager.create_tenant_settlements(s1)
    assert len(t_s1) == 1
    assert t_s1[0].tenant == 't3'
    assert t_s1[0].bills_pln == 500.0
    assert t_s1[0].balance_pln == -500.0

    s0 = manager.create_apartment_settlement('apt-0', 2024, 2)
    t_s0 = manager.create_tenant_settlements(s0)
    assert len(t_s0) == 0