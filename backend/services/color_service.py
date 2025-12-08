"""
Service for computing color mappings for poll choices.
Handles color assignment based on poll types and party affiliations.
"""
from typing import List, Dict
from logging import Logger


class ColorService:
    """Handles color mapping computation for poll choices."""

    # Color palettes
    PARTY_COLORS = {
        'Dem': '#2563eb',
        'Rep': '#e02f28',
        'Lib': '#c4b937',
        'Green': '#288544',
        'Other': '#7f7f7f'
    }

    DEM_PALETTE = [
        '#2563eb',  # Original Dem blue
        '#3b82f6',  # Lighter blue
        '#1d4ed8',  # Darker blue
        '#60a5fa',  # Even lighter blue
        '#1e40af'   # Even darker blue
    ]

    REP_PALETTE = [
        '#e02f28',  # Original Rep red
        '#f87171',  # Lighter red
        '#b91c1c',  # Darker red
        '#fb7185',  # Even lighter red/pinkish
        '#991b1b'   # Even darker red
    ]

    FALLBACK_PALETTE = [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Olive
        '#17becf'   # Cyan
    ]

    def __init__(self, choice_service, logger: Logger):
        """
        Initialize the color service.

        Args:
            choice_service: ChoiceService instance for normalization
            logger: Logger instance
        """
        self.choice_service = choice_service
        self.logger = logger

    async def compute_color_map(
        self,
        choices: List[str],
        poll_type: str,
        party_affiliation_service
    ) -> Dict[str, str]:
        """
        Compute color mapping for poll choices.

        Args:
            choices: List of choice names
            poll_type: Type of poll
            party_affiliation_service: Service for fetching party affiliations

        Returns:
            Dictionary mapping normalized choice names to hex colors
        """
        normalized_choices = [self.choice_service.normalize(c) for c in choices]

        # Check for standard choice pairs
        if color_map := self._get_standard_color_map(normalized_choices):
            return color_map

        # Handle primary polls
        if 'primary' in poll_type.lower():
            return self._get_primary_colors(choices)

        # Handle candidate polls with party affiliations
        return await self._get_party_based_colors(
            choices,
            party_affiliation_service
        )

    def _get_standard_color_map(self, normalized_choices: List[str]) -> Dict[str, str]:
        """
        Get color map for standard choice pairs.

        Args:
            normalized_choices: List of normalized choice names

        Returns:
            Color map if standard pair found, None otherwise
        """
        # Party choices
        if 'Dem' in normalized_choices and 'Rep' in normalized_choices:
            return {
                self.choice_service.normalize(k): v
                for k, v in self.PARTY_COLORS.items()
            }

        # Approval choices
        if 'Approve' in normalized_choices and 'Disapprove' in normalized_choices:
            return {
                'Approve': '#288544',
                'Disapprove': '#e08728'
            }

        # Favorability choices
        if 'Favorable' in normalized_choices and 'Unfavorable' in normalized_choices:
            return {
                'Favorable': '#288544',
                'Unfavorable': '#e08728'
            }

        # Yes/No choices
        if 'Yes' in normalized_choices and 'No' in normalized_choices:
            return {
                'Yes': '#288544',
                'No': '#e08728'
            }

        return None

    def _get_primary_colors(self, choices: List[str]) -> Dict[str, str]:
        """
        Get distinct colors for primary poll choices.

        Args:
            choices: List of choice names

        Returns:
            Color map with distinct colors for each choice
        """
        color_map = {}
        for idx, choice in enumerate(choices):
            normalized = self.choice_service.normalize(choice)
            color_map[normalized] = self.FALLBACK_PALETTE[idx % len(self.FALLBACK_PALETTE)]
        return color_map

    async def _get_party_based_colors(
        self,
        choices: List[str],
        party_affiliation_service
    ) -> Dict[str, str]:
        """
        Get colors based on party affiliations using the service.

        Args:
            choices: List of choice names
            party_affiliation_service: Service for fetching affiliations

        Returns:
            Color map based on party affiliations
        """
        # Fetch party affiliations using the service
        party_affiliations = []
        try:
            self.logger.info(f"Fetching party affiliations for {len(choices)} choices")
            party_affiliations = await party_affiliation_service.get_affiliations(choices)
            self.logger.info(f"Retrieved {len(party_affiliations)} party affiliations")
        except Exception as e:
            self.logger.error(f"Error getting party affiliations: {e}")
            return self._get_primary_colors(choices)

        # No affiliations found
        if not party_affiliations:
            self.logger.warning("No party affiliations found, using fallback palette")
            return self._get_primary_colors(choices)

        # Assign colors based on party
        return self._assign_party_colors(choices, party_affiliations)

    def _assign_party_colors(
        self,
        choices: List[str],
        party_affiliations: List
    ) -> Dict[str, str]:
        """
        Assign colors to choices based on their party affiliations.

        Args:
            choices: List of choice names
            party_affiliations: List of PartyAffiliation objects

        Returns:
            Color map with party-based colors
        """
        dem_index = 0
        rep_index = 0
        color_map = {}

        for choice in choices:
            # Find matching affiliation
            affiliation = self._find_affiliation(choice, party_affiliations)
            normalized_choice = self.choice_service.normalize(choice)

            if affiliation:
                party = affiliation.party
                if party == 'Dem':
                    color_map[normalized_choice] = self.DEM_PALETTE[dem_index % len(self.DEM_PALETTE)]
                    dem_index += 1
                elif party == 'Rep':
                    color_map[normalized_choice] = self.REP_PALETTE[rep_index % len(self.REP_PALETTE)]
                    rep_index += 1
                else:
                    color_map[normalized_choice] = self.PARTY_COLORS.get(party, '#7f7f7f')
            else:
                # No affiliation, use gray
                color_map[normalized_choice] = '#7f7f7f'

        return color_map

    def _find_affiliation(self, choice: str, party_affiliations: List):
        """
        Find the party affiliation for a choice.

        Args:
            choice: Choice name to find affiliation for
            party_affiliations: List of PartyAffiliation objects

        Returns:
            Matching PartyAffiliation or None
        """
        # Try exact match
        affiliation = next((a for a in party_affiliations if a.person == choice), None)
        if affiliation:
            return affiliation

        # Try normalized match
        normalized_choice = self.choice_service.normalize(choice).lower()
        affiliation = next(
            (a for a in party_affiliations
             if self.choice_service.normalize(a.person).lower() == normalized_choice),
            None
        )
        if affiliation:
            return affiliation

        # Try substring match
        affiliation = next(
            (a for a in party_affiliations
             if choice.lower() in a.person.lower() or a.person.lower() in choice.lower()),
            None
        )
        return affiliation
