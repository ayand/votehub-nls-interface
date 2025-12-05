from pydantic import BaseModel, Field

from typing import Optional

class VoteHubRequestParams(BaseModel):
    poll_type: Optional[str] = Field(default=None, description="The poll type to use")
    pollster: Optional[str] = Field(default=None, description="The pollster to use")
    subject: Optional[str] = Field(default=None, description="The subject to use")
    from_date: Optional[str] = Field(default=None, description="The start date to use")
    to_date: Optional[str] = Field(default=None, description="The end date to use")
    min_sample_size: Optional[int] = Field(default=None, description="The minimum sample size to use")
    population: Optional[str] = Field(default=None, description="The population to use")

class PartyAffiliation(BaseModel):
    party: str = Field(description="The party of the person")
    person: str = Field(description="The name of the person")

class PartyAffiliationList(BaseModel):
    party_affiliations: list[PartyAffiliation] = Field(description="The results of party affiliation determinations")

class NameCorrection(BaseModel):
    incorrect_name: str = Field(description="The incorrect name of a choice")
    correct_name: str = Field(description="The correct name of a choice")

class NameCorrectionList(BaseModel):
    name_corrections: list[NameCorrection] = Field(description="The results of name corrections")
