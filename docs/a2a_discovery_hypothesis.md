# A2A Agent Discovery Hypothesis for a Personal AI Agent

## 1. Introduction

This document outlines a hypothesized method by which a personal AI agent (e.g., an OpenAI Assistant wrapped with A2A client capabilities) could autonomously discover and interact with external Agent-to-Agent (A2A) enabled services on the internet. The goal is to allow the personal agent to find and utilize specialized third-party agents to fulfill user queries that are beyond its own built-in tools or knowledge.

## 2. Core Scenario

A user interacts with their personal AI agent. The personal agent attempts to fulfill the query using its own capabilities. If it cannot, it determines that it needs to find an external A2A agent that might be able to assist.

## 3. Proposed Discovery and Interaction Workflow

The personal AI agent would follow these steps:

### Step 1: Identify Need for External A2A Agent

The personal agent's internal logic or prompt engineering would guide it to recognize when a query requires capabilities it doesn't possess. For example, its prompt might include instructions like:

> "You are a helpful assistant. Try to solve every query. If you cannot solve a query using any of the tools you have available, then you may attempt to find an external A2A agent that can help."

### Step 2: Formulate a Web Search Query

Based on the user's original query or the identified need, the personal agent formulates a targeted web search query to find potential services or domains that might offer the required capability.

*   **Example 1 (General Service):** If the user asks for recommendations for "new high heel shoes," the agent might search for "new high heel shoes retailer" or "online shoe stores."
*   **Example 2 (Specific Service):** If the user asks to "book a session at Inflate-a-Nation kids activity centre," the agent might search directly for "Inflate-a-Nation kids activity centre."

### Step 3: Execute Web Search & Identify Candidate Base URLs

The agent executes the web search (e.g., via a search tool it has access to). From the search results, it extracts promising base URLs of websites (e.g., `https://<retailer_base_url>`, `https://inflatanation.com`).

### Step 4: Probe for A2A Agent Card using Well-Known URI

For each candidate base URL identified, the personal agent attempts to discover an A2A agent by appending the standard A2A discovery path to the base URL:

`https://<candidate_base_url>/.well-known/agent.json`

The agent then makes an HTTP GET request to this constructed URL.

### Step 5: Evaluate Response

*   **Successful Discovery (HTTP 200 OK & Valid JSON):**
    *   If the request returns an HTTP 200 OK status code and the response body is a valid JSON document conforming to the A2A `agent.json` schema, the personal agent has successfully discovered an A2A agent.
    *   The agent parses the `agent.json` card to understand the discovered agent's capabilities (from the `skills` array) and, crucially, its `base_url` for task execution (which might be the same as the discovery base URL or different).
*   **Failed Discovery (e.g., HTTP 404, Connection Error, Invalid JSON):**
    *   If the request results in an error (like a 404 Not Found, connection timeout) or if a 200 OK is returned but the content is not valid JSON, the personal agent concludes that no A2A agent is discoverable at that path for the candidate domain.
    *   The agent would then move on to the next candidate base URL from its search results or refine its search if all initial candidates fail.

### Step 6: (If Successful Discovery) Formulate and Send Task Request

If an A2A agent is successfully discovered and its `agent.json` indicates it has the required skill(s):

1.  The personal agent uses the `base_url` from the discovered agent card.
2.  It constructs an A2A task request payload (as per A2A protocol specifications) for the desired skill.
3.  It sends this task request (typically an HTTP POST) to the appropriate task endpoint (e.g., `https://<discovered_agent_base_url>/tasks/send`).
4.  It then handles the response from the external A2A agent.

## 4. Key Assumptions & Considerations

*   **Personal Agent Capabilities:** The personal agent needs access to a web search tool and the ability to make HTTP GET (for discovery) and HTTP POST (for tasks) requests.
*   **A2A Client Wrapper:** The personal agent's core logic (e.g., the OpenAI Assistant) would be wrapped by or interact with an A2A client library/scaffold that handles the construction and parsing of A2A protocol messages.
*   **Error Handling:** The agent must be robust in handling failures at each step (web search returning no relevant results, candidate URLs not having A2A agents, network errors, etc.).
*   **Security & Trust:** This hypothesis does not yet detail how the personal agent would assess the trustworthiness of a discovered A2A agent or handle authentication if required by the external agent (though many initial discovery endpoints might be unauthenticated, as ours is).
*   **Scalability/Efficiency:** Repeatedly probing many URLs might be inefficient. Future refinements could involve caching discovered agents, using A2A directories (if they emerge), or more sophisticated heuristics for selecting candidate URLs.

## 5. Next Steps

*   Test the core discovery mechanism (`/.well-known/agent.json`) manually or with simple scripts against known and hypothetical endpoints.
*   Consult A2A protocol documentation for any standardized recommendations on discovery beyond the well-known URI or for directory services.
*   Begin prototyping the A2A client wrapper for the personal AI agent. 