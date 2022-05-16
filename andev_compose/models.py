import sqlalchemy as sa
import sqlalchemy.ext.declarative as sa_declarative

Base = sa_declarative.declarative_base()

class Device(Base):
    __tablename__ = "devices"

    id = sa.Column(sa.BigInteger, primary_key=True)
    dev_id = sa.Column(sa.String(200), nullable=False)
    dev_type = sa.Column(sa.String(120), nullable=False)

class Endpoint(Base):
    __tablename__ = "endpoints"

    id = sa.Column(sa.BigInteger, primary_key=True)
    device_id = sa.Column(sa.Integer, sa.ForeignKey("devices.id", onupdate="CASCADE", ondelete="CASCADE"))
    comment = sa.Column(sa.String)