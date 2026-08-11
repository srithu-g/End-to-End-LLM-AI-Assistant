# 🚀 End-to-End LLM AI Assistant

> **From a simple LLM API call to a complete AI system — routing, tool calling, conversation memory, validation, testing, and deployment.**

<p align="center">

**🔗 <a href="YOUR_STREAMLIT_URL">Live Demo</a>** &nbsp; | &nbsp;
**💻 <a href="YOUR_GITHUB_REPO_URL">GitHub Repository</a>**

</p>

---

## 🧠 What I Built

I built and deployed an **end-to-end LLM-powered AI assistant** to understand what actually happens beyond simply sending a prompt to an LLM.

The project brings together the major components required to turn an LLM into a functional AI application:

```text
User Query
    ↓
Conversation Context
    ↓
LLM-Based Routing
    ↓
Tool Execution / Direct LLM Response
    ↓
Output Validation
    ↓
State & Logging
    ↓
Final Response
🔍 How It Works
1. The user sends a query

For example:

"What's 25% of 480?"

The request enters through the Streamlit interface.

2. Conversation context is managed

The Conversation Manager maintains the current session history and provides relevant context for follow-up questions.

This led to one of the most important concepts I understood through this project:

The LLM itself is stateless. Conversation memory has to be engineered around the model.

The application therefore manages the conversation state separately instead of expecting the model to inherently remember previous interactions.

3. The LLM determines the intent

The routing layer uses the LLM to determine what the user is trying to accomplish.

For example:

"What's 25% of 480?"
          ↓
      Calculator
"What's the weather in London?"
          ↓
      Weather API
"Tell me about the Transformer architecture."
          ↓
      Wikipedia

The important design decision is the separation between:

Routing → deciding what should happen

and

Tools → actually executing the operation

4. The selected tool executes

The system currently supports four tools:

Tool	Purpose
🧮 Calculator	Arithmetic calculations
🌤️ Weather API	Weather information
📖 Wikipedia	Factual summaries
📏 Unit Converter	Unit conversions

This makes the application more than a simple chatbot — the LLM can determine when external capabilities are required and route the request accordingly.

5. The output is validated

LLM-generated or externally retrieved data should not automatically be treated as valid application data.

The project uses Pydantic schemas to define expected structures at important boundaries.

Output
  ↓
Schema Validation
  ↓
 ┌───────────────┐
 │ Valid?        │
 └───────┬───────┘
         │
    ┌────┴────┐
    │         │
   YES        NO
    │         │
    ▼         ▼
 Continue   Retry /
           Fallback

This helped me understand that reliability is an engineering concern, not something the LLM automatically provides.

6. State and logging

The application tracks relevant state and tool usage throughout the pipeline.

This provides visibility into what happened during a request rather than treating the LLM interaction as an isolated API call.

💡 Key Engineering Concepts
🧠 Stateless LLM + External Memory

An LLM does not inherently maintain application conversation state.

LLM
 ↓
Stateless

Application
 ↓
Conversation Manager
 ↓
Relevant Context
 ↓
LLM

This separation keeps the routing layer focused on decision-making while conversation management handles state.

🧭 Routing vs Execution

The router determines:

"What should happen?"

The tool determines:

"How should it happen?"

This separation makes the system easier to extend, test, and maintain.

🛡️ Validation at System Boundaries

LLM outputs and external API responses can be unpredictable.

Schema validation establishes clear contracts between components and prevents invalid data from silently moving through the application.

🔄 Reliability Around LLMs

Real AI applications need to account for failures.

This project includes:

Schema validation
Retry logic
Fallback handling
Mocked LLM calls
Integration testing
Structured logging
🧪 Testing

The project uses multiple levels of testing.

Unit Tests

Individual tools and components are tested independently.

Mock Tests

LLM-dependent components can be tested without making real LLM API calls.

This makes tests faster, deterministic, and less expensive.

Integration Tests

The complete pipeline is tested end-to-end, including conversation state.

Run Tests
pytest tests/ -v
Run With Coverage
pytest tests/ --cov=app --cov-report=term-missing
🖥️ Example Interactions
Calculator
User:
What's 25% of 480?

Assistant:
25% of 480 is exactly 120.
Weather
User:
What's the weather in London?

Assistant:
[Weather API executed]
Knowledge Retrieval
User:
Tell me about the Transformer architecture.

Assistant:
[Wikipedia tool executed]
Unit Conversion
User:
Convert 100 Fahrenheit to Celsius.

Assistant:
100°F is 37.78°C.
Conversation Memory
User:
What did I ask first?

Assistant:
Your first question was about calculating 25% of 480.
📁 Project Structure
End-to-End-LLM-AI-Assistant/
│
├── app/
│   ├── main.py
│   ├── router.py
│   ├── llm_client.py
│   ├── state.py
│   ├── validator.py
│   ├── conversation.py
│   │
│   ├── ui/
│   │   └── streamlit_app.py
│   │
│   ├── prompts/
│   │   ├── routing_prompt.txt
│   │   └── response_prompt.txt
│   │
│   ├── tools/
│   │   ├── calculator.py
│   │   ├── weather_api.py
│   │   ├── wikipedia_tool.py
│   │   └── unit_converter.py
│   │
│   ├── schemas/
│   │   ├── tool_schema.py
│   │   ├── response_schema.py
│   │   ├── state_schema.py
│   │   └── conversation_schema.py
│   │
│   └── utils/
│       ├── logger.py
│       ├── config.py
│       └── helpers.py
│
├── tests/
│   ├── test_tools.py
│   ├── test_validator.py
│   ├── test_router.py
│   ├── test_conversation.py
│   └── test_end_to_end.py
│
├── examples/
│   ├── sample_inputs.md
│   ├── expected_outputs.md
│   └── sample_conversations.md
│
├── docs/
│   ├── CONCEPTS.md
│   ├── PROJECT_LIFECYCLE.md
│   ├── DEPLOYMENT.md
│   └── INTERVIEW_PREP.md
│
├── .env.example
├── requirements.txt
├── run.py
├── run_ui.py
└── README.md
🛠️ Tech Stack
Technology	Role
Python 3.10+	Core application
OpenAI / Anthropic API	LLM interaction
Streamlit	Interactive web interface
Pydantic v2	Schema validation
Requests	External API communication
python-dotenv	Environment configuration
pytest	Testing
Python Logging	Observability
🚀 Run Locally
1. Clone the repository
git clone YOUR_GITHUB_REPO_URL
cd End-to-End-LLM-AI-Assistant
2. Create a virtual environment
python -m venv venv
3. Activate the environment

Windows

venv\Scripts\activate

macOS / Linux

source venv/bin/activate
4. Install dependencies
pip install -r requirements.txt
5. Configure environment variables

Create a .env file using .env.example:

OPENAI_API_KEY=your_api_key_here

⚠️ Never commit your real API key to GitHub.

6. Start the application
streamlit run app/ui/streamlit_app.py
☁️ Deployment

The application is deployed using Streamlit Community Cloud.

Live Demo

🔗 YOUR_STREAMLIT_URL

The LLM API key is configured through Streamlit Secrets and is not stored in the repository.

📈 What I Learned

This project changed my understanding of what it means to build with LLMs.

Before this project, it was easy to think of an LLM application as:

Prompt → LLM → Response

After building the complete system, I now think of it as:

                 ┌───────────────┐
                 │   User / UI   │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │   Context     │
                 │   & Memory    │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │    Routing    │
                 │      LLM      │
                 └───────┬───────┘
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
        Direct LLM             Tool Calling
              │                     │
              └──────────┬──────────┘
                         ↓
                 ┌───────────────┐
                 │  Validation   │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │ State / Logs  │
                 └───────┬───────┘
                         ↓
                    Response
The biggest takeaway:

Building an AI application is not just about using an LLM. It is about engineering the system around the LLM.

That includes understanding:

Architecture → Routing → Tools → Context → Validation → Reliability → Testing → Deployment

🎯 Future Improvements

Potential extensions I would explore next:

 Persistent conversation memory
 Database-backed state
 Authentication and user management
 More advanced tool orchestration
 RAG integration
 LLM evaluation pipelines
 Production monitoring
 Containerized deployment
📚 Learning Resource & Credits

This project was built as part of my AI Engineering learning journey, using Joshith Reddy Aleti's AI Engineering Roadmap 2026 — Episode 4 as the primary learning resource.

The original project provided the foundation for exploring the complete lifecycle of an AI application — from architecture and implementation to testing, documentation, and deployment.

Original Project

Joshith Reddy Aleti — Your First End-to-End AI Project

https://github.com/JoshithReddyAleti/Episode_4_Your_First_End_To_End_AI_Project

AI Engineering Roadmap 2026

https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/

I have created this repository as my own learning implementation and portfolio version, while giving full credit to the original project and its author.

If you're learning AI Engineering, I highly recommend following the series.