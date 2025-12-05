from typing import List
from langchain.agents import create_agent
import os
from models import NameCorrectionList, PartyAffiliationList, VoteHubRequestParams
from tools import get_supported_poll_types, get_supported_pollsters, get_poll_subjects, date_n_units_ago, get_month_range_by_name, make_api_call
from agents import Agent, WebSearchTool, Runner

def create_poll_params_agent():
    system_prompt = """
    You are a calculator of request parameters for the VoteHub API. You must calculate one or more of the following parameters (using tools as needed):

    * subject and poll_type (Use get_poll_subjects to get possible values to cross-reference; first use the subject field from the tool's output for the subject parameter, then use the poll_types field from the tool's output for the poll_type parameter. The poll_type parameter has to be one of the supported poll types that corresponds to the selected subject. It is also possible that the query only specifies a poll_type, in which case you should use the poll_type parameter without the subject parameter.)
    * pollster (Use get_supported_pollsters to get possible values to cross-reference; it could be a partial match)
    * from_date (Use date_n_units_ago or get_month_range_by_name to get possible values to cross-reference)
    * to_date (Use date_n_units_ago or get_month_range_by_name to get possible values to cross-reference)
    * min_sample_size (in integer format)
    * population (e.g. rv – registered voters, lv – likely voters, a – all voters)
    You must output your response    in JSON format. The response must be a valid JSON object and must be a valid VoteHubRequestParams object.
    """
    return create_agent(
        model="gpt-5",
        tools=[get_supported_poll_types, get_poll_subjects, get_supported_pollsters, date_n_units_ago, get_month_range_by_name],
        system_prompt=system_prompt,
        response_format=VoteHubRequestParams,
    )

def create_party_affiliation_agent():
    system_prompt = """
    You are a calculator of party affiliations. Your input is a comma-separated list of names. You must calculate the party affiliation of each person supplied to you. If a person's party affiliation is not in your data, you should call your search tool to acquire the results. If you can't determine the party affiliation, answer 'Unknown'.

    Answer 'Dem' for Democrat, 'Rep' for Republican, 'Ind' for Independent, 'Lib' for Libertarian, 'Green' for Green, 'Other' for any other party. If you cannot determine the party affiliation, answer 'Unknown'.
    
    You must output your response in JSON format.
    """
    
    return Agent(
        name="party_affiliation_agent",
        model="gpt-5",
        tools=[WebSearchTool()],
        instructions=system_prompt,
        output_type=PartyAffiliationList,
    )

async def get_party_affiliations(choices: List[str]):
    agent_result = await Runner.run(create_party_affiliation_agent(), ','.join(choices))
    return agent_result.final_output.party_affiliations

def create_name_correction_agent():
    system_prompt = """
    You are a name correction agent. Your input is a comma-separated list of names. You must correct the names to the correct name. All of the correct names are in fact included in your input.

    You must output your response in JSON format.
    """
    return Agent(
        name="name_correction_agent",
        model="gpt-5",
        instructions=system_prompt,
        output_type=NameCorrectionList,
    )

async def get_name_corrections(names: List[str]):
    agent_result = await Runner.run(create_name_correction_agent(), ','.join(names))
    return agent_result.final_output.name_corrections
