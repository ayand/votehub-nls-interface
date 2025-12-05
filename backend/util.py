import requests
from typing import Dict, List
import asyncio

def make_api_call(url):
    response = requests.get(url)
    return response.json()

def normalize_choice(choice: str) -> str:
    """
    Normalize choice names by removing periods, commas, and extra whitespace.
    Matches the frontend normalization logic.
    """
    return choice.replace('.', '').replace(',', '').strip()

async def get_colors(choices: List[str], poll_type: str, app_logger) -> Dict[str, str]:
    """
    Compute color mapping for poll choices based on the poll type and party affiliations.

    Args:
        choices: List of choice names (e.g., candidate names, options)
        poll_type: Type of poll (e.g., 'primary', 'generic-ballot', 'approval')
        app_logger: Logger to log errors
    Returns:
        Dictionary mapping normalized choice names to hex color codes
    """
    from supporting_agents import get_party_affiliations
    

    # Hardcoded color maps for common poll types
    party_color_map = {
        normalize_choice('Dem'): '#2563eb',
        normalize_choice('Rep'): '#e02f28',
        normalize_choice('Lib'): '#c4b937',
        normalize_choice('Green'): '#288544',
        normalize_choice('Other'): '#7f7f7f'
    }

    # Normalize all input choices for comparison
    normalized_choices = [normalize_choice(c) for c in choices]

    # Check for Dem/Rep choices
    if 'Dem' in normalized_choices and 'Rep' in normalized_choices:
        return party_color_map

    # Check for Approve/Disapprove
    if 'Approve' in normalized_choices and 'Disapprove' in normalized_choices:
        return {
            normalize_choice('Approve'): '#288544',
            normalize_choice('Disapprove'): '#e08728'
        }

    # Check for Favorable/Unfavorable
    if 'Favorable' in normalized_choices and 'Unfavorable' in normalized_choices:
        return {
            normalize_choice('Favorable'): '#288544',
            normalize_choice('Unfavorable'): '#e08728'
        }

    # Check for Yes/No
    if 'Yes' in normalized_choices and 'No' in normalized_choices:
        return {
            normalize_choice('Yes'): '#288544',
            normalize_choice('No'): '#e08728'
        }

    # For primaries, map each choice to a distinct color
    if 'primary' in poll_type.lower():
        # Use colorblind-friendly categorical colors (Tableau 10)
        palette = [
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
        color_map = {}
        for idx, choice in enumerate(choices):
            color_map[normalize_choice(choice)] = palette[idx % len(palette)]
        return color_map

    # For candidate choices that may map to a party
    # Use get_party_affiliations to fetch party information
    party_affiliations = []
    try:
        app_logger.info(f"Fetching party affiliations for choices: {choices}")
        party_affiliations = await get_party_affiliations(choices)
        app_logger.info(f"Retrieved {len(party_affiliations)} party affiliations")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        app_logger.error(f"Error getting party affiliations: {e}\n{tb}")
        # If agent fails, we'll use fallback colors

    # If we have no affiliations at all, use fallback palette
    if not party_affiliations:
        app_logger.warning("No party affiliations found, using fallback palette")
        palette = [
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
        color_map = {}
        for idx, choice in enumerate(choices):
            color_map[normalize_choice(choice)] = palette[idx % len(palette)]
        return color_map

    # Count how many Dems/Reps in result
    party_counts = {}
    for affiliation in party_affiliations:
        party = affiliation.party
        if party not in party_counts:
            party_counts[party] = 0
        party_counts[party] += 1

    # Extended color palettes for Dems and Reps
    party_palettes = {
        'Dem': [
            '#2563eb',  # Original Dem blue
            '#3b82f6',  # Lighter blue
            '#1d4ed8',  # Darker blue
            '#60a5fa',  # Even lighter blue
            '#1e40af'   # Even darker blue
        ],
        'Rep': [
            '#e02f28',  # Original Rep red
            '#f87171',  # Lighter red
            '#b91c1c',  # Darker red
            '#fb7185',  # Even lighter red/pinkish
            '#991b1b'   # Even darker red
        ]
    }

    # Default fallback for other parties
    default_party_colors = {
        'Ind': '#eab308',  # yellow-ish for Independent
        'Other': '#7c3aed'
    }

    # Assign colors to each choice based on their party
    dem_index = 0
    rep_index = 0
    color_map = {}

    for choice in choices:
        # Find the party for this choice
        # Try exact match first, then fuzzy match
        affiliation = next((a for a in party_affiliations if a.person == choice), None)

        if not affiliation:
            # Try normalized comparison
            normalized_choice_lower = normalize_choice(choice).lower()
            affiliation = next((a for a in party_affiliations
                              if normalize_choice(a.person).lower() == normalized_choice_lower), None)

        if not affiliation:
            # Try substring matching (choice in person or person in choice)
            affiliation = next((a for a in party_affiliations
                              if choice.lower() in a.person.lower() or a.person.lower() in choice.lower()), None)

        normalized_choice = normalize_choice(choice)

        if affiliation:
            party = affiliation.party
            if party == 'Dem':
                color_map[normalized_choice] = party_palettes['Dem'][dem_index % len(party_palettes['Dem'])]
                dem_index += 1
            elif party == 'Rep':
                color_map[normalized_choice] = party_palettes['Rep'][rep_index % len(party_palettes['Rep'])]
                rep_index += 1
            else:
                color_map[normalized_choice] = default_party_colors.get(party, '#7f7f7f')  # fallback gray
        else:
            # No affiliation info, assign fallback gray
            color_map[normalized_choice] = '#7f7f7f'

    return color_map
