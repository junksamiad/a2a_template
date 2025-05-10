# Urmston Town Chatbot A2A Service: Project Overview and Current Objectives

## 1. Broader Project Goal: Urmston Town Chatbot A2A Service

We are developing the **"Urmston Town Chatbot,"** an AI-powered Agent-to-Agent (A2A) service.

*   **Purpose:** This service will enable other AI agents or A2A-compatible clients to programmatically interact with it. The goal is to provide information and perform actions related to Urmston Town Juniors Football Club (e.g., checking team vacancies, registering interest, etc.).
*   **Core Technology Stack:**
    *   **Backend:** Python with FastAPI (for the web server framework).
    *   **AI Logic:** OpenAI Agents SDK (for core conversational AI and skill execution).
    *   **Containerization:** Docker (for packaging the application).
    *   **A2A Compliance:** The `python-a2a` library (to adhere to A2A communication protocols).
*   **Key Application Components (primarily within `urmston_town_chatbot/chatbot_src/`):**
    *   `server.py`: The FastAPI application responsible for serving the A2A discovery card and exposing A2A skill endpoints. It utilizes `A2AServer` from `python-a2a`.
    *   `skills.py`: Defines the A2A skills (e.g., `check_team_spaces`) that the agent can perform. These skills leverage an `orchestrator_agent`.
    *   `go.py`: Contains the definition of the `orchestrator_agent` (using `openai-agents` SDK) and its associated tools. Initially, this might use placeholder data (e.g., `_FAKE_TEAM_DB`), with plans to integrate with real data sources like Airtable.
    *   `agent.json`: The A2A discovery card. This JSON file describes the agent's metadata, capabilities (skills), and its base URL, making it discoverable by other A2A clients.
    *   `Dockerfile`: Defines the Docker image for deploying the application.
    *   `requirements-a2a.txt`: Python dependencies.

## 2. Current Focused Task: Initial Elastic Beanstalk Deployment

Our immediate objective is to deploy the core A2A service components to **AWS Elastic Beanstalk** in the `eu-north-1` region.

*   **Specific Goal:** To establish a stable, public HTTPS endpoint for the A2A service, primarily to serve the `agent.json` discovery card. The target URL for this initial deployment will be the AWS-issued Elastic Beanstalk URL, formatted like `http://<environment-name>.<region>.elasticbeanstalk.com/.well-known/agent.json`.
*   **Components Being Deployed in this Phase:** `Dockerfile`, `server.py`, `skills.py`, and `agent.json`.

## 3. Context and "Why" for the Current Task

This initial deployment to Elastic Beanstalk is a critical foundational step for several reasons:

*   **Enable A2A Discovery:** A public HTTPS endpoint is essential for any A2A service. It's how other agents/clients will find (discover) your Urmston Town Chatbot and learn about its capabilities by fetching the `agent.json` card.
*   **Verify `agent.json` Serving:** We need to confirm that the `agent.json` card is correctly served from the `/.well-known/agent.json` path on the live Elastic Beanstalk environment.
*   **Validate Basic A2A Functionality & Deployment Pipeline:** This step allows us to:
    *   Test the core FastAPI web server setup in a deployed environment.
    *   Ensure the `python-a2a` library integration for handling A2A protocol specifics is working.
    *   Confirm that the Docker containerization defined in `Dockerfile` functions as expected on Elastic Beanstalk.
    *   Validate the Elastic Beanstalk deployment process itself.
*   **Iterative Development:** This approach is iterative. By getting the foundational web service and A2A layers working and publicly accessible, we create a stable platform. This allows us to confirm these core aspects before integrating more complex backend logic (like the planned Airtable integration for real team data, which will eventually replace any placeholder data mechanisms like `_FAKE_TEAM_DB`).

## 4. Next Major Step After Successful EB Deployment: Custom Domain

Once the Elastic Beanstalk application is running and the `agent.json` is accessible via the AWS-issued URL, the next significant step will be to make it accessible via the club's custom domain: `https://urmstontownjfc.co.uk/.well-known/agent.json`.

This will be achieved using a reverse-proxy strategy:

*   **AWS API Gateway:**
    *   Create a REST API with proxy resources:
        *   `ANY /.well-known/{proxy+}` will forward requests to the corresponding path on the Elastic Beanstalk application URL.
        *   `ANY /tasks/{proxy+}` will also forward requests to the corresponding path on the Elastic Beanstalk application URL.
*   **Custom Domain in API Gateway:**
    *   Set up `urmstontownjfc.co.uk` as a custom domain.
    *   Map base paths (`/.well-known` and `/tasks`) to the API Gateway stage serving the proxy resources.
*   **AWS Route 53:**
    *   Create an A Alias record for `urmstontownjfc.co.uk` pointing to the API Gateway custom domain.
*   **HTML Hook (for crawler fallback):**
    *   Add `<link rel="agent" href="https://urmstontownjfc.co.uk/.well-known/agent.json">` to the `<head>` of the existing Hostinger-hosted website.

This setup ensures that the chatbot's A2A interface is discoverable and usable under the official club domain, while the service logic is reliably hosted on Elastic Beanstalk.

## 5. Progress as of 2025-05-09

We have successfully achieved several key milestones:

*   **Elastic Beanstalk Deployment:**
    *   The core A2A service (FastAPI application using Docker) has been successfully deployed to AWS Elastic Beanstalk in the `eu-north-1` region.
    *   **Application Name:** `urmston-town-a2a-agent`
    *   **Environment Name:** `urmston-town-a2a-agent-dev`
    *   **Platform:** Docker running on 64bit Amazon Linux 2023.
    *   **Current CNAME (URL):** `http://urmston-town-a2a-agent-dev.eba-39a4mdxw.eu-north-1.elasticbeanstalk.com`
    *   The `agent.json` discovery card is confirmed to be successfully served from `http://urmston-town-a2a-agent-dev.eba-39a4mdxw.eu-north-1.elasticbeanstalk.com/.well-known/agent.json`.
    *   A root `GET /` endpoint returning `{"message":"Urmston Town A2A Service is running"}` was added to `server.py` to satisfy basic health checks and confirm application responsiveness.

*   **IAM Configuration:**
    *   Initial issues with the `aws-elasticbeanstalk-service-role` were resolved by attaching the necessary `AWSElasticBeanstalkService` AWS-managed policy. This allows the Elastic Beanstalk service to correctly manage the environment resources.

*   **Custom Domain Setup (In Progress):**
    *   The groundwork for using the custom domain `https://urmstontownjfc.co.uk` has begun:
        *   An **AWS API Gateway REST API** named `UrmstonTownA2AProxy` has been created in the `eu-north-1` region.
        *   Within this API, **proxy resources** have been configured:
            *   `/.well-known/{proxy+}` forwarding to the Elastic Beanstalk URL for the agent card.
            *   `/tasks/{proxy+}` forwarding to the Elastic Beanstalk URL for A2A skill endpoints.
        *   The API Gateway configuration has been **deployed to a `prod` stage**, with the Invoke URL: `https://yztnm78fi1.execute-api.eu-north-1.amazonaws.com/prod`.
        *   An **SSL Certificate has been requested from AWS Certificate Manager (ACM)** for `urmstontownjfc.co.uk` (Certificate ARN: `arn:aws:acm:eu-north-1:650251723700:certificate/5707681f-f96a-486f-b167-4365b13db6cf`).
        *   The **DNS CNAME record required for ACM validation** has been successfully added to the domain's DNS settings at Hostinger.
        *   **Current Status:** We are currently awaiting the ACM certificate to be issued (status to change from "Pending validation" to "Issued").

Once the ACM certificate is issued, the next steps will involve completing the custom domain setup in API Gateway and configuring the DNS records in Route 53 (or Hostinger, as appropriate for the A Alias record). 