from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric

from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Boolean
from tuition.database import Base


class Institution(Base):

    __tablename__ = 'institutions'

    id = Column(Integer, primary_key=True, index=True)
    name_of_institution = Column(String, nullable=False)
    type_of_institution = Column(String, nullable=False)
    website = Column(Text)
    account_id = Column(String)
    address = Column(Text)
    email = Column(Text, unique=True, nullable=False)
    country = Column(String, nullable=False)
    official_name = Column(String, nullable=False)
    brief_description = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # transactions = relationship('Transaction', back_populates='institutions')
    sub_accounts = relationship('SubAccount', back_populates='institution')
    programs = relationship('Program', back_populates='institution')

    def __repr__(self):
        return f"<Institution {self.name_of_institution}>"
    



# class Transaction(Base):
#     __tablename__ = 'transactions'

#     id = Column(Integer, primary_key=True, index=True)
#     student_id = Column(Integer, ForeignKey('students.id'))
#     institution_id = Column(Integer, ForeignKey('institutions.id'))
#     amount = Column(Numeric, nullable=False)
#     currency = Column(String, nullable=False)
#     status = Column(String, default='Pending')
#     transaction_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
#     flw_transaction_id = Column(String, nullable=True)



class SubAccount(Base):
    __tablename__ = 'sub_accounts'

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey('institutions.id'))
    subaccount_id = Column(String, unique=True)
    account_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    account_email = Column(String)
    account_type = Column(String)
    country = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    split_type = Column(String)  # percentage or flat
    split_value = Column(Numeric)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    institution = relationship('Institution', back_populates='sub_accounts')



class Program(Base):
    __tablename__ = 'programs'
    
    id = Column(Integer, primary_key=True, index=True)
    name_of_program = Column(String, nullable=False)
    institution_id = Column(Integer, ForeignKey('institutions.id'))
    application_deadline = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    description = Column(String)
    cost = Column(Numeric)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    institution = relationship("Institution", back_populates='programs')
