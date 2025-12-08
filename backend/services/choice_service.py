"""
Service for processing and normalizing poll choices.
Handles choice deduplication, normalization, and statistics calculation.
"""
from typing import List, Dict, Any
from collections import defaultdict


class ChoiceService:
    """Handles poll choice processing and normalization."""

    @staticmethod
    def normalize(choice: str) -> str:
        """
        Normalize choice names by removing periods, commas, and extra whitespace.
        Matches the frontend normalization logic.

        Args:
            choice: The choice name to normalize

        Returns:
            Normalized choice name
        """
        return choice.replace('.', '').replace(',', '').strip()

    def calculate_choice_statistics(
        self,
        polls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate statistics for all choices across polls.

        Args:
            polls: List of poll dictionaries

        Returns:
            List of choice statistics sorted by average percentage
        """
        choice_stats = {}

        for poll in polls:
            for answer in poll.get('answers', []):
                choice = answer.get('choice', '')
                normalized = self.normalize(choice)

                if normalized not in choice_stats:
                    choice_stats[normalized] = {
                        'total': 0,
                        'count': 0,
                        'display_name': choice,
                        'original_names': []
                    }

                stats = choice_stats[normalized]
                stats['total'] += answer.get('pct', 0)
                stats['count'] += 1
                stats['original_names'].append(choice)

                # Use the shortest version as display name
                if len(choice) < len(stats['display_name']):
                    stats['display_name'] = choice

        # Sort choices by average percentage
        unique_choices = sorted(
            [
                {
                    'normalized': normalized,
                    'display_name': stats['display_name'],
                    'average': stats['total'] / stats['count'] if stats['count'] > 0 else 0
                }
                for normalized, stats in choice_stats.items()
            ],
            key=lambda x: x['average'],
            reverse=True
        )

        return unique_choices

    def deduplicate_answers(
        self,
        answers: List[Dict[str, Any]],
        name_corrections: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate and merge answers with corrections applied.

        Args:
            answers: List of answer dictionaries
            name_corrections: Mapping of incorrect names to correct names

        Returns:
            List of deduplicated answers
        """
        # Apply corrections
        for answer in answers:
            original_choice = answer.get('choice', '')
            if original_choice in name_corrections:
                answer['choice'] = name_corrections[original_choice]

        # Deduplicate
        deduplicated = {}
        for answer in answers:
            choice = answer.get('choice', '')
            pct = answer.get('pct', 0)

            if choice in deduplicated:
                deduplicated[choice]['total'] += pct
                deduplicated[choice]['count'] += 1
            else:
                deduplicated[choice] = {
                    'choice': choice,
                    'total': pct,
                    'count': 1
                }

        # Calculate averages
        final_answers = []
        for choice, data in deduplicated.items():
            avg_pct = data['total'] / data['count']
            final_answers.append({'choice': choice, 'pct': avg_pct})

        return final_answers

    def extract_distinct_choices(self, polls: List[Dict[str, Any]]) -> List[str]:
        """
        Extract all distinct choices from a list of polls.

        Args:
            polls: List of poll dictionaries

        Returns:
            List of distinct choice names
        """
        distinct_choices = set()
        for poll in polls:
            for answer in poll.get('answers', []):
                choice = answer.get('choice', '')
                if choice:
                    distinct_choices.add(choice)
        return list(distinct_choices)
