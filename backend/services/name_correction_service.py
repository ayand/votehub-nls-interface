"""
Service for correcting inconsistent candidate/choice names using AI agents.
"""
from typing import List, Dict
from logging import Logger

from agents import Agent, WebSearchTool, Runner
from models import NameCorrectionList
from .agent_service import AgentService


class NameCorrectionService(AgentService):
    """
    Service for identifying and correcting inconsistent names in poll data.

    Uses AI agents to detect variations like:
    - "Trump, Jr." vs "Trump Jr" (punctuation differences)
    - "J.D. Vance" vs "JD Vance" (period differences)
    - Other naming inconsistencies in poll choices
    """

    def __init__(self, logger: Logger = None):
        """
        Initialize the name correction service.

        Args:
            logger: Logger instance for operation logging
        """
        super().__init__(logger)

    def _create_agent(self):
        """
        Create the name correction agent.

        Returns:
            Configured Agent instance for name correction
        """
        system_prompt = """
        You are a name correction agent. Your input is a comma-separated list of names.
        You must correct the names to the correct name. All of the correct names are in
        fact included in your input. If the difference between the names is just dots,
        remove the dots. If you don't recognize the name, you should call your search
        tool to acquire the results.

        You must output your response in JSON format.
        """

        return Agent(
            name="name_correction_agent",
            model="gpt-5",
            tools=[WebSearchTool()],
            instructions=system_prompt,
            output_type=NameCorrectionList,
        )

    async def get_corrections(self, names: List[str]) -> Dict[str, str]:
        """
        Get name corrections for a list of names.

        Args:
            names: List of potentially inconsistent names

        Returns:
            Dictionary mapping incorrect names to correct names

        Raises:
            Exception: If agent invocation fails
        """
        if not names:
            self._log_info("No names provided for correction")
            return {}

        try:
            self._log_info(f"Getting name corrections for {len(names)} names")

            # Invoke agent with comma-separated names
            agent_result = await Runner.run(self.agent, ','.join(names))

            # Extract corrections from structured output
            corrections_list = agent_result.final_output.name_corrections

            # Build mapping dictionary
            corrections_map = {
                correction.incorrect_name: correction.correct_name
                for correction in corrections_list
            }

            self._log_info(f"Received {len(corrections_map)} name corrections")

            # Log specific corrections for debugging
            for incorrect, correct in corrections_map.items():
                if incorrect != correct:
                    self._log_info(f"Correcting '{incorrect}' → '{correct}'")

            return corrections_map

        except Exception as e:
            self._log_error(f"Error getting name corrections: {e}")
            raise

    async def apply_corrections_to_choices(
        self,
        choices: List[str]
    ) -> Dict[str, str]:
        """
        Get corrections and return a mapping for all choices.

        Args:
            choices: List of choice names to correct

        Returns:
            Dictionary mapping original names to corrected names
            (includes identity mappings for uncorrected names)
        """
        corrections = await self.get_corrections(choices)

        # Build complete mapping (including identity mappings)
        complete_mapping = {}
        for choice in choices:
            complete_mapping[choice] = corrections.get(choice, choice)

        return complete_mapping
