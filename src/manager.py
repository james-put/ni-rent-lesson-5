from src.models import Apartment, Bill, Parameters, Tenant, Transfer


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
    
    def get_apartment_costs(self, apartment_key="default", year=0, month=0):
        cost=0.00
        
        if apartment_key not in self.apartments:
            return cost
        for bill in self.bills:
            if bill.apartment == apartment_key and bill.settlement_year==year and bill.settlement_month==month:
                cost+=bill.amount_pln
        for tenant in self.tenants.values():
            from_year, from_month = map(int, tenant.date_agreement_from.split('-')[:2])
            to_year, to_month = map(int, tenant.date_agreement_to.split('-')[:2])
            
            if tenant.apartment == apartment_key and from_year <= year <= to_year and from_month <= month <= to_month:
                cost+=tenant.rent_pln
        return cost