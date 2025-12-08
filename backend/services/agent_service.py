"""
Base service class for AI agent operations.
Provides common functionality for agent-based services.
"""
from abc import ABC, abstractmethod
from typing import Any
from logging import Logger


class AgentService(ABC):
    """
    Abstract base class for agent-based services.

    Provides a template for services that interact with AI agents
    to perform specific tasks like name correction, party affiliation
    lookup, or parameter extraction.
    """

    def __init__(self, logger: Logger = None):
        """
        Initialize the agent service.

        Args:
            logger: Optional logger instance for logging operations
        """
        self.logger = logger
        self._agent = None

    @abstractmethod
    def _create_agent(self):
        """
        Create and configure the AI agent.

        This method should be implemented by subclasses to create
        their specific agent with appropriate tools and prompts.

        Returns:
            Configured agent instance
        """
        pass

    @property
    def agent(self):
        """
        Lazy-load the agent instance.

        Creates the agent on first access to avoid initialization
        overhead if the service is never used.

        Returns:
            The agent instance
        """
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    def _log_info(self, message: str):
        """
        Log an info message if logger is available.

        Args:
            message: Message to log
        """
        if self.logger:
            self.logger.info(message)

    def _log_error(self, message: str):
        """
        Log an error message if logger is available.

        Args:
            message: Error message to log
        """
        if self.logger:
            self.logger.error(message)

    def _log_warning(self, message: str):
        """
        Log a warning message if logger is available.

        Args:
            message: Warning message to log
        """
        if self.logger:
            self.logger.warning(message)
