from sqlalchemy import Column, ForeignKey, String, Uuid, UUID
from sqlalchemy.orm import relationship
from core.database.base import Base


class M2MAffectedVersions(Base):
    __tablename__ = "affectedversions"
    id = Column(Uuid, primary_key=True, nullable=False)
    affected = Column(Uuid, ForeignKey("CNAAffected.id"), primary_key=True)
    version = Column(Uuid, ForeignKey("CNAAffectedVersion.id"), primary_key=True)

class CNAAffectedVersion(Base):
    id = Column(Uuid, primary_key=True, nullable=False)
    status = Column(String)
    version = Column(String)
    versions = relationship("CNAAffected", secondary="M2MAffectedVersions", back_populates="versions")

class CNAAffected(Base):
    id = Column(Uuid, primary_key=True, nullable=False)

    product = Column(String)
    vendor = Column(String)
    versions = relationship("CNAAffectedVersion", secondary="M2MAffectedVersions", back_populates="versions")

class M2MCNAAffected(Base):
    pass

class CNA(Base):
    id = Column(Uuid, primary_key=True, nullable=False)
    affected: list[TypedCNAAffected]
    # descriptions: list[TypedCNADescription]
    # problemTypes: list[TypedCNAProblemType]
    # providerMetadata: TypedProviderMetadata
    # references: list[TypedCNAReference]
    # x_legacyV4Record: TypedCNAXLegacyV4Record

class CVEContainer(Base):
    id = Column(Uuid, primary_key=True, nullable=False)
    cna = Column(CNA, ForeignKey("CNA.id"), nullable=False)
    # adp: list[TypedADP]

class CVEMetadata(Base):
    id = Column(Uuid, primary_key=True, nullable=False)
    assignerOrgId = Column(String)
    assignerShortName = Column(String)
    cveId = Column(String)
    datePublished = Column(String)
    dateReserved = Column(String)
    dateUpdated = Column(String)
    state = Column(String)

class CVE(Base):
    id = Column(Uuid, primary_key=True, nullable=False)
    containers_id = Column(Uuid, ForeignKey("CVEContainer.id"), nullable=False)
    cveMetadata_id = Column(Uuid, ForeignKey("CVEMetadata.id",), nullable=False)
    dataType = Column(String)
    dataVersion = Column(String)