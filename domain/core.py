from dataclasses import dataclass

class TxStatus:
    TxRequested = "Req"
    TxAccepted = "Acc"

class NotMyTransaction(Exception):
    """Member can't accept a transaction involving other members
    """
    pass

class CantAcceptTx(Exception):
    """Member can't accept request (it is not supposed to accept it)
    """
    pass


class MissingValue(Exception):
    """An attempt to get a value that is missing or unknown has occurred
    """
    pass

class GroupsDontMatch(Exception):
    """A transaction in different groups
    """
    pass

class TxSameUser(Exception):
    """Transaction with same user from to
    """
    pass

class TxExceedsLimits(Exception):
    def __init__(self, limit, amount):
        self.limit = limit
        self.amount = amount

    def __str__(self):
        return "Limit: " + str(self.limit) + ", Exceeding Amount: " + str(self.amount)

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
    def __init__(self, member_id: str, name: str, group: Group):
        self.member_id = member_id
        self.name = name
        self.group = group.group_id
        self.group_obj = group
        self._balance = None

    def __eq__(self, second):
        return self.member_id == second.member_id

    def getbalance(self):
        """balance must be set by querying the repository
        """
        if self._balance is None:
            raise MissingValue
        return self._balance

    def setbalance(self, balance: float):
        self._balance = balance

    def request_receive_credit(self, from_member, amount):
        tx = Transaction(self.group_obj, from_member, self, amount,
                            accepter_id = from_member.member_id)
        if check_valid_transaction_request(tx):
            return tx

    def request_give_credit(self, to_member, amount):
        tx = Transaction(self.group_obj, self, to_member, amount,
                            accepter_id = to_member.member_id)
        if check_valid_transaction_request(tx):
            return tx

    def accept_tx(self, tx):
        if tx.from_member_obj != self and tx.to_member_obj != self:
            raise NotMyTransaction
        if tx.accepter_id != self.member_id:
            raise CantAcceptTx
        if check_valid_transaction_request(tx):
            tx.status = TxStatus.TxAccepted
        return tx


class Transaction:
    group_id: str
    from_member: str
    to_member: str
    amount: float
    status: str
    accepter_id: str

    def __init__(self, group, from_m, to_m, amount, accepter_id = None):
        if from_m.group != to_m.group:
            raise GroupsDontMatch
        if from_m == to_m:
            raise TxSameUser
        if amount <= 0:
            raise ValueError

        self.group_id = group.group_id
        self.group_obj = group
        self.from_member = from_m.member_id
        self.from_member_obj = from_m
        self.to_member = to_m.member_id
        self.to_member_obj = to_m
        self.amount = amount
        self.status = TxStatus.TxRequested
        self.accepter_id = accepter_id

def check_valid_transaction_request(tx):
    """check if tx complies with the limits defined in the group.
    """
    newfrombalance = tx.from_member_obj.getbalance() + tx.amount
    if tx.group_obj.individual_credit_limit < newfrombalance:
        raise TxExceedsLimits(tx.group_obj.individual_credit_limit, newfrombalance)

    newtobalance = tx.to_member_obj.getbalance() - tx.amount
    if newtobalance < tx.group_obj.individual_debt_limit:
        raise TxExceedsLimits(tx.group_obj.individual_debt_limit, newtobalance)

    return True
