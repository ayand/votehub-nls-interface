"""
Processor for handling poll data operations.
Coordinates between services to process poll divisions.
"""
from typing import Dict, Any, List
from logging import Logger
from collections import defaultdict


class PollProcessor:
    """Processes poll data including deduplication and color assignment."""

    def __init__(
        self,
        choice_service,
        color_service,
        name_correction_service,
        party_affiliation_service,
        logger: Logger
    ):
        """
        Initialize the poll processor.

        Args:
            choice_service: Service for choice operations
            color_service: Service for color operations
            name_correction_service: Service for name corrections
            party_affiliation_service: Service for party affiliations
            logger: Logger instance
        """
        self.choice_service = choice_service
        self.color_service = color_service
        self.name_correction_service = name_correction_service
        self.party_affiliation_service = party_affiliation_service
        self.logger = logger

    def divide_polls(self, polls: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Divide polls by subject and poll_type.

        Args:
            polls: List of poll dictionaries

        Returns:
            Dictionary mapping division keys to lists of polls
        """
        divisions = defaultdict(list)
        for poll in polls:
            key = f"{poll.get('subject', 'unknown')}_{poll.get('poll_type', 'unknown')}"
            divisions[key].append(poll)
        return dict(divisions)

    async def process_division(
        self,
        division_key: str,
        division_polls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a single poll division.

        Args:
            division_key: Division identifier (subject_polltype)
            division_polls: List of polls in this division

        Returns:
            Dictionary with processed polls and color map
        """
        try:
            # Extract distinct choices
            distinct_choices = self.choice_service.extract_distinct_choices(division_polls)

            # Get name corrections
            name_corrections_map = await self._get_name_corrections(distinct_choices, division_key)

            # Apply corrections and deduplicate
            self._apply_corrections_to_polls(division_polls, name_corrections_map)

            # Calculate choice statistics
            unique_choices = self.choice_service.calculate_choice_statistics(division_polls)

            # Get top 10 choices
            top_10_choices = [item['display_name'] for item in unique_choices[:10]]

            # Compute color map
            poll_type = division_key.split('_', 1)[1] if '_' in division_key else 'unknown'
            color_map = await self.color_service.compute_color_map(
                top_10_choices,
                poll_type,
                self.party_affiliation_service
            ) if top_10_choices else {}

            return {
                'polls': division_polls,
                'color_map': color_map
            }

        except Exception as e:
            self.logger.error(f"Error processing division {division_key}: {e}")
            return {
                'polls': division_polls,
                'color_map': {}
            }

    def _should_skip_name_correction(self, distinct_choices: List[str]) -> bool:
        """
        Check if name correction should be skipped for standard option polls.

        Standard options include:
        - Dem/Rep (party polls)
        - Approve/Disapprove (approval polls)
        - Favorable/Unfavorable (favorability polls)
        - Yes/No (referendum polls)

        Args:
            distinct_choices: List of distinct choice names

        Returns:
            True if name correction should be skipped, False otherwise
        """
        # Normalize choices for comparison
        normalized_choices = [
            self.choice_service.normalize(choice).lower()
            for choice in distinct_choices
        ]

        # Define standard option pairs
        standard_pairs = [
            {'dem', 'rep'},
            {'approve', 'disapprove'},
            {'favorable', 'unfavorable'},
            {'yes', 'no'}
        ]

        # Check if choices match any standard pair
        choices_set = set(normalized_choices)
        for pair in standard_pairs:
            # If both options from a pair are present, skip name correction
            if pair.issubset(choices_set):
                self.logger.info(
                    f"Skipping name correction - standard options detected: {pair}"
                )
                return True

        return False

    async def _get_name_corrections(
        self,
        distinct_choices: List[str],
        division_key: str
    ) -> Dict[str, str]:
        """
        Get name corrections for choices using the name correction service.
        Skips correction for standard option polls (Dem/Rep, Approve/Disapprove, etc.)

        Args:
            distinct_choices: List of distinct choice names
            division_key: Division identifier for logging

        Returns:
            Dictionary mapping incorrect names to correct names
        """
        if not distinct_choices:
            return {}

        # Check if this is a standard option poll (skip name correction)
        if self._should_skip_name_correction(distinct_choices):
            self.logger.info(
                f"Skipping name correction for division {division_key} - standard options"
            )
            return {}

        try:
            self.logger.info(
                f"Getting name corrections for {len(distinct_choices)} choices in {division_key}"
            )

            # Use the name correction service instead of direct function
            name_corrections_map = await self.name_correction_service.get_corrections(
                distinct_choices
            )

            self.logger.info(f"Received {len(name_corrections_map)} name corrections")
            return name_corrections_map

        except Exception as e:
            self.logger.error(f"Error getting name corrections: {e}")
            return {}

    def _apply_corrections_to_polls(
        self,
        polls: List[Dict[str, Any]],
        name_corrections: Dict[str, str]
    ) -> None:
        """
        Apply name corrections and deduplicate answers in polls.

        Args:
            polls: List of poll dictionaries (modified in place)
            name_corrections: Mapping of incorrect to correct names
        """
        for poll in polls:
            answers = poll.get('answers', [])

            # Apply corrections and deduplicate
            final_answers = self.choice_service.deduplicate_answers(
                answers,
                name_corrections
            )

            # Log any merges
            if len(final_answers) < len(answers):
                self.logger.info(
                    f"Merged {len(answers)} answers to {len(final_answers)} "
                    f"in poll {poll.get('id', 'unknown')}"
                )

            poll['answers'] = final_answers
