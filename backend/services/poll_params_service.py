"""
Service for converting natural language queries to VoteHub API parameters using AI agents.
"""
from typing import Dict, Any
from logging import Logger

from langchain.agents import create_agent
from models import VoteHubRequestParams
from tools import (
    get_supported_poll_types,
    get_supported_pollsters,
    get_poll_subjects,
    date_n_units_ago,
    get_month_range_by_name
)
from .agent_service import AgentService


class PollParamsService(AgentService):
    """
    Service for extracting structured poll query parameters from natural language.

    Converts user queries like "Biden approval ratings in the last month"
    into structured VoteHub API parameters like:
    {
        "subject": "Biden",
        "poll_type": "approval",
        "from_date": "2024-11-01",
        "to_date": "2024-12-01"
    }
    """

    def __init__(self, logger: Logger = None):
        """
        Initialize the poll params service.

        Args:
            logger: Logger instance for operation logging
        """
        super().__init__(logger)

    def _create_agent(self):
        """
        Create the poll params agent.

        Returns:
            Configured agent instance for parameter extraction
        """
        system_prompt = """
        You are a calculator of request parameters for the VoteHub API. You must
        calculate one or more of the following parameters (using tools as needed):

        * subject and poll_type (Use get_poll_subjects to get possible values to
          cross-reference; first use the subject field from the tool's output for
          the subject parameter, then use the poll_types field from the tool's
          output for the poll_type parameter. The poll_type parameter has to be
          one of the supported poll types that corresponds to the selected subject.
          It is also possible that the query only specifies a poll_type, in which
          case you should use the poll_type parameter without the subject parameter.)
        * pollster (Use get_supported_pollsters to get possible values to
          cross-reference; it could be a partial match)
        * from_date (Use date_n_units_ago or get_month_range_by_name to get
          possible values to cross-reference)
        * to_date (Use date_n_units_ago or get_month_range_by_name to get
          possible values to cross-reference)
        * min_sample_size (in integer format)
        * population (e.g. rv – registered voters, lv – likely voters, a – all voters)

        You must output your response in JSON format. The response must be a valid
        JSON object and must be a valid VoteHubRequestParams object.
        """

        return create_agent(
            model="gpt-5",
            tools=[
                get_supported_poll_types,
                get_poll_subjects,
                get_supported_pollsters,
                date_n_units_ago,
                get_month_range_by_name
            ],
            system_prompt=system_prompt,
            response_format=VoteHubRequestParams,
        )

    def extract_params(self, user_query: str) -> VoteHubRequestParams:
        """
        Extract VoteHub API parameters from a natural language query.

        Args:
            user_query: Natural language query from user

        Returns:
            VoteHubRequestParams object with extracted parameters

        Raises:
            Exception: If agent invocation fails
        """
        if not user_query or not user_query.strip():
            self._log_warning("Empty query provided")
            return VoteHubRequestParams()

        try:
            self._log_info(f"Extracting params from query: '{user_query}'")

            # Invoke agent with user query
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": user_query}]
            })

            # Extract structured response
            params = result['structured_response']

            # Log extracted parameters
            self._log_info(f"Extracted parameters: {params.model_dump(exclude_none=True)}")

            return params

        except Exception as e:
            self._log_error(f"Error extracting poll params: {e}")
            raise

    def extract_params_as_dict(self, user_query: str) -> Dict[str, Any]:
        """
        Extract VoteHub API parameters as a dictionary.

        Args:
            user_query: Natural language query from user

        Returns:
            Dictionary of parameters (excluding None values)
        """
        params = self.extract_params(user_query)
        return {
            k: v for k, v in params.model_dump(exclude_none=True).items()
        }

    def validate_params(self, params: VoteHubRequestParams) -> bool:
        """
        Validate that extracted parameters are reasonable.

        Args:
            params: VoteHubRequestParams to validate

        Returns:
            True if params appear valid, False otherwise
        """
        # Check if at least one parameter was extracted
        param_dict = params.model_dump(exclude_none=True)

        if not param_dict:
            self._log_warning("No parameters extracted from query")
            return False

        # Check date ordering if both dates present
        if params.from_date and params.to_date:
            if params.from_date > params.to_date:
                self._log_error(
                    f"from_date ({params.from_date}) is after to_date ({params.to_date})"
                )
                return False

        # Check sample size is positive
        if params.min_sample_size is not None and params.min_sample_size < 0:
            self._log_error(f"min_sample_size is negative: {params.min_sample_size}")
            return False

        return True
