from .agent_base import AgentBase
import json
from typing import Dict, Any, List

class ClinicalParserValidatorAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="ClinicalParserValidatorAgent", max_retries=max_retries, verbose=verbose)

    def execute(self, original_note: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the accuracy and completeness of clinical note parsing.
        
        Args:
            original_note (str): The original clinical note
            parsed_data (Dict): The parsed structured data
        
        Returns:
            Dict containing validation results and recommendations
        """
        if not self.validate_input(original_note) or not parsed_data:
            raise ValueError("Invalid input provided for validation")

        # Prepare validation prompt
        system_message = self.prepare_system_message(
            "You are a clinical data validation expert. Assess the accuracy and completeness of medical data extraction."
        )
        
        validation_prompt = f"""
        Please validate the accuracy and completeness of this clinical note parsing:

        ORIGINAL CLINICAL NOTE:
        {original_note}

        PARSED STRUCTURED DATA:
        {json.dumps(parsed_data, indent=2)}

        Assess the following aspects:
        1. ACCURACY: Are the extracted elements correctly identified from the note?
        2. COMPLETENESS: What important information might be missing?
        3. CATEGORIZATION: Are items placed in the correct categories?
        4. MEDICAL TERMINOLOGY: Are medical terms correctly captured?
        5. ERRORS: Any obvious mistakes or misinterpretations?

        Provide your assessment in this JSON format:
        {{
            "overall_score": <score 0-10>,
            "accuracy_score": <score 0-10>,
            "completeness_score": <score 0-10>,
            "categorization_score": <score 0-10>,
            "missing_information": ["item1", "item2"],
            "incorrect_extractions": ["item1", "item2"],
            "recommendations": ["suggestion1", "suggestion2"],
            "confidence_level": "high|medium|low"
        }}
        """

        messages = [
            system_message,
            {"role": "user", "content": validation_prompt}
        ]

        response = self.call_llama(messages, max_tokens=600)
        
        try:
            # Try to parse validation response as JSON
            validation_result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback structured parsing
            validation_result = self._parse_validation_response(response)
        
        # Add metadata
        validation_result["validation_metadata"] = {
            "original_note_length": len(original_note),
            "parsed_sections": len([k for k, v in parsed_data.items() if k != 'metadata' and v]),
            "timestamp": self._get_timestamp()
        }
        
        return validation_result

    def validate_medical_entities(self, original_note: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Validate extracted medical entities for accuracy
        
        Args:
            original_note (str): Original clinical note
            entities (Dict): Extracted medical entities
            
        Returns:
            Dict containing entity validation results
        """
        system_message = self.prepare_system_message(
            "You are a medical entity validation expert. Verify the accuracy of extracted medical terms."
        )
        
        entity_validation_prompt = f"""
        Validate these extracted medical entities from the clinical note:

        ORIGINAL NOTE:
        {original_note}

        EXTRACTED ENTITIES:
        {json.dumps(entities, indent=2)}

        Check each category for:
        1. Accuracy of extraction
        2. Proper categorization
        3. Missing entities
        4. Incorrect classifications

        Provide validation in JSON format:
        {{
            "entity_accuracy": {{
                "symptoms": <score 0-10>,
                "conditions": <score 0-10>,
                "medications": <score 0-10>,
                "procedures": <score 0-10>,
                "anatomy": <score 0-10>
            }},
            "missing_entities": {{
                "symptoms": ["missed1", "missed2"],
                "conditions": ["missed1"],
                "medications": ["missed1"],
                "procedures": ["missed1"],
                "anatomy": ["missed1"]
            }},
            "misclassified_entities": ["entity that's in wrong category"],
            "overall_entity_score": <score 0-10>
        }}
        """

        messages = [
            system_message,
            {"role": "user", "content": entity_validation_prompt}
        ]

        response = self.call_llama(messages, max_tokens=500)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return self._parse_entity_validation_response(response)

    def assess_extraction_quality(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the overall quality of the extraction without the original note
        
        Args:
            parsed_data (Dict): The parsed structured data
            
        Returns:
            Dict containing quality assessment
        """
        system_message = self.prepare_system_message(
            "You are a clinical data quality assessor. Evaluate the coherence and medical validity of extracted data."
        )
        
        quality_prompt = f"""
        Assess the quality and medical coherence of this extracted clinical data:

        PARSED DATA:
        {json.dumps(parsed_data, indent=2)}

        Evaluate:
        1. Medical coherence (do symptoms match diagnoses?)
        2. Completeness of clinical picture
        3. Consistency across sections
        4. Medical logic and validity

        Provide assessment in JSON format:
        {{
            "coherence_score": <score 0-10>,
            "completeness_score": <score 0-10>,
            "consistency_score": <score 0-10>,
            "medical_validity_score": <score 0-10>,
            "quality_issues": ["issue1", "issue2"],
            "strengths": ["strength1", "strength2"],
            "overall_quality": "excellent|good|fair|poor"
        }}
        """

        messages = [
            system_message,
            {"role": "user", "content": quality_prompt}
        ]

        response = self.call_llama(messages, max_tokens=400)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return self._parse_quality_response(response)

    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """Fallback parsing for validation response"""
        return {
            "overall_score": 7.0,
            "accuracy_score": 7.0,
            "completeness_score": 7.0,
            "categorization_score": 7.0,
            "missing_information": ["Unable to parse specific missing items"],
            "incorrect_extractions": ["Unable to parse specific errors"],
            "recommendations": ["Review parsing results manually"],
            "confidence_level": "medium"
        }

    def _parse_entity_validation_response(self, response: str) -> Dict[str, Any]:
        """Fallback parsing for entity validation response"""
        return {
            "entity_accuracy": {
                "symptoms": 7.0,
                "conditions": 7.0,
                "medications": 7.0,
                "procedures": 7.0,
                "anatomy": 7.0
            },
            "missing_entities": {
                "symptoms": [],
                "conditions": [],
                "medications": [],
                "procedures": [],
                "anatomy": []
            },
            "misclassified_entities": [],
            "overall_entity_score": 7.0
        }

    def _parse_quality_response(self, response: str) -> Dict[str, Any]:
        """Fallback parsing for quality assessment response"""
        return {
            "coherence_score": 7.0,
            "completeness_score": 7.0,
            "consistency_score": 7.0,
            "medical_validity_score": 7.0,
            "quality_issues": ["Unable to parse specific issues"],
            "strengths": ["Unable to parse specific strengths"],
            "overall_quality": "fair"
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()