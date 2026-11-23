from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, TenantSettlement, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
    
    def get_apartment_costs(self, apartment_key, year=None, month=None):
        if apartment_key not in self.apartments:
            return None

        if month is not None and (month < 1 or month > 12):
            raise ValueError("Invalid month")

        cost = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key:
                if year is None and month is None:
                    cost += bill.amount_pln
                elif month is None and bill.settlement_year == year:
                    cost += bill.amount_pln
                elif bill.settlement_year == year and bill.settlement_month == month:
                    cost += bill.amount_pln
        return cost

    def create_apartment_settlement(self, apartment_key, year, month):
        bills_sum = self.get_apartment_costs(apartment_key, year, month)
        if bills_sum is None:
            return None

        settlement = ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=0.0,
            total_bills_pln=bills_sum,
            total_due_pln=bills_sum
        )
        return settlement

    def create_tenant_settlements(self, apartment_settlement):
        apartment_tenants = []
        for tenant_key, tenant in self.tenants.items():
            if tenant.apartment == apartment_settlement.apartment:
                apartment_tenants.append(tenant_key)

        if len(apartment_tenants) == 0:
            return []

        bills_per_tenant = apartment_settlement.total_bills_pln / len(apartment_tenants)
        settlements = []

        for tenant_key in apartment_tenants:
            settlement = TenantSettlement(
                tenant=tenant_key,
                apartment_settlement=f"{apartment_settlement.apartment}-{apartment_settlement.year}-{apartment_settlement.month}",
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                rent_pln=0.0,
                bills_pln=bills_per_tenant,
                total_due_pln=bills_per_tenant,
                balance_pln=-bills_per_tenant
            )
            settlements.append(settlement)

        return settlements