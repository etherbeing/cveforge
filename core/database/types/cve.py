from dataclasses import dataclass
from typing import Optional, TypedDict


@dataclass
class TypedCNAAffectedVersion(TypedDict):
    status: str
    version: str


@dataclass
class TypedCNAAffected(TypedDict):
    product: str
    vendor: str
    versions: list[TypedCNAAffectedVersion]


@dataclass
class TypedCNADescription(TypedDict):
    lang: str
    value: str


@dataclass
class TypedCNAProblemTypeDescription(TypedDict):
    lang: str
    type: str
    description: str


@dataclass
class TypedCNAProblemType(TypedDict):
    descriptions: list[TypedCNAProblemTypeDescription]


@dataclass
class TypedProviderMetadata(TypedDict):
    dateUpdated: str
    orgId: str
    shortName: str


@dataclass
class TypedCNAReference(TypedDict):
    name: Optional[str]
    tags: list[str]
    url: str


@dataclass
class TypedCNAXLV4RecordDataMeta(TypedDict):
    ASSIGNER: str
    ID: str
    STATE: str


@dataclass
class TypedCNAXLV4DescriptionData(TypedDict):
    lang: str
    value: str


@dataclass
class TypedCNAXLV4Description(TypedDict):
    description_data: list[TypedCNAXLV4DescriptionData]


@dataclass
class TypedCNAXLV4ProblemTypeDataDescription(TypedDict):
    lang: str
    value: str


@dataclass
class TypedCNAXLV4ProblemTypeData(TypedDict):
    description: list[TypedCNAXLV4ProblemTypeDataDescription]


@dataclass
class TypedCNAXLV4ProblemType(TypedDict):
    problemtype_data: list[TypedCNAXLV4ProblemTypeData]


@dataclass
class TypedCNAXLV4ReferenceData(TypedDict):
    refsource: str
    name: str
    url: str


@dataclass
class TypedCNAXLV4Reference(TypedDict):
    reference_data: list[TypedCNAXLV4ReferenceData]


@dataclass
class TypedCNAXLV4AVDPDVersionData(TypedDict):
    version_value: str


@dataclass
class TypedCNAXLV4AVDPDVersion(TypedDict):
    version_data: list[TypedCNAXLV4AVDPDVersionData]


@dataclass
class TypedCNAXLV4AVDPData(TypedDict):
    product_name: str
    version: TypedCNAXLV4AVDPDVersion


@dataclass
class TypedCNAXLV4AVDProduct(TypedDict):
    product_data: list[TypedCNAXLV4AVDPData]


@dataclass
class TypedCNAXLV4AffectsVendorData(TypedDict):
    product: TypedCNAXLV4AVDProduct
    vendor_name: str


@dataclass
class TypedCNAXLV4AffectsVendor(TypedDict):
    vendor_data: list[TypedCNAXLV4AffectsVendorData]


@dataclass
class TypedCNAXLV4Affects(TypedDict):
    vendor: TypedCNAXLV4AffectsVendor


@dataclass
class TypedCNAXLegacyV4Record(TypedDict):
    CVE_data_meta: TypedCNAXLV4RecordDataMeta
    affects: TypedCNAXLV4Affects
    data_format: str
    data_type: str
    data_version: str
    description: TypedCNAXLV4Description
    problemtype: TypedCNAXLV4ProblemType
    references: TypedCNAXLV4Reference


@dataclass
class TypedCNA(TypedDict):
    affected: list[TypedCNAAffected]
    descriptions: list[TypedCNADescription]
    problemTypes: list[TypedCNAProblemType]
    providerMetadata: TypedProviderMetadata
    references: list[TypedCNAReference]
    x_legacyV4Record: TypedCNAXLegacyV4Record


@dataclass
class TypedADPProviderMetadata(TypedDict):
    orgId: str
    shortName: str
    dateUpdated: str


@dataclass
class TypedADPReference(TypedDict):
    tags: list[str]
    url: str
    name: Optional[str]


@dataclass
class TypedADP(TypedDict):
    title: str
    providerMetadata: TypedADPProviderMetadata
    references: list[TypedADPReference]


@dataclass
class TypedContainer(TypedDict):
    cna: TypedCNA
    adp: list[TypedADP]


@dataclass
class TypedCVEMetadata(TypedDict):
    assignerOrgId: str
    assignerShortName: str
    cveId: str
    datePublished: str
    dateReserved: str
    dateUpdated: str
    state: str


@dataclass
class TypedCVE(TypedDict):
    containers: TypedContainer
    cveMetadata: TypedCVEMetadata
    dataType: str
    dataVersion: str
