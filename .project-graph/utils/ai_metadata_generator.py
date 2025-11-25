#!/usr/bin/env python3
"""AI-powered metadata generator for graph router.

This module uses AI (local Ollama or free APIs) to generate semantic metadata
like 'when_to_use' and 'typical_queries' for graphs.

Supported AI providers:
    - Ollama (local, free, no API key needed)
    - OpenAI GPT-4o-mini (cheap: ~$0.15/1M tokens)
    - Google Gemini (free tier available)
    - Anthropic Claude Haiku (cheap)

Usage:
    # Using local Ollama (recommended for free)
    python3 ai_metadata_generator.py --graph testing --provider ollama

    # Using OpenAI (requires OPENAI_API_KEY env var)
    python3 ai_metadata_generator.py --graph testing --provider openai

    # Generate for all incomplete graphs
    python3 ai_metadata_generator.py --auto-fill
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


def get_graph_root() -> Path:
    """Get graph root directory."""
    return Path(__file__).parent.parent


def load_router() -> Dict[str, Any]:
    """Load router file."""
    router_path = get_graph_root() / "graph-router.json"
    with open(router_path) as f:
        return json.load(f)


def save_router(router: Dict[str, Any]) -> None:
    """Save router file."""
    router_path = get_graph_root() / "graph-router.json"
    with open(router_path, 'w') as f:
        json.dump(router, f, indent=2)
        f.write('\n')


def load_graph(graph_file: str) -> Dict[str, Any]:
    """Load a specific graph file."""
    graph_path = get_graph_root() / graph_file
    with open(graph_path) as f:
        return json.load(f)


def build_context_from_graph(graph_id: str, graph_info: Dict, full_graph: Optional[Dict] = None) -> str:
    """Build context string for AI from graph metadata and content.

    Args:
        graph_id: Graph identifier
        graph_info: Graph metadata from router
        full_graph: Full graph content (optional, for deeper analysis)

    Returns:
        Context string for AI prompt
    """
    context_parts = []

    # Basic info
    context_parts.append(f"Graph ID: {graph_id}")
    context_parts.append(f"Name: {graph_info.get('name', 'N/A')}")
    context_parts.append(f"Description: {graph_info.get('description', 'N/A')}")

    # Coverage info
    if 'coverage' in graph_info:
        cov = graph_info['coverage']
        if 'directories' in cov:
            context_parts.append(f"Directories: {', '.join(cov['directories'])}")
        if 'key_components' in cov:
            context_parts.append(f"Key Components: {', '.join(cov['key_components'][:10])}")
        if 'modules' in cov:
            context_parts.append(f"Modules: {cov['modules']}")
        if 'scripts' in cov:
            context_parts.append(f"Scripts: {cov['scripts']}")

    # If we have full graph, extract more details
    if full_graph:
        nodes = full_graph.get('nodes', [])

        # Extract unique classes and functions (top 15)
        all_classes = []
        all_functions = []

        for node in nodes[:20]:  # Sample first 20 nodes
            all_classes.extend(node.get('classes', []))
            all_functions.extend(node.get('functions', []))

        unique_classes = list(set(all_classes))[:15]
        unique_functions = list(set(all_functions))[:15]

        if unique_classes:
            context_parts.append(f"Example Classes: {', '.join(unique_classes)}")
        if unique_functions:
            context_parts.append(f"Example Functions: {', '.join(unique_functions)}")

        # Node types
        node_types = list(set(n.get('type', 'unknown') for n in nodes))
        context_parts.append(f"Node Types: {', '.join(node_types)}")

    return '\n'.join(context_parts)


def generate_with_ollama(prompt: str, model: str = "llama3.2") -> Optional[str]:
    """Generate text using local Ollama.

    Args:
        prompt: Prompt text
        model: Ollama model name (default: llama3.2, also good: qwen2.5)

    Returns:
        Generated text or None if failed
    """
    try:
        import requests
    except ImportError:
        print("❌ requests library not found. Install: pip install requests")
        return None

    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'num_predict': 500
                }
            },
            timeout=60
        )

        if response.status_code == 200:
            return response.json()['response']
        else:
            print(f"❌ Ollama error: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        print("   Start Ollama: ollama serve")
        print(f"   Pull model: ollama pull {model}")
        return None
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return None


def generate_with_openai(prompt: str, model: str = "gpt-4o-mini") -> Optional[str]:
    """Generate text using OpenAI API.

    Args:
        prompt: Prompt text
        model: OpenAI model (default: gpt-4o-mini, cheap and good)

    Returns:
        Generated text or None if failed
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai library not found. Install: pip install openai")
        return None

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return None

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a technical documentation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return None


def generate_with_gemini(prompt: str) -> Optional[str]:
    """Generate text using Google Gemini API (free tier).

    Args:
        prompt: Prompt text

    Returns:
        Generated text or None if failed
    """
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ google-generativeai library not found.")
        print("   Install: pip install google-generativeai")
        return None

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Get free key: https://makersuite.google.com/app/apikey")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return None


def create_prompt(graph_id: str, context: str) -> str:
    """Create AI prompt for generating metadata.

    Args:
        graph_id: Graph identifier
        context: Context string about the graph

    Returns:
        Complete prompt text
    """
    return f"""You are analyzing a project dependency graph for a Telegram bot framework.

Graph Context:
{context}

Task: Generate metadata to help developers navigate this codebase efficiently.

Please provide:

1. "when_to_use": A list of 6-8 scenarios when a developer should load this graph.
   - Be specific and action-oriented
   - Focus on developer tasks, not just descriptions
   - Examples: "Adding new storage backend", "Fixing CI workflow", "Writing tests for X"

2. "typical_queries": A list of 7-10 questions developers might ask when working with this code.
   - Write as actual questions
   - Cover different aspects: how-to, where-is, what-does, debugging
   - Examples: "How to implement custom storage?", "Where are admin commands defined?"

Format your response as JSON:
{{
  "when_to_use": [
    "scenario 1",
    "scenario 2",
    ...
  ],
  "typical_queries": [
    "question 1?",
    "question 2?",
    ...
  ]
}}

IMPORTANT:
- Output ONLY valid JSON, no markdown formatting, no explanation
- Ensure all strings are properly escaped
- Be specific to this graph's actual content, not generic
"""


def parse_ai_response(response: str) -> Optional[Dict[str, List[str]]]:
    """Parse AI response and extract metadata.

    Args:
        response: Raw AI response text

    Returns:
        Dictionary with when_to_use and typical_queries, or None if parsing failed
    """
    # Try to extract JSON from response
    # Sometimes AI wraps JSON in markdown code blocks
    response = response.strip()

    # Remove markdown code blocks if present
    if response.startswith('```json'):
        response = response[7:]
    elif response.startswith('```'):
        response = response[3:]

    if response.endswith('```'):
        response = response[:-3]

    response = response.strip()

    try:
        data = json.loads(response)

        # Validate structure
        if 'when_to_use' not in data or 'typical_queries' not in data:
            print("⚠️  Response missing required fields")
            return None

        if not isinstance(data['when_to_use'], list) or not isinstance(data['typical_queries'], list):
            print("⚠️  Fields are not lists")
            return None

        return data

    except json.JSONDecodeError as e:
        print(f"⚠️  Failed to parse JSON: {e}")
        print(f"Response:\n{response[:200]}")
        return None


def generate_metadata_for_graph(
    graph_id: str,
    provider: str = 'ollama',
    model: Optional[str] = None,
    dry_run: bool = False
) -> Optional[Dict[str, List[str]]]:
    """Generate metadata for a specific graph using AI.

    Args:
        graph_id: Graph identifier
        provider: AI provider ('ollama', 'openai', 'gemini')
        model: Model name (provider-specific)
        dry_run: If True, only show what would be generated

    Returns:
        Generated metadata or None if failed
    """
    router = load_router()

    # Find graph info
    graph_info = None
    for _key, info in router['graphs'].items():
        if info['id'] == graph_id:
            graph_info = info
            break

    if not graph_info:
        print(f"❌ Graph '{graph_id}' not found in router")
        return None

    print(f"\n🤖 Generating metadata for: {graph_id}")
    print(f"   Provider: {provider}")

    # Load full graph for deeper analysis
    full_graph = None
    try:
        full_graph = load_graph(graph_info['file'])
    except Exception as e:
        print(f"   ⚠️  Could not load full graph: {e}")

    # Build context
    context = build_context_from_graph(graph_id, graph_info, full_graph)

    if dry_run:
        print(f"\n📄 Context that would be sent to AI:")
        print(context)
        return None

    # Create prompt
    prompt = create_prompt(graph_id, context)

    # Generate with selected provider
    print(f"   🔄 Generating...")

    if provider == 'ollama':
        model = model or 'llama3.2'
        response = generate_with_ollama(prompt, model)
    elif provider == 'openai':
        model = model or 'gpt-4o-mini'
        response = generate_with_openai(prompt, model)
    elif provider == 'gemini':
        response = generate_with_gemini(prompt)
    else:
        print(f"❌ Unknown provider: {provider}")
        return None

    if not response:
        return None

    # Parse response
    metadata = parse_ai_response(response)

    if metadata:
        print(f"   ✅ Generated {len(metadata['when_to_use'])} scenarios, {len(metadata['typical_queries'])} queries")

    return metadata


def auto_fill_incomplete(
    provider: str = 'ollama',
    min_when_to_use: int = 5,
    min_queries: int = 5,
    dry_run: bool = False
) -> int:
    """Auto-fill metadata for graphs that have incomplete metadata.

    Args:
        provider: AI provider to use
        min_when_to_use: Minimum number of when_to_use items required
        min_queries: Minimum number of typical_queries required
        dry_run: If True, don't actually update router

    Returns:
        Number of graphs updated
    """
    router = load_router()
    updated_count = 0

    print(f"\n🤖 Auto-filling incomplete graphs with {provider}")
    print("=" * 60)

    for graph_key, graph_info in router['graphs'].items():
        graph_id = graph_info['id']

        when_to_use = graph_info.get('when_to_use', [])
        typical_queries = graph_info.get('typical_queries', [])

        needs_update = (
            len(when_to_use) < min_when_to_use or
            len(typical_queries) < min_queries
        )

        if needs_update:
            print(f"\n📊 {graph_id}")
            print(f"   Current: {len(when_to_use)} scenarios, {len(typical_queries)} queries")

            metadata = generate_metadata_for_graph(graph_id, provider, dry_run=dry_run)

            if metadata and not dry_run:
                # Update router
                graph_info['when_to_use'] = metadata['when_to_use']
                graph_info['typical_queries'] = metadata['typical_queries']
                updated_count += 1
                print(f"   ✅ Updated in router")
            elif metadata and dry_run:
                print(f"   🔍 Would update with:")
                print(f"      when_to_use: {metadata['when_to_use'][:2]}...")
                print(f"      typical_queries: {metadata['typical_queries'][:2]}...")

    if updated_count > 0 and not dry_run:
        save_router(router)
        print(f"\n✅ Updated {updated_count} graph(s) and saved router")
    elif dry_run:
        print(f"\n🔍 Dry run complete - no changes made")

    print("=" * 60)

    return updated_count


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI-powered metadata generator for graphs"
    )
    parser.add_argument(
        '--graph',
        help='Graph ID to generate metadata for'
    )
    parser.add_argument(
        '--provider',
        choices=['ollama', 'openai', 'gemini'],
        default='ollama',
        help='AI provider (default: ollama - free and local)'
    )
    parser.add_argument(
        '--model',
        help='Model name (provider-specific)'
    )
    parser.add_argument(
        '--auto-fill',
        action='store_true',
        help='Auto-fill all graphs with incomplete metadata'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    if args.graph:
        # Generate for specific graph
        metadata = generate_metadata_for_graph(
            args.graph,
            provider=args.provider,
            model=args.model,
            dry_run=args.dry_run
        )

        if metadata:
            print(f"\n📄 Generated Metadata:")
            print(json.dumps(metadata, indent=2))

            if not args.dry_run:
                # Ask to update router
                print(f"\n💾 Update router.json with this metadata? (y/n): ", end='')
                response = input().strip().lower()

                if response == 'y':
                    router = load_router()
                    for _key, info in router['graphs'].items():
                        if info['id'] == args.graph:
                            info['when_to_use'] = metadata['when_to_use']
                            info['typical_queries'] = metadata['typical_queries']
                            break
                    save_router(router)
                    print("✅ Router updated!")

    elif args.auto_fill:
        # Auto-fill incomplete graphs
        auto_fill_incomplete(
            provider=args.provider,
            dry_run=args.dry_run
        )

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
