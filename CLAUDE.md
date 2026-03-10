# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Beaulit Agent** is a Korean beauty care chatbot targeting 20-30 year olds, built with a multi-agent LangGraph architecture and RAG (Retrieval-Augmented Generation). It provides skin care advice using a vector knowledge base and DuckDuckGo web search as a fallback.

## Commands

```bash
# Install dependencies (requires UV)
uv sync

# Run CLI chatbot
uv run python main.py

# Run Streamlit web UI
uv run streamlit run streamlit_app.py

# Initialize or rebuild the vector database from data/
uv run python scripts/init_vector_db.py

# Add a document to the vector database
uv run python scripts/add_document.py
```

There is no test suite or lint configuration currently in the project.

## Environment Setup

Copy `.env.example` to `.env` and set:
- `OPENAI_API_KEY` — required
- `OPENAI_MODEL` — defaults to `gpt-4-turbo-preview`
- `VECTOR_DB_PATH` — defaults to `./vector_db`

Run `uv run python scripts/init_vector_db.py` after setup to populate the Chroma vector DB.

## Architecture

### LangGraph Workflow (`workflow/`)

The core is a **LangGraph state machine** (`workflow/graph.py`) where each agent is a node. Execution follows this conditional flow:

```
User Input → [Router] → [Diagnosis] → [Analysis] → [Care Guide] → [Simulation?] → Response
                    ↘ [Ingredient Analysis] ↗
                    ↘ [Web Search] ↗
```

- **`workflow/state.py`** — Defines `AgentState` (TypedDict), the shared state passed between all nodes
- **`workflow/router.py`** — LLM-based intent classifier; sets `routing_target` and `user_intent` on state
- **`workflow/nodes.py`** — Wraps each agent as a LangGraph node function
- **`workflow/graph.py`** — Assembles the graph with conditional edges based on router output

### Agents (`agents/`)

All agents inherit from `BaseAgent` (`agents/base_agent.py`), which provides:
- `ChatOpenAI` LLM initialization
- Vector DB similarity search via Chroma
- DuckDuckGo web search fallback when retrieval is insufficient
- Conversation history management

Specialized agents:
| Agent | File | Purpose |
|-------|------|---------|
| `SkinDiagnosisAgent` | `skin_diagnosis_agent.py` | Diagnoses skin type and current issues |
| `SkinAnalysisAgent` | `skin_analysis_agent.py` | Comprehensive analysis using diagnosis context |
| `CareGuideAgent` | `care_guide_agent.py` | AM/PM routines and weekly care plans |
| `SimulationAgent` | `simulation_agent.py` | Short/mid/long-term improvement predictions |
| `IngredientAnalysisAgent` | `ingredient_analysis_agent.py` | Analyzes skincare product ingredients |
| `WebSearchAgent` | `web_search_agent.py` | DuckDuckGo search for latest information |

### Knowledge Base (`data/`)

Markdown files embedded into the Chroma vector DB by `scripts/init_vector_db.py`:
- `data/피부관리의기초.md` — Core skin care principles
- `data/skin_type_cards/` — 11 skin type diagnostic cards (Korean)
- `data/ingredient_cards/` — Ingredient information cards

The vector DB is stored locally at `./vector_db/` (git-ignored).

### Configuration (`config/settings.py`)

Uses `pydantic-settings` to load and validate environment variables. Import `Settings` from `config` to access configuration values.

## Key Design Patterns

- **RAG with fallback**: Each agent first queries the Chroma vector DB; if results are insufficient, it falls back to DuckDuckGo web search.
- **State threading**: All agents read from and write to the shared `AgentState` TypedDict; no direct agent-to-agent calls.
- **Conditional routing**: The router node sets `routing_target`; `workflow/graph.py` uses conditional edges to skip irrelevant agents.
- **Conversation context**: `AgentState.conversation_history` is maintained across turns and injected into agent prompts.
