import domain.core as core

class SQLRepository:
    def __init__(self, session):
        self.session = session
        
    def addGroup(self, group):
        self.session.add(group)
        self.session.commit()
        
    def getGroup(self, group_id):
        return self.session.query(core.Group).filter_by(group_id = group_id).one()
    
    def addMember(self, member):
        self.session.add(member)
        self.session.commit()

    def getMember(self, group_id, member_id):
        return self.session.query(core.Member).filter_by(member_id = member_id, group = group_id).one()
                
    def addTx(self, group, mA, mB, amount):
        mA.setbalance(self.getMemberBalance(mA))
        mB.setbalance(self.getMemberBalance(mB))
        tx = core.make_valid_transaction(group, mA, mB, amount)
        if tx is None:
            return
        # if all goes well;
        mA.setbalance(mA.getbalance()+amount)
        mA.setbalance(mA.getbalance()-amount)
        
        self.session.add(tx)
        self.session.commit()

    def getMemberBalance(self, member):
        balances = next(self.session.execute(
        "SELECT " + 
            f"(SELECT COALESCE(SUM(amount), 0) FROM transaction_ WHERE group_id = :group AND from_member = :member) as credit, " +
            f"(SELECT COALESCE(SUM(amount), 0) FROM transaction_ WHERE group_id = :group AND to_member = :member) as debit",
            dict(group = member.group, member = member.member_id)
        ))
        
        return balances.credit - balances.debit