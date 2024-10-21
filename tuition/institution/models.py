from sqlalchemy import Column, DateTime, String, Text, ForeignKey, Numeric, DateTime, func, CHAR, CheckConstraint, Table
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Text, Boolean

from tuition.database import Base

class Institution(Base):
    __tablename__ = 'institutions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    role = Column(String, nullable=False, default='user')
    name_of_institution = Column(String(255), nullable=False)
    type_of_institution = Column(String(255), nullable=False)
    website = Column(Text)
    address = Column(Text)
    email = Column(Text, unique=True, nullable=False)
    country = Column(String, nullable=False)
    official_name = Column(String, nullable=False)
    brief_description = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    hashed_password = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # timezone-aware
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # timezone-aware

    sub_accounts = relationship('SubAccount', back_populates='institution')
    programs = relationship('Program', back_populates='institution')
    # transactions = relationship('Transaction', back_populates='institution')


class SubAccount(Base):
    __tablename__ = 'sub_accounts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    institution_id = Column(UUID, ForeignKey('institutions.id'))
    subaccount_id = Column(String, unique=True, default= None)
    account_name = Column(String(255), nullable=False)
    account_number = Column(String, nullable=False)
    account_email = Column(String)
    account_type = Column(String)
    country = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    split_type = Column(String)  # percentage or flat
    split_value = Column(Numeric)

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # timezone-aware
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # timezone-aware

    institution = relationship('Institution', back_populates='sub_accounts')

program_category_association = Table(
    'program_category_association',
    Base.metadata,
    Column('program_id', UUID(as_uuid=True), ForeignKey('programs.id')),
    Column('category_id', UUID(as_uuid=True), ForeignKey('categories.id'))
)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, unique=True)

    programs = relationship(
        'Program', 
        secondary=program_category_association, 
        back_populates='categories'
    )

class Program(Base):
    __tablename__ = 'programs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    program_level = Column(String(255), nullable=False)
    name_of_program = Column(String(255), nullable=False)
    institution_id = Column(UUID, ForeignKey('institutions.id'))
    application_deadline = Column(DateTime(timezone=True), nullable=True)
    always_available = Column(Boolean, default=False)
    description = Column(Text)
    cost = Column(Numeric(12, 2), nullable=True)
    subaccount_id = Column(String)
    is_free = Column(Boolean, default=False)
    currency_code = Column(CHAR(3), nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    institution = relationship("Institution", back_populates='programs')
    categories = relationship(
        'Category', 
        secondary=program_category_association, 
        back_populates='programs'
    )

    __table_args__ = (
        CheckConstraint(
            "(application_deadline > now()) OR (application_deadline IS NULL)", 
            name="check_application_deadline_future"
        ),
    )




# class Category(Base):
#     __tablename__ = 'categories'

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
#     name = Column(String(255), nullable=False, unique=True)

#     programs = relationship('Program', back_populates='category')
    

# class Program(Base):
#     __tablename__ = 'programs'

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
#     program_level = Column(String(255), nullable=False)
#     Category_id = Column(UUID, ForeignKey("categories.id"))

#     name_of_program = Column(String(255), nullable=False)
#     institution_id = Column(UUID, ForeignKey('institutions.id'))
#     # Deadline should be nullable for evergreen programs (always available)
#     application_deadline = Column(DateTime(timezone=True), nullable=True)  # TIMESTAMPTZ equivalent
#     # Boolean to track if the program is always available
#     always_available = Column(Boolean, default=False)
#     description = Column(Text)
#     cost = Column(Numeric(12, 2), nullable=True)
#     subaccount_id = Column(String)
#     is_free = Column(Boolean, default=False)
#     currency_code = Column(CHAR(3), nullable=False)
#     image_url = Column(String, nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())  # timezone-aware
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # timezone-aware

#     institution = relationship("Institution", back_populates='programs')
#     category = relationship("Category", back_populates='programs')

#     __table_args__ = (
#         CheckConstraint(
#             "(application_deadline > now()) OR (application_deadline IS NULL)", 
#             name="check_application_deadline_future"
#         ),
#     )
