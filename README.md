# Integration: Neo4j Knowledge Graph + MongoDB + Salesforce via n8n

This repository contains an end-to-end integration demo connecting a Neo4j knowledge graph, MongoDB Atlas, and Salesforce using n8n as the orchestration layer. 

The repo includes example LWC components, Apex scripts, and configuration examples to reproduce the integration and perform sanity tests.

Core files

- Project config: [sfdx-project.json](sfdx-project.json)
- NPM scripts, lint and tests: [package.json](package.json)
- LWC demo component: [force-app/main/default/lwc/agentQuery/agentQuery.js](force-app/main/default/lwc/agentQuery/agentQuery.js) (component class: [`AgentQuery`](force-app/main/default/lwc/agentQuery/agentQuery.js)), [agentQuery.html](force-app/main/default/lwc/agentQuery/agentQuery.html), [agentQuery.js-meta.xml](force-app/main/default/lwc/agentQuery/agentQuery.js-meta.xml)
- LWC unit test example: [force-app/main/default/lwc/agentQuery/__tests__/agentQuery.test.js](force-app/main/default/lwc/agentQuery/__tests__/agentQuery.test.js)
- Example Apex & SOQL scripts: [scripts/apex/hello.apex](scripts/apex/hello.apex), [scripts/soql/account.soql](scripts/soql/account.soql)
- Dev/debug config: [.vscode/launch.json](.vscode/launch.json)
- Jest config: [jest.config.js](jest.config.js)
- ESLint config: [eslint.config.js](eslint.config.js)

Overview of steps
1. Preparing Aura-agent, MongoDB Atlas, data load scripts and sanity testing
   - Prepare the Aura/agent service (the "Aura-agent") that will interact with the knowledge graph.
   - Provision MongoDB Atlas and create the necessary databases/collections.
   - Create vector index in Atlas manually (Automatic does not work in free version) 
   - Load sample data using provided scripts provided for Mongo and Neo4j (customize per environment).
   - Run sanity queries from MongoDB and Neo4j to verify data integrity.

The data to load is in  directory step1. Set the environment file. Then run the script

## Images for Aura configuration 

![Aura config  ](aurasetup/auraagent1.jpeg)
![Aura config  ](aurasetup/auraagent2.jpeg)
![Aura config  ](aurasetup/auraagent3.jpeg)
![Aura config  ](aurasetup/auraagent4.jpeg)


## Images for Mongo configuration 

![Mongo config  ](mongosetup/mongochunkrecord.jpeg)
![Mongo config  ](mongosetup/mongovectorsearchindex.jpeg)

2. Configure n8n flows (nodes) and sanity test them

![Alt text](image-url)
## Architechure of workflow in n8n

![Architechure of n8n  ](n8nsetup/n8narchitechure.jpeg)

### Testing command

<pre>

curl -s -X POST https://raga2560.app.n8n.cloud/webhook-test/sfinterface  -H "Content-Type: application/json" -H "Accept: application/json,text/event-stream" -d @question.json

</pre>


### Contents of question.json

<pre>

{    "question": "find the relationship for Systemic Lupus Erythematosus and skin lesions" }

</pre>

   - Create n8n workflows that:
     - Query Neo4j (REST or Bolt via a connector).
     - Read/write to MongoDB Atlas.
     - Call Salesforce endpoints (Apex REST, Platform Events or standard REST).
     - Communicate with the Aura-agent (HTTP nodes).
   - Use test nodes / execute workflow runs in n8n to validate nodes individually.



3. Connect Aura-agent, MongoDB, and Salesforce through n8n; sanity test end-to-end
   - Wire up n8n workflows to orchestrate the full path:

4. Demonstration
   - Record or demo the complete integration showing:
     - LWC UI in Salesforce invoking the Aura-agent via n8n.
     - n8n workflows processing and persisting data to MongoDB.
     - Knowledge graph lookups in Neo4j and returned responses in Salesforce.

## Image of demo working on salesforce

![Demo working on salesforce ](salesforcesetup/salesforceworking.jpeg)


How to run local checks and tests
- Lint JS files:
```bash
// filepath: run-lint.sh
# Run from repo root
npm run lint