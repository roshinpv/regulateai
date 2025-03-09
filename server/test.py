

import openai
import json
import logging
import asyncio
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = openai.AsyncOpenAI(base_url="https://api.deepseek.com", api_key="sk-db7c0a2d025a4758ab3fcc9c49e1fa6d")

# System message for compliance extraction
SYSTEM_MESSAGE = """You are a regulatory compliance expert. Analyze the provided document and extract structured information about regulations, agencies, jurisdictions, compliance steps, and risk assessment mappings.

Your response should be a JSON object with the following structure:
{
  "regulations": [
    {
      "id": "REG-[UUID]",
      "title": "string",
      "agency_id": "AG-[UUID]",
      "jurisdiction_id": "JUR-[UUID]",
      "impact_level": "High|Medium|Low",
      "last_updated": "YYYY-MM-DD",
      "summary": "string",
      "category": "string",
      "effective_date": "YYYY-MM-DD",
      "compliance_deadline": "YYYY-MM-DD",
      "source_url": "string",
      "official_reference": "string"
    }
  ],
  "agencies": [
    {
      "id": "AG-[UUID]",
      "name": "string",
      "description": "string",
      "website": "string"
    }
  ],
  "jurisdictions": [
    {
      "id": "JUR-[UUID]",
      "name": "string",
      "code": "string",
      "type": "Global|Regional|National|State|Local"
    }
  ],
  "compliance_steps": [
    {
      "id": "CS-[UUID]",
      "regulation_id": "REG-[UUID]",
      "description": "string",
      "order": number
    }
  ],
  "risk_compliance_mapping": [
    {
      "regulation_id": "REG-[UUID]",
      "compliance_area": "string"
    }
  ],
  "related_regulations": [
    {
      "regulation_id": "REG-[UUID]",
      "related_regulation_id": "REG-[UUID]"
    }
  ]
}"""


async def analyze_document(text: str):
    """
    Analyzes a regulatory document using OpenAI and extracts structured compliance information.

    Args:
        text (str): The document text to analyze.

    Returns:
        dict: Extracted compliance information as a JSON object, or None if an error occurs.
    """
    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": text}
            ],
            temperature=0.2,  # Reduce randomness for consistency
            max_tokens=2000
        )

        # Extract response content
        if response.choices and response.choices[0].message.content:
            extracted_data = response.choices[0].message.content
            return extracted_data

        logger.warning("No response content received from OpenAI.")
        return None

    except json.JSONDecodeError:
        logger.error("Failed to parse OpenAI response as JSON.")
        return None
    except Exception as e:
        logger.error(f"Error analyzing document with OpenAI: {e}")
        return None


# Example usage
if __name__ == "__main__":
    sample_text = "Sample regulatory text regarding financial compliance in the EU."

    result = asyncio.run(analyze_document(sample_text))

    if result:
        print(result)
    else:
        print("Failed to analyze the document.")
