from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from urllib.parse import urlencode
from supporting_agents import create_party_affiliation_agent, create_poll_params_agent
from util import make_api_call, get_colors, normalize_choice
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Flask backend is running!'
    })

@app.route('/api/polls', methods=['GET'])
def get_polls():

    poll_params_agent = create_poll_params_agent()

    user_prompt = request.args.get('q', '')
    result = poll_params_agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )

    votehub_params = result['structured_response']

    query_params = {k: v for k, v in votehub_params.model_dump(exclude_none=True).items()}
    query_string = urlencode(query_params)
    app.logger.info(f"Polls API query string: {query_string}")

    # Fetch polls from VoteHub API
    polls_data = make_api_call(f"https://api.votehub.com/polls?{query_string}")

    # Divide polls by subject and poll_type
    divisions = defaultdict(list)
    for poll in polls_data:
        key = f"{poll.get('subject', 'unknown')}_{poll.get('poll_type', 'unknown')}"
        divisions[key].append(poll)

    # Helper async function to compute color map for a division
    async def compute_division_data(division_key, division_polls):
        from supporting_agents import get_name_corrections
        
        # Step 1: Extract distinct choices from all polls in this division
        distinct_choices = set()
        for poll in division_polls:
            answers = poll.get('answers', [])
            for answer in answers:
                choice = answer.get('choice', '')
                if choice:
                    distinct_choices.add(choice)
        
        # Step 2: Get name corrections for all distinct choices
        name_corrections_map = {}
        if distinct_choices:
            try:
                app.logger.info(f"Getting name corrections for {len(distinct_choices)} choices in division {division_key}")
                choices_list = list(distinct_choices)
                name_corrections = await get_name_corrections(choices_list)
                
                # Build a mapping from incorrect name to correct name
                for correction in name_corrections:
                    name_corrections_map[correction.incorrect_name] = correction.correct_name
                
                app.logger.info(f"Received {len(name_corrections_map)} name corrections")
            except Exception as e:
                app.logger.error(f"Error getting name corrections: {e}")
                # Continue without corrections if the agent fails
        
        # Step 3: Apply name corrections and de-duplicate answers in each poll
        for poll in division_polls:
            answers = poll.get('answers', [])
            
            # First, apply corrections
            for answer in answers:
                original_choice = answer.get('choice', '')
                if original_choice in name_corrections_map:
                    corrected_choice = name_corrections_map[original_choice]
                    app.logger.info(f"Correcting '{original_choice}' to '{corrected_choice}'")
                    answer['choice'] = corrected_choice
            
            # Second, de-duplicate answers with the same choice name
            deduplicated = {}
            for answer in answers:
                choice = answer.get('choice', '')
                pct = answer.get('pct', 0)
                
                if choice in deduplicated:
                    # Merge: track total and count for averaging
                    deduplicated[choice]['total'] += pct
                    deduplicated[choice]['count'] += 1
                else:
                    # New entry
                    deduplicated[choice] = {
                        'choice': choice,
                        'total': pct,
                        'count': 1
                    }
            
            # Calculate averages and build final answer list
            final_answers = []
            for choice, data in deduplicated.items():
                avg_pct = data['total'] / data['count']
                final_answers.append({'choice': choice, 'pct': avg_pct})
                if data['count'] > 1:
                    app.logger.info(f"Averaged {data['count']} entries for '{choice}': {avg_pct:.1f}%")
            
            # Replace answers with deduplicated list
            poll['answers'] = final_answers
        
        # Step 4: Calculate unique choices for this group with normalization
        choice_stats = {}
        for poll in division_polls:
            answers = poll.get('answers', [])
            for answer in answers:
                choice = answer.get('choice', '')
                normalized = normalize_choice(choice)
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

        # Sort choices by average percentage in descending order
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

        # Get top 10 choices
        top_10_choices = [item['display_name'] for item in unique_choices[:10]]

        # Compute color map
        poll_type = division_key.split('_', 1)[1] if '_' in division_key else 'unknown'
        color_map = await get_colors(top_10_choices, poll_type, app.logger) if top_10_choices else {}

        return {
            'polls': division_polls,
            'color_map': color_map
        }

    # Process divisions sequentially with async support
    import asyncio

    async def process_one_division(key, polls):
        try:
            result = await compute_division_data(key, polls)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            app.logger.error(f"Error processing division {key}: {str(e)}\n{tb}")
            result = {
                'polls': divisions[key],
                'color_map': {}
            }
        return key, result

    async def process_all_divisions():
        import asyncio
        tasks = [process_one_division(key, polls) for key, polls in divisions.items()]
        results = await asyncio.gather(*tasks)
        # Convert (key, result) tuples to a dict
        return {key: result for key, result in results}

    result_divisions = asyncio.run(process_all_divisions())
    return jsonify(result_divisions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
