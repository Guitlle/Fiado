from dataclasses import dataclass

class MissingValue(Exception):
    """An attempt to get a value that is missing or unknown has occurred
    """
    pass

class GroupsDontMatch(Exception):
    """A transaction in different groups
    """
    pass

class TxExceedsLimits(Exception):
    def __init__(self, limit, amount):
        self.limit = limit
        self.amount = amount
        
    def __str__(self):
        return "Limit: " + str(self.limit) + ", Amount: " + str(self.amount)

class Group:
    def __init__(self, group_id: str, name: str, parent_reference: str = "",
                 individual_debt_limit: float = -1e2, 
                 individual_credit_limit: float = 1e2):
        self.group_id = group_id
        self.name = name
        self.individual_debt_limit = individual_debt_limit
        self.individual_credit_limit = individual_credit_limit
        self.parent_reference = parent_reference

class Member:
    def __init__(self, member_id: str, name: str, group: str):
        self.member_id = member_id
        self.name = name
        self.group = group
        self._balance = None

    def getbalance(self):
        """balance must be set by querying the repository
        """
        if self._balance is None:
            raise MissingValue
        return self._balance
                        
    def setbalance(self, balance: float):
        self._balance = balance

@dataclass()
class Transaction:
    group_id: str
    from_member: str
    to_member: str
    amount: float

def make_valid_transaction(group: Group, from_member: Member, to_member: Member, 
                     amount: float):
    """check if tx complies with the limits defined in the group.

       amount must be positive
    """
    if amount <= 0:
        raise ValueError
    if from_member.member_id == to_member.member_id:
        return None
    if from_member.group != to_member.group and from_member.group != group.group_id:
        raise GroupsDontMatch
        
    newfrombalance = from_member.getbalance() + amount
    if group.individual_credit_limit < newfrombalance:
        raise TxExceedsLimits(group.individual_credit_limit, newfrombalance)
    newtobalance = to_member.getbalance() - amount
    
    if newtobalance < group.individual_debt_limit:
        raise TxExceedsLimits(group.individual_debt_limit, newtobalance)

    return Transaction(group.group_id, from_member.member_id,
                       to_member.member_id, amount)