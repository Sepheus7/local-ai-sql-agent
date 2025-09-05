from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import boto3


class BedrockToolUseClient:
    """
    Thin wrapper around Amazon Bedrock runtime (Converse/Invoke) with function calling support.
    """

    def __init__(self,
                 model_id: Optional[str] = None,
                 region: Optional[str] = None):
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.client = boto3.client("bedrock-runtime", region_name=self.region)

    def invoke_text(self, system: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "modelId": self.model_id,
            "input": {
                "messages": messages,
                "system": system,
            },
            "anthropic_version": "bedrock-2023-05-31"
        }
        if tools:
            payload["tools"] = tools

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(payload)
        )
        body = json.loads(response["body"].read())
        return body



