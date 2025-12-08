"""
Service for determining party affiliations of political candidates using AI agents.
"""
from typing import List
from logging import Logger

from agents import Agent, WebSearchTool, Runner
from models import PartyAffiliation, PartyAffiliationList
from .agent_service import AgentService


class PartyAffiliationService(AgentService):
    """
    Service for determining the party affiliation of political candidates.

    Uses AI agents with web search capabilities to look up and identify
    party affiliations for candidates in poll data.

    Supported parties:
    - Dem (Democrat)
    - Rep (Republican)
    - Ind (Independent)
    - Lib (Libertarian)
    - Green (Green Party)
    - Other (other parties)
    - Unknown (cannot be determined)
    """

    def __init__(self, logger: Logger = None):
        """
        Initialize the party affiliation service.

        Args:
            logger: Logger instance for operation logging
        """
        super().__init__(logger)

    def _create_agent(self):
        """
        Create the party affiliation agent.

        Returns:
            Configured Agent instance for party affiliation lookup
        """
        system_prompt = """
        You are a calculator of party affiliations. Your input is a comma-separated
        list of names. You must calculate the party affiliation of each person
        supplied to you. If a person's party affiliation is not in your data, you
        should call your search tool to acquire the results. If you can't determine
        the party affiliation, answer 'Unknown'.

        Answer 'Dem' for Democrat, 'Rep' for Republican, 'Ind' for Independent,
        'Lib' for Libertarian, 'Green' for Green, 'Other' for any other party.
        If you cannot determine the party affiliation, answer 'Unknown'.

        You must output your response in JSON format.
        """

        return Agent(
            name="party_affiliation_agent",
            model="gpt-5",
            tools=[WebSearchTool()],
            instructions=system_prompt,
            output_type=PartyAffiliationList,
        )

    async def get_affiliations(self, names: List[str]) -> List[PartyAffiliation]:
        """
        Get party affiliations for a list of names.

        Args:
            names: List of candidate/person names

        Returns:
            List of PartyAffiliation objects

        Raises:
            Exception: If agent invocation fails
        """
        if not names:
            self._log_info("No names provided for party affiliation lookup")
            return []

        try:
            self._log_info(
                f"Fetching party affiliations for {len(names)} names: {names}"
            )

            # Invoke agent with comma-separated names
            agent_result = await Runner.run(self.agent, ','.join(names))

            # Extract affiliations from structured output
            affiliations = agent_result.final_output.party_affiliations

            self._log_info(f"Retrieved {len(affiliations)} party affiliations")

            # Log affiliations for debugging
            for affiliation in affiliations:
                self._log_info(
                    f"Party affiliation: {affiliation.person} → {affiliation.party}"
                )

            return affiliations

        except Exception as e:
            self._log_error(f"Error getting party affiliations: {e}")
            raise

    async def get_affiliations_map(self, names: List[str]) -> dict:
        """
        Get party affiliations as a dictionary mapping.

        Args:
            names: List of candidate/person names

        Returns:
            Dictionary mapping person names to party affiliations
        """
        affiliations = await self.get_affiliations(names)

        return {
            affiliation.person: affiliation.party
            for affiliation in affiliations
        }

    def filter_by_party(
        self,
        affiliations: List[PartyAffiliation],
        party: str
    ) -> List[str]:
        """
        Filter affiliations to get names belonging to a specific party.

        Args:
            affiliations: List of PartyAffiliation objects
            party: Party to filter by (e.g., 'Dem', 'Rep')

        Returns:
            List of person names belonging to the specified party
        """
        return [
            affiliation.person
            for affiliation in affiliations
            if affiliation.party == party
        ]

    def count_by_party(self, affiliations: List[PartyAffiliation]) -> dict:
        """
        Count affiliations by party.

        Args:
            affiliations: List of PartyAffiliation objects

        Returns:
            Dictionary mapping party names to counts
        """
        counts = {}
        for affiliation in affiliations:
            party = affiliation.party
            counts[party] = counts.get(party, 0) + 1

        return counts
