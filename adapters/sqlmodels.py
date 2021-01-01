from sqlalchemy import Table, MetaData, Column, Integer, Float, String, Date,  ForeignKey
from sqlalchemy.orm import mapper, relationship

from domain import core

metadata = MetaData()

group_table = Table(
    'group', metadata,
    Column('group_id', String(255), primary_key = True),
    Column('name', String(255)),
    Column('parent_reference', String(255)),
    Column('individual_debt_limit', Float),
    Column('individual_credit_limit', Float),
)

member_table = Table(
    'member', metadata,
    Column('member_id', String(255), primary_key = True),
    Column('name', String(255)),
    Column('group', String(255)),
)


tx_table = Table(
    'transaction_', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('group_id', String(255)),
    Column('from_member', String(255)),
    Column('to_member', String(255)),
    Column('amount', Float),
)

def start_mappers():
    tx_mapper = mapper(core.Transaction, tx_table)
    member_mapper = mapper(core.Group, group_table)
    group_mapper = mapper(core.Member, member_table)
