# Integration: Neo4j Knowledge Graph + MongoDB Atlas + Salesforce via n8n

This repository demonstrates an end-to-end integration connecting a Neo4j knowledge graph, MongoDB Atlas, and Salesforce, with n8n as the orchestration layer. It includes example LWC components, Apex scripts, data-load scripts, and n8n workflow configurations you can reuse to reproduce the integration and run sanity tests.

## Repository layout (high level)

- `force-app/` — Salesforce metadata (LWC components, Apex, etc.)
- `n8nsetup/`, `mongosetup/`, `aurasetup/`, `salesforcesetup/` — screenshots and configuration images
- `step1/` — data-load scripts and environment templates
- `scripts/` — example Apex and SOQL scripts

## Architecture

![n8n architecture](n8nsetup/n8narchitechure.jpeg)

## Demo

Screenshot: Salesforce demo

![Salesforce demo](salesforcesetup/salesforceworking.jpeg)

Video walkthrough

[Watch the demo video](https://www.youtube.com/watch?v=wOy2NtS1X6w)

## Screenshots and configuration images

### Aura-agent

| Prompt UI | External settings |
|---:|:---|
| ![Aura prompt UI](aurasetup/auraagent1.jpeg) | ![Aura external settings](aurasetup/auraagent2.jpeg) |
| Tool configuration | Access link |
| ![Tool config](aurasetup/auraagent3.jpeg) | ![Access link config](aurasetup/auraagent4.jpeg) |

### MongoDB Atlas

![Mongo chunked record](mongosetup/mongochunkrecord.jpeg)
![Mongo vector search index](mongosetup/mongovectorsearchindex.jpeg)

### n8n flow configuration (selected nodes)

| AI-Agent | Aura-Agent |
|---:|:---|
| ![AI-Agent](n8nsetup/aiagentconfig.jpeg) | ![Aura-Agent](n8nsetup/auraagentconfig.jpeg) |
| Credentials | Model configuration |
| ![Credentials](n8nsetup/auraagentcredential.jpeg) | ![Model](n8nsetup/modelforagent.jpeg) |
| Embedding configuration | MongoDB query |
| ![Embeddings](n8nsetup/embeddingformongoquery.jpeg) | ![Mongo query](n8nsetup/mongoquery.jpeg) |
| Respond to webhook | Webhook for Salesforce |
| ![Respond to webhook](n8nsetup/respondtowebhook.jpeg) | ![Salesforce webhook](n8nsetup/webhookforsalesforcequery.jpeg) |

## Manual testing

Use the following `curl` example to test the n8n webhook that interfaces with Salesforce (replace the URL and payload as needed):

```powershell
curl -s -X POST "https://raga2560.app.n8n.cloud/webhook-test/sfinterface" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -d @question.json
```

Contents of `question.json`:

```json
{
  "question": "find the relationship for Systemic Lupus Erythematosus and skin lesions"
}
```

## Step-by-step overview

### Step 1 — Prepare Aura-agent, MongoDB Atlas, and data

- Build or deploy the Aura-agent service (the component that bridges Salesforce and the knowledge graph).
- Provision a MongoDB Atlas cluster and create the required databases/collections.
- Create the vector search index in Atlas (manual creation is often required for free tiers).
- Load sample data using the scripts in the `step1/` directory. Configure the provided `.env` file before running the scripts.
- Run basic queries in MongoDB and Neo4j to verify the data was loaded correctly.

### Step 2 — Configure n8n workflows

- Create workflows that query Neo4j, read/write to MongoDB Atlas, call Salesforce endpoints (Apex REST or Platform Events), and exchange requests with the Aura-agent.
- Test each node in n8n individually using the node execution features.

### Step 3 — Connect systems and run end-to-end sanity tests

- Orchestrate the complete flow in n8n: Neo4j → n8n → MongoDB / Salesforce → Aura-agent (and the return path as needed).
- Trigger the flow from Salesforce (for example via the `AgentQuery` LWC) and verify that:
  - MongoDB documents are created/updated as expected.
  - Neo4j nodes/relationships are read or written as expected.
  - The Aura-agent responds and the final result is returned to Salesforce.

### Step 4 — Demonstration

- Record demos showing the LWC invoking a workflow, n8n processing the request, MongoDB/Neo4j responses, and the final response shown in Salesforce.

## Notes and tips

- Place screenshots and configuration images under `n8nsetup/`, `mongosetup/`, `aurasetup/`, and `salesforcesetup/`.
- If you use the MongoDB Atlas free tier, vector index creation may require manual steps in the Atlas UI.
- Customize the provided scripts and `.env` files before running them in your environment.

## Useful file locations

- LWC example: `force-app/main/default/lwc/agentQuery/`
- Data-load scripts: `step1/`
- Example Apex & SOQL: `scripts/apex/`, `scripts/soql/`

## Contributing

Contributions are welcome. Please open issues or pull requests with clear descriptions and reproduction steps.

## License

Add a `LICENSE` file to this repository to indicate the intended license.
# Integration: Neo4j Knowledge Graph + MongoDB + Salesforce via n8n

This repository contains an end-to-end integration demo connecting a Neo4j knowledge graph, MongoDB Atlas, and Salesforce using n8n as the orchestration layer. 

The repo includes example LWC components, Apex scripts, and configuration examples to reproduce the integration and perform sanity tests.


## 1.0 Architecture of workflow in n8n

![Architecture of n8n  ](n8nsetup/n8narchitechure.jpeg)

## 2.0 The Salesforce demo 

![Demo working on salesforce ](salesforcesetup/salesforceworking.jpeg)

[![Demo of working n8n integration ](https://img.youtube.com/vi/wOy2NtS1X6w/0.jpg)](https://www.youtube.com/watch?v=wOy2NtS1X6w)




## 3.0 Images for Aura configuration 

| Auraagent-Prompt | Auraagent-External |
|-----------|-------|
| ![Aura config  ](aurasetup/auraagent1.jpeg)      | ![Aura config  ](aurasetup/auraagent2.jpeg) |
| Auraagent-Tool | Auraagent-Access link |
| ![Aura config  ](aurasetup/auraagent3.jpeg)      | ![Aura config  ](aurasetup/auraagent4.jpeg) |



## 4.0 Images for Mongo configuration 

![Mongo config  ](mongosetup/mongochunkrecord.jpeg)
![Mongo config  ](mongosetup/mongovectorsearchindex.jpeg)





## 5.0 Flow configuration at n8n

| AI-Agent config | Aura-Agent config |
|-----------|-------|
| ![AI-Agent config  ](n8nsetup/aiagentconfig.jpeg)      | ![Aura-Agent config  ](n8nsetup/auraagentconfig.jpeg)  |
| Aura-Agent credential | Model for agent |
| ![AI-Agent credential  ](n8nsetup/auraagentcredential.jpeg) | ![Model for Agent  ](n8nsetup/modelforagent.jpeg) |
| Embedding form mongo query  | Mongo query |
| ![Embedding for mongo query  ](n8nsetup/embeddingformongoquery.jpeg) | ![Mongo query  ](n8nsetup/mongoquery.jpeg) |
| Respond to webhook  | webhook for salesforce query |
| ![ Respondtowebhook  ](n8nsetup/respondtowebhook.jpeg) | ![webhookforsalesforcequery ](n8nsetup/webhookforsalesforcequery.jpeg) |


## 6.0 Manual Testing 

### Testing command

<pre>

curl -s -X POST https://raga2560.app.n8n.cloud/webhook-test/sfinterface  -H "Content-Type: application/json" -H "Accept: application/json,text/event-stream" -d @question.json

</pre>


### Contents of question.json

<pre>

{    "question": "find the relationship for Systemic Lupus Erythematosus and skin lesions" }

</pre>



## 7.0 Overview of step-1
1. Preparing Aura-agent, MongoDB Atlas, data load scripts and sanity testing
   - Prepare the Aura/agent service (the "Aura-agent") that will interact with the knowledge graph.
   - Provision MongoDB Atlas and create the necessary databases/collections.
   - Create vector index in Atlas manually (Automatic does not work in free version) 
   - Load sample data using provided scripts provided for Mongo and Neo4j (customize per environment).
   - Run sanity queries from MongoDB and Neo4j to verify data integrity.

The data to load is in  directory step1. Set the environment file. Then run the script

   


## 8.0 Connect Aura-agent, MongoDB, and Salesforce through n8n and do sanity test end-to-end

   - Wire up n8n workflows to orchestrate the full path:

   ![Architecture of n8n  ](n8nsetup/n8narchitechure.jpeg)


## 9.0 Demonstration

   - Record or demo the complete integration showing:
     - LWC UI in Salesforce invoking the n8n workflow through Salesforce Apex.
     - n8n workflows processing the request.
     - Mongodb query processing 
     - Knowledge graph lookup in Neo4j via Aura-agent 
     - The reply from Mongodb and Aura-agent summarised by AI-agent 
     - Then the response returned to Salesforce.



[![Demo of working n8n integration ](https://img.youtube.com/vi/wOy2NtS1X6w/0.jpg)](https://www.youtube.com/watch?v=wOy2NtS1X6w)

