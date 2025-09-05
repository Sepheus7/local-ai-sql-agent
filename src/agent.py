# src/agent.py
import boto3
import json
from typing import Dict, List, Optional
import pandas as pd

bucket_name = "llm-sandbox-842676020002"

class DataAgent:
    def __init__(self):
        self.bedrock = boto3.client(
            service_name='bedrock',
            region_name='us-east-1'  # ensure Llama 2 is available in your region
        )
        self.athena = boto3.client('athena')
        self.s3 = boto3.client('s3')
        
    def generate_sql(self, user_question: str) -> str:
        """Convert natural language to SQL using Llama 2 via Bedrock"""
        prompt = f"""You are an expert SQL writer. Convert the following question to SQL.
        
        Rules to follow:
        1. Only query from safe_marketing_metrics view
        2. Always include date filters
        3. No individual customer data
        4. Always aggregate results
        
        Table schema:
        safe_marketing_metrics (
            event_date DATE,
            platform STRING,
            campaign_id STRING,
            unique_users INTEGER,
            event_count INTEGER
        )
        
        Question: {user_question}
        
        First explain your approach, then write the SQL query.
        """
        
        body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 512,
            "temperature": 0.1,
            "top_p": 0.9
        })
        
        response = self.bedrock.invoke_model(
            modelId='meta.llama3-2-3b-instruct-v1:0',  # Llama 2 70B model
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['generation']

    def execute_query(self, sql: str) -> pd.DataFrame:
        """Execute query in Athena and return results"""
        response = self.athena.start_query_execution(
            QueryString=sql,
            ResultConfiguration={
                f'OutputLocation': 's3://{bucket_name}/query-results/'
            }
        )
        
        # Wait for query to complete
        query_execution_id = response['QueryExecutionId']
        waiter = self.athena.get_waiter('query_execution_complete')
        waiter.wait(
            QueryExecutionId=query_execution_id,
            WaiterConfig={'Delay': 1, 'MaxAttempts': 60}
        )
        
        # Get results
        result_df = pd.read_csv(f"s3://{bucket_name}/query-results/{query_execution_id}.csv")
        return result_df

# Testing function
def test_llama_connection():
    try:
        agent = DataAgent()
        test_question = "What was the total number of events by platform yesterday?"
        sql = agent.generate_sql(test_question)
        print("Successfully connected to Llama 2!")
        print("\nGenerated SQL:", sql)
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False