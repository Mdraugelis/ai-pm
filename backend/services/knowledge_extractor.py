"""
Knowledge Extractor Service
AI Product Manager Agent - Backend

Extracts and classifies knowledge from blueprint documents using LLM.
Identifies content as: policy, guideline, procedure, reference, or example.
"""

import re
from typing import Any, Dict, Optional

import structlog
from anthropic import Anthropic

logger = structlog.get_logger(__name__)


# ============================================================================
# Knowledge Extractor
# ============================================================================


class KnowledgeExtractor:
    """
    Extract and classify knowledge from blueprint documents

    Uses LLM to analyze document content and:
    - Classify as policy/guideline/procedure/reference/example
    - Extract key sections and concepts
    - Generate summary for indexing
    - Determine confidence score

    Example:
        >>> extractor = KnowledgeExtractor(api_key="...")
        >>> result = await extractor.classify_blueprint("Policy text...")
        >>> print(result['blueprint_subtype'])  # "policy"
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize knowledge extractor

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model

        logger.info("KnowledgeExtractor initialized", model=model)

    async def classify_blueprint(
        self, content: str, filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify blueprint document content

        Args:
            content: Document content to classify
            filename: Optional filename for context

        Returns:
            Classification result with:
                - blueprint_subtype: policy, guideline, procedure, reference, example
                - confidence: 0.0 to 1.0
                - summary: Brief summary of content
                - key_concepts: List of key concepts extracted
                - reasoning: Why this classification was chosen
        """
        logger.info(
            "Classifying blueprint document",
            content_length=len(content),
            has_filename=filename is not None,
        )

        # Build classification prompt
        prompt = self._build_classification_prompt(content, filename)

        try:
            # Call Claude for classification
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.0,  # Deterministic for classification
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text response
            response_text = response.content[0].text if response.content else ""

            # Parse structured response
            result = self._parse_classification_response(response_text)

            logger.info(
                "Blueprint classified",
                subtype=result.get("blueprint_subtype"),
                confidence=result.get("confidence"),
            )

            return result

        except Exception as e:
            logger.error("Classification failed", error=str(e), exc_info=True)
            # Return fallback classification
            return {
                "blueprint_subtype": "reference",  # Safe default
                "confidence": 0.3,
                "summary": content[:200] + "...",
                "key_concepts": [],
                "reasoning": f"Classification failed: {str(e)}",
            }

    def extract_sections(self, content: str) -> Dict[str, str]:
        """
        Extract logical sections from document

        Args:
            content: Document content

        Returns:
            Dict mapping section names to content
        """
        sections = {}

        # Try to detect markdown-style sections
        section_pattern = r"^#+\s+(.+)$"
        current_section = "preamble"
        current_content = []

        for line in content.split("\n"):
            match = re.match(section_pattern, line, re.MULTILINE)
            if match:
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                # Start new section
                current_section = match.group(1).lower().replace(" ", "_")
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def generate_summary(
        self, content: str, max_length: int = 500
    ) -> str:
        """
        Generate summary of document content

        Args:
            content: Document content
            max_length: Maximum summary length

        Returns:
            Summary string
        """
        # For now, simple extraction (can be enhanced with LLM)
        # Take first few sentences
        sentences = re.split(r"[.!?]+", content)
        summary = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(summary) + len(sentence) < max_length:
                summary += sentence + ". "
            else:
                break

        return summary.strip()

    # ========================================================================
    # Internal Methods
    # ========================================================================

    def _build_classification_prompt(
        self, content: str, filename: Optional[str]
    ) -> str:
        """
        Build prompt for blueprint classification

        Args:
            content: Document content
            filename: Optional filename

        Returns:
            Classification prompt
        """
        prompt = f"""Analyze the following document and classify it as one of these blueprint knowledge types:

**Blueprint Types:**
1. **policy** - Mandatory rules, requirements, or regulations (MUST statements)
2. **guideline** - Best practices, recommendations (SHOULD statements)
3. **procedure** - Step-by-step instructions or processes (HOW-TO content)
4. **reference** - Reference information, definitions, templates
5. **example** - Examples, case studies, sample outputs

**Document to classify:**"""

        if filename:
            prompt += f"\nFilename: {filename}\n"

        prompt += f"\n```\n{content[:4000]}\n```\n"  # Limit to 4K chars

        prompt += """
**Your task:**
1. Classify this document into ONE of the five types above
2. Explain your reasoning
3. Extract 3-5 key concepts or topics
4. Provide a 1-2 sentence summary
5. Rate your confidence (0.0 to 1.0)

**Response format (JSON):**
```json
{
    "blueprint_subtype": "policy|guideline|procedure|reference|example",
    "confidence": 0.85,
    "reasoning": "This is classified as X because...",
    "summary": "Brief summary of the document",
    "key_concepts": ["concept1", "concept2", "concept3"]
}
```

Respond with ONLY the JSON object, no additional text."""

        return prompt

    def _parse_classification_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM classification response

        Args:
            response_text: Raw LLM response

        Returns:
            Parsed classification dict
        """
        import json

        # Try to extract JSON from response
        try:
            # Look for JSON block
            json_match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to parse entire response as JSON
                json_text = response_text

            result = json.loads(json_text)

            # Validate required fields
            required_fields = [
                "blueprint_subtype",
                "confidence",
                "reasoning",
                "summary",
            ]
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing field in classification: {field}")
                    result[field] = "unknown" if field != "confidence" else 0.5

            # Validate blueprint_subtype
            valid_subtypes = ["policy", "guideline", "procedure", "reference", "example"]
            if result["blueprint_subtype"] not in valid_subtypes:
                logger.warning(
                    f"Invalid blueprint_subtype: {result['blueprint_subtype']}"
                )
                result["blueprint_subtype"] = "reference"  # Safe default

            return result

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse classification JSON",
                error=str(e),
                response_text=response_text[:200],
            )
            # Fallback extraction
            return self._fallback_parse(response_text)

    def _fallback_parse(self, response_text: str) -> Dict[str, Any]:
        """
        Fallback parsing if JSON parse fails

        Args:
            response_text: Raw LLM response

        Returns:
            Best-effort classification dict
        """
        # Try to extract key info using regex
        result = {
            "blueprint_subtype": "reference",
            "confidence": 0.5,
            "reasoning": "Fallback classification",
            "summary": response_text[:200],
            "key_concepts": [],
        }

        # Try to find blueprint_subtype mention
        subtype_pattern = r"blueprint_subtype.*?[\"']?(policy|guideline|procedure|reference|example)[\"']?"
        match = re.search(subtype_pattern, response_text, re.IGNORECASE)
        if match:
            result["blueprint_subtype"] = match.group(1).lower()

        # Try to find confidence
        conf_pattern = r"confidence.*?([0-9.]+)"
        match = re.search(conf_pattern, response_text)
        if match:
            try:
                result["confidence"] = float(match.group(1))
                if result["confidence"] > 1.0:
                    result["confidence"] = result["confidence"] / 100.0
            except ValueError:
                pass

        return result


# ============================================================================
# Module Exports
# ============================================================================

__all__ = ["KnowledgeExtractor"]
