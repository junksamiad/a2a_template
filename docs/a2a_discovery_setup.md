# A2A Agent Discovery & Endpoint Setup Guide: Urmston Town JFC

## 1. Introduction & Goal

This document details the infrastructure setup for serving an Agent-to-Agent (A2A) service for Urmston Town JFC. The primary goal is to make the A2A agent's discovery card (`agent.json`) and its task endpoints accessible via the custom apex domain `https://urmstontownjfc.co.uk`. Concurrently, the main club website, hosted on Hostinger, will continue to be served from the same apex domain for all other paths.

This setup utilizes several AWS services to achieve path-based routing, SSL termination, and scalable hosting for the A2A agent backend. Refer to `project.md` for the initial project overview and roadmap that led to this configuration.

## 2. Core Components & Architecture Overview

The request flow for A2A discovery and tasks is as follows:

`Client/User -> DNS (Hostinger) -> AWS CloudFront -> AWS API Gateway -> AWS Elastic Beanstalk <- A2A Agent Application (FastAPI/Docker)`

For requests to the main website (non-A2A paths):

`Client/User -> DNS (Hostinger) -> AWS CloudFront -> Hostinger Origin Server`

**Roles of Key AWS Services:**

*   **AWS Elastic Beanstalk (EB):** Hosts the Dockerized Python FastAPI application that implements the A2A agent logic, serves `agent.json`, and handles skill invocations.
*   **AWS Certificate Manager (ACM):** Provides SSL/TLS certificates for securing the custom domain. Two certificates are used: one in `us-east-1` for CloudFront (global service) and one in `eu-north-1` for the regional API Gateway custom domain endpoint.
*   **AWS API Gateway:** Acts as a regional HTTP proxy for the A2A-specific paths (`/.well-known/*` and `/tasks/*`), routing these requests from CloudFront to the Elastic Beanstalk environment. It also manages the custom domain integration at the API level.
*   **AWS CloudFront:** Serves as the global Content Delivery Network (CDN) and primary reverse proxy. It handles SSL termination for `https://urmstontownjfc.co.uk`, caches static content for the main website, and performs path-based routing to direct traffic to either the Hostinger origin (for the main site) or the API Gateway origin (for A2A services).

**External Services:**

*   **Hostinger:** Provides DNS hosting for `urmstontownjfc.co.uk` and web hosting for the main club website.
*   **Hostinger Website Builder:** Used to inject the A2A discovery HTML hook into the main website.

## 3. Elastic Beanstalk (EB) - Application Hosting

*   **Purpose:** Hosts the Dockerized FastAPI application that is the A2A agent.
*   **Region:** `eu-north-1` (Stockholm)
*   **Application Name:** `urmston-town-a2a-agent`
*   **Environment Name:** `urmston-town-a2a-agent-dev`
*   **Platform:** Docker running on 64bit Amazon Linux 2023 (Version: 4.5.1)
*   **Key Deployed Files (from `urmston_town_chatbot/chatbot_src/` directory):**
    *   `Dockerfile`: Defines the container image.
    *   `server.py`: FastAPI application. Includes a `GET /` route for basic health checks and a `GET /.well-known/agent.json` route to serve the discovery card. A2A server logic (using `A2AServer` from `python-a2a`) and skill routing for `/tasks/*` will be uncommented/implemented here.
    *   `agent.json`: The A2A discovery card. `base_url` is set to `https://urmstontownjfc.co.uk`.
    *   `skills.py` (to be fully implemented): Defines agent skills.
    *   `go.py` (to be fully implemented): Defines the orchestrator agent.
*   **EB Environment URL (direct access, primarily for testing/origin):** `http://urmston-town-a2a-agent-dev.eba-39a4mdxw.eu-north-1.elasticbeanstalk.com`
*   **IAM Role (`aws-elasticbeanstalk-service-role`):**
    *   Ensured this role exists and has the correct trust policy for `elasticbeanstalk.amazonaws.com`.
    *   Attached AWS Managed Policies:
        *   `arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth`
        *   `arn:aws:iam::aws:policy/AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy`
        *   `arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkService` (This was crucial for resolving initial deployment issues).

## 4. AWS Certificate Manager (ACM) - SSL/TLS Certificates

Two SSL certificates are utilized for `urmstontownjfc.co.uk`:

*   **Certificate 1 (for CloudFront - Global Service):**
    *   **Region:** `us-east-1` (N. Virginia) - *This is a strict requirement for CloudFront custom domain SSL.*
    *   **ARN:** `arn:aws:acm:us-east-1:650251723700:certificate/3425c090-0e17-47e9-91c4-3eb63c4ae301`
    *   **Validation Method:** DNS.
*   **Certificate 2 (for API Gateway Regional Custom Domain):**
    *   **Region:** `eu-north-1` (Stockholm) - *Must be in the same region as the API Gateway.*
    *   **ARN:** `arn:aws:acm:eu-north-1:650251723700:certificate/3afbee67-85b0-44c3-be5e-2e0cd74979f8`
    *   **Validation Method:** DNS.
*   **DNS Validation CNAME Record (in Hostinger):**
    *   The same CNAME record was successfully used by ACM to validate both certificates:
        *   Name: `_988a869cb7213679f3800048d0adc2f9.urmstontownjfc.co.uk.`
        *   Type: `CNAME`
        *   Value: `_4cea1e3eeb50fc0386114b4a3e6f6909.xlfgrmvvlj.acm-validations.aws.`
*   **CAA DNS Record (in Hostinger):**
    *   To allow AWS to issue certificates, the following CAA record was added:
        *   Type: `CAA`
        *   Name: `@` (for the apex domain)
        *   Flag: `0`
        *   Tag: `issue`
        *   Value: `"amazon.com"`

## 5. API Gateway - A2A Endpoint Proxy

*   **Purpose:** Provides a stable, regional HTTP proxy for A2A paths, abstracting the Elastic Beanstalk backend.
*   **Region:** `eu-north-1` (Stockholm)
*   **API Name:** `UrmstonTownA2AProxy`
*   **API Type:** REST API
*   **Endpoint Type:** Regional
*   **Stage:** `prod`
*   **Direct Invoke URL (for testing):** `https://yztnm78fi1.execute-api.eu-north-1.amazonaws.com/prod`
*   **Resources & HTTP Proxy Integrations:**
    *   **Path:** `/.well-known/{proxy+}`
        *   Method: `ANY`
        *   Integration Type: HTTP Proxy
        *   Endpoint URL: `http://urmston-town-a2a-agent-dev.eba-39a4mdxw.eu-north-1.elasticbeanstalk.com/.well-known/{proxy}`
    *   **Path:** `/tasks/{proxy+}`
        *   Method: `ANY`
        *   Integration Type: HTTP Proxy
        *   Endpoint URL: `http://urmston-town-a2a-agent-dev.eba-39a4mdxw.eu-north-1.elasticbeanstalk.com/tasks/{proxy}`
*   **Custom Domain Name in API Gateway:**
    *   Domain Name: `urmstontownjfc.co.uk`
    *   Associated ACM Certificate: The `eu-north-1` certificate (ARN ending `...2e0cd74979f8`).
    *   API Gateway domain name (used as an origin target by CloudFront): `d-fruh6gxt7l.execute-api.eu-north-1.amazonaws.com`
*   **API Mapping:**
    *   Custom domain `urmstontownjfc.co.uk` with an empty path (`/`) is mapped to the `prod` stage of the `UrmstonTownA2AProxy` API.
*   **Logging:** CloudWatch Execution Logs enabled for the `prod` stage (Log level: INFO, Log full requests/responses data).

## 6. AWS CloudFront - CDN & Path-Based Routing

*   **Purpose:** Main public entry point. Provides SSL termination for the custom domain, caches static website content, and routes traffic by path to appropriate backends (Hostinger or API Gateway).
*   **Distribution ID:** `E3LOKQLE8XX6FB`
*   **Distribution Domain Name (target for Hostinger ALIAS record):** `d2ambqou2ub92w.cloudfront.net`
*   **Settings:**
    *   **Alternate Domain Names (CNAMEs):** `urmstontownjfc.co.uk`
    *   **Custom SSL Certificate:** The `us-east-1` ACM certificate (ARN ending `...3eb63c4ae301`).
    *   **Supported HTTP Versions:** HTTP/2, HTTP/1.1, HTTP/1.0 (HTTP/3 also enabled).
    *   **Default Root Object:** `index.html` (or as appropriate for the Hostinger site).
    *   **Price Class:** Use all edge locations.
    *   **WAF:** Not enabled initially.
*   **Origins:**
    1.  **`Hostinger-Main-Site` (Default Origin):**
        *   Origin Domain: `connect.hostinger.com`
        *   Protocol: HTTPS only
    2.  **`APIGW-A2A-Proxy-Prod` (A2A Service Origin):**
        *   Origin Domain: `d-fruh6gxt7l.execute-api.eu-north-1.amazonaws.com` (the API Gateway custom domain's target)
        *   Origin Path: *Blank/Empty* (Crucial change from earlier attempts where `/prod` was incorrectly used here)
        *   Protocol: HTTPS only
*   **Behaviors (Order of precedence matters: specific paths before default):**
    1.  **Path Pattern:** `/.well-known/*`
        *   Origin: `APIGW-A2A-Proxy-Prod`
        *   Viewer Protocol Policy: Redirect HTTP to HTTPS
        *   Allowed HTTP Methods: `GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE`
        *   Cache Policy: `Managed-CachingDisabled`
        *   Origin Request Policy: `Managed-AllViewer`
    2.  **Path Pattern:** `/tasks/*`
        *   Origin: `APIGW-A2A-Proxy-Prod`
        *   Viewer Protocol Policy: Redirect HTTP to HTTPS
        *   Allowed HTTP Methods: `GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE`
        *   Cache Policy: `Managed-CachingDisabled`
        *   Origin Request Policy: `Managed-AllViewer`
    3.  **Path Pattern:** `Default (*)`
        *   Origin: `Hostinger-Main-Site`
        *   Viewer Protocol Policy: Redirect HTTP to HTTPS
        *   Allowed HTTP Methods: `GET, HEAD, OPTIONS` (Adjust if Hostinger site needs POST for forms etc.)
        *   Cache Policy: `UseOriginCacheControlHeaders` (or `Managed-CachingOptimized`)
        *   Origin Request Policy: `Managed-AllViewer` (or a more restrictive one like `Managed-UserAgentRefererHeaders` if suitable)

## 7. Hostinger DNS Configuration (`urmstontownjfc.co.uk`)

*   **CAA Records:**
    *   `@ 0 issue "amazon.com"`
    *   (Plus other existing CAA records for `letsencrypt.org`, `comodoca.com`, etc.)
*   **CNAME Record (for ACM validation):**
    *   Name: `_988a869cb7213679f3800048d0adc2f9`
    *   Target: `_4cea1e3eeb50fc0386114b4a3e6f6909.xlfgrmvvlj.acm-validations.aws.`
    *   TTL: `300`
*   **ALIAS Record (for routing apex domain to CloudFront):**
    *   Name: `@`
    *   Target/Content: `d2ambqou2ub92w.cloudfront.net` (CloudFront Distribution Domain Name)
    *   TTL: `300`

## 8. Hostinger Website Builder - HTML Hook

*   The following line was added to the `<head>` section of the main website via the "Integrations" -> "Custom code" feature in Hostinger's Website Builder:
    `<link rel="agent" href="https://urmstontownjfc.co.uk/.well-known/agent.json">`

## 9. Final Result & Testing

*   Accessing `https://urmstontownjfc.co.uk/` serves the main website hosted on Hostinger, routed through CloudFront.
*   Accessing `https://urmstontownjfc.co.uk/.well-known/agent.json` serves the A2A agent's discovery card, routed through CloudFront and API Gateway to the Elastic Beanstalk application.
*   Accessing `https://urmstontownjfc.co.uk/tasks/...` (once skills are implemented) will be routed similarly for A2A skill invocations.

This document provides a snapshot of the successfully configured infrastructure. 