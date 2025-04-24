import os

import boto3

bedrock_agent_runtime = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name="us-east-1",
)


class Retriever:
    def __init__(self, message: str, session_id: str | None):
        self.message = message
        self.session_id = session_id
        pass

    def retrieve_and_respond(self):
        retrieve_config = {
            "retrieveAndGenerateConfiguration": {
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": os.getenv("KNOWLEDGE_BASE_ID", ""),
                    "modelArn": os.getenv("BEDROCK_MODEL_ARN", ""),
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 5,
                            "overrideSearchType": "HYBRID",
                        }
                    },
                    "generationConfiguration": {
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "maxTokens": 4096,
                                "temperature": 0.7,
                                "topP": 0.9,
                            }
                        }
                    },
                },
            }
        }

        input_data = {"text": self.message}

        session_config = {}
        if self.session_id:
            session_config["sessionId"] = self.session_id

        self.response = bedrock_agent_runtime.retrieve_and_generate(
            input=input_data,
            retrieveAndGenerateConfiguration=retrieve_config[
                "retrieveAndGenerateConfiguration"
            ],
            **session_config,
        )
        return self.response

    def format_result(self):
        try:
            answer = self.response.get("output", {}).get("text", "")
            citations = []
            if "citations" in self.response:
                for citation in self.response["citations"]:
                    retrieved_references = citation.get("retrievedReferences", [])
                    for reference in retrieved_references:
                        citations.append(
                            {
                                "content": reference.get("content", {}).get("text", ""),
                            }
                        )
            session_id = self.response.get("sessionId", "")
            return {
                "answer": answer,
                "citations": citations,
                "session_id": session_id,
            }
        except Exception as e:
            return {
                "error": f"Failed to format result: {str(e)}",
                "raw_response": self.response,
            }
