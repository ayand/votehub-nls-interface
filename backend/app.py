"""
Refactored Flask application following OOP principles.
Uses dependency injection and separation of concerns.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import asyncio
from urllib.parse import urlencode

from services import (
    ApiService,
    ColorService,
    ChoiceService,
    NameCorrectionService,
    PartyAffiliationService,
    PollParamsService
)
from processors import PollProcessor


class VoteHubApplication:
    """Main application class encapsulating the VoteHub backend."""

    def __init__(self):
        """Initialize the application with all dependencies."""
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)

        # Initialize core services
        self.api_service = ApiService()
        self.choice_service = ChoiceService()

        # Initialize agent services
        self.name_correction_service = NameCorrectionService(self.app.logger)
        self.party_affiliation_service = PartyAffiliationService(self.app.logger)
        self.poll_params_service = PollParamsService(self.app.logger)

        # Initialize color service (depends on party affiliation service)
        self.color_service = ColorService(self.choice_service, self.app.logger)

        # Initialize processor with injected dependencies
        self.poll_processor = PollProcessor(
            choice_service=self.choice_service,
            color_service=self.color_service,
            name_correction_service=self.name_correction_service,
            party_affiliation_service=self.party_affiliation_service,
            logger=self.app.logger
        )

        # Register routes
        self._register_routes()

        # Validate environment
        self._validate_environment()

    def _validate_environment(self):
        """Validate required environment variables are set."""
        required_vars = ['OPENAI_API_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            self.app.logger.warning(
                f"Missing environment variables: {', '.join(missing)}"
            )

    def _register_routes(self):
        """Register all application routes."""
        self.app.route('/api/health', methods=['GET'])(self.health)
        self.app.route('/api/polls', methods=['GET'])(self.get_polls)

    def health(self):
        """
        Health check endpoint.

        Returns:
            JSON response with health status
        """
        return jsonify({
            'status': 'healthy',
            'message': 'Flask backend is running!'
        })

    def get_polls(self):
        """
        Get polls endpoint.
        Processes user query and returns organized poll data with color mappings.

        Returns:
            JSON response with poll divisions and color maps
        """
        try:
            # Extract query parameter
            user_query = request.args.get('q', '')
            if not user_query:
                return jsonify({'error': 'Query parameter "q" is required'}), 400

            # Convert query to VoteHub API parameters
            votehub_params = self._convert_query_to_params(user_query)

            # Fetch polls from VoteHub API
            polls_data = self._fetch_polls(votehub_params)

            # Process polls and return results
            result = asyncio.run(self._process_polls(polls_data))

            return jsonify(result)

        except Exception as e:
            self.app.logger.error(f"Error in get_polls: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    def _convert_query_to_params(self, user_query: str) -> dict:
        """
        Convert user query to VoteHub API parameters using an agent service.

        Args:
            user_query: Natural language query from user

        Returns:
            Dictionary of VoteHub API parameters
        """
        params_dict = self.poll_params_service.extract_params_as_dict(user_query)

        query_string = urlencode(params_dict)
        self.app.logger.info(f"Polls API query string: {query_string}")

        return params_dict

    def _fetch_polls(self, params: dict) -> list:
        """
        Fetch polls from VoteHub API.

        Args:
            params: Query parameters for the API

        Returns:
            List of poll dictionaries
        """
        query_string = urlencode(params)
        url = f"https://api.votehub.com/polls?{query_string}"
        return self.api_service.get(url)

    async def _process_polls(self, polls_data: list) -> dict:
        """
        Process poll data into divisions with color maps.

        Args:
            polls_data: Raw poll data from API

        Returns:
            Dictionary mapping division keys to processed data
        """
        # Divide polls by subject and poll_type
        divisions = self.poll_processor.divide_polls(polls_data)

        # Process each division concurrently
        tasks = [
            self._process_single_division(key, polls)
            for key, polls in divisions.items()
        ]

        results = await asyncio.gather(*tasks)

        # Convert to dictionary
        return {key: result for key, result in results}

    async def _process_single_division(self, key: str, polls: list) -> tuple:
        """
        Process a single poll division.

        Args:
            key: Division identifier
            polls: List of polls in division

        Returns:
            Tuple of (key, processed_data)
        """
        try:
            result = await self.poll_processor.process_division(key, polls)
            return (key, result)
        except Exception as e:
            self.app.logger.error(f"Error processing division {key}: {e}")
            return (key, {'polls': polls, 'color_map': {}})

    def run(self, host='0.0.0.0', port=5000, debug=True):
        """
        Run the Flask application.

        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Debug mode flag
        """
        self.app.run(host=host, port=port, debug=debug)


# Create application instance
application = VoteHubApplication()
app = application.app


if __name__ == '__main__':
    application.run()
