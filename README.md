# 🌉 RakyatBridge: Multilingual Agentic Swarm for Public Services
**The Boss Raid 24 Hours Gemini Nexus The Agentverse Virtual Hackathon Level 10 Build with AI Hackathon Track A Submission: Intelligence Bureau** | **Theme: Strategic Research Swarm**

RakyatBridge is an autonomous, multi-agent system designed to bridge the "Information Gap" in public services. It takes unstructured local dialects (e.g., Penang Hokkien, Manglish), translates them, securely searches complex government policies via local MCP servers, and recursively simplifies the results to a 5th-grade reading level.

---

## 🧠 System Architecture Diagram (A2A Flow)
*Note: The dotted lines represent the **Agentic Recovery Loop**. If the AI encounters unknown slang, it does not hallucinate; it autonomously pauses, logs a reasoning trace, and calls a local dictionary tool via MCP to recover.*

```mermaid
graph TD
    User((User)) -->|1. Enters Dialect Query| UI[Streamlit UI & Reasoning Terminal]
    UI -->|2. Raw Input| Guardrails{Google ADK Safety Guardrails}

    %% System Robustness
    Guardrails -->|Blocked: Jailbreak/Off-Topic| Alert[Reject & Log Alert to UI]
    Guardrails -->|Approved: Public Service| Linguist[Agent 1: The Linguist]

    %% Agentic Agency & Recovery Loop
    Linguist -->|3. Attempt Translation| EvalConfidence{Confidence > 90%?}
    
    EvalConfidence -.->|No: Unknown Slang Detected| FallbackLog[Log Reasoning Trace]
    FallbackLog -.->|4a. Call MCP Tool| MCP_Dict[MCP Server: Dictionary Lookup]
    MCP_Dict <-->|Read| Dict[(dialect_glossary.json)]
    MCP_Dict -.->|4b. Return Formal Term| Linguist
    
    EvalConfidence -->|Yes: Successful Translation| Researcher[Agent 2: The Researcher]

    %% Technical Depth & Unstructured Data
    Researcher -->|5a. A2A Call: Need Policy Data| MCP_Policy[MCP Server: Policy Search]
    MCP_Policy <-->|Vector Search| Policy[(unstructured_policies.txt)]
    MCP_Policy -->|5b. Return Complex Govt Text| Simplifier[Agent 3: The Simplifier]

    %% Simplification & Final Output
    Simplifier -->|6. Condense to 5th-Grade Level| Linguist_Reverse[Agent 1: The Linguist]
    Linguist_Reverse -->|7. Translate back to Dialect| UI