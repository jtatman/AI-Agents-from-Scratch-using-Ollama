from .agent_base import AgentBase
import json
import re
from typing import Dict, Any, List, Optional

class ClinicalParserTool(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="ClinicalParserTool", max_retries=max_retries, verbose=verbose)

    def execute(self, clinical_note: str, extract_format: str = "json") -> Dict[str, Any]:
        """
        Parse clinical notes and extract structured medical information.
        
        Args:
            clinical_note (str): The clinical note text to parse
            extract_format (str): Output format ('json' or 'structured')
        
        Returns:
            Dict containing structured medical information
        """
        if not self.validate_input(clinical_note):
            raise ValueError("Invalid clinical note provided")
        
        # Prepare extraction prompt
        system_message = self.prepare_system_message()
        
        extraction_prompt = f"""
        Extract the following structured information from this clinical note:

        1. Patient Demographics (age, gender, if mentioned)
        2. Chief Complaint
        3. Present Illness (symptoms, duration, severity)
        4. Past Medical History
        5. Medications (current and past)
        6. Allergies
        7. Vital Signs (if present)
        8. Physical Examination findings
        9. Assessment/Diagnosis
        10. Plan/Treatment

        Clinical Note:
        {clinical_note}

        Please provide the extracted information in a clear, structured JSON format with the following keys:
        - demographics
        - chief_complaint
        - present_illness
        - medical_history
        - medications
        - allergies
        - vital_signs
        - physical_exam
        - assessment
        - plan

        For each section, provide a list of relevant findings or "Not mentioned" if not present.
        """

        messages = [
            system_message,
            {"role": "user", "content": extraction_prompt}
        ]

        # Get structured extraction
        response = self.call_llama(messages, max_tokens=800)
        
        # Parse the response and structure it
        structured_data = self._parse_extraction_response(response)
        
        # Add metadata
        structured_data["metadata"] = {
            "note_length": len(clinical_note),
            "extraction_timestamp": self._get_timestamp(),
            "confidence_score": self._calculate_confidence_score(structured_data)
        }
        
        return structured_data

    def extract_medical_entities(self, clinical_note: str) -> Dict[str, List[str]]:
        """
        Extract specific medical entities (symptoms, conditions, medications, etc.)
        
        Args:
            clinical_note (str): The clinical note text
            
        Returns:
            Dict with categorized medical entities
        """
        system_message = self.prepare_system_message(
            "You are a medical entity extraction specialist. Extract and categorize medical terms precisely."
        )
        
        entity_prompt = f"""
        Extract and categorize the following medical entities from this clinical note:

        1. SYMPTOMS: All symptoms mentioned (e.g., chest pain, shortness of breath, fever)
        2. CONDITIONS: Diagnoses and medical conditions (e.g., hypertension, diabetes, pneumonia)
        3. MEDICATIONS: All drugs and medications (e.g., lisinopril, metformin, aspirin)
        4. PROCEDURES: Medical procedures and tests (e.g., X-ray, ECG, blood test)
        5. ANATOMY: Body parts and anatomical references (e.g., heart, lungs, abdomen)

        Clinical Note:
        {clinical_note}

        Provide the results in this exact JSON format:
        {{
            "symptoms": ["symptom1", "symptom2"],
            "conditions": ["condition1", "condition2"],
            "medications": ["med1", "med2"],
            "procedures": ["procedure1", "procedure2"],
            "anatomy": ["body_part1", "body_part2"]
        }}
        """

        messages = [
            system_message,
            {"role": "user", "content": entity_prompt}
        ]

        response = self.call_llama(messages, max_tokens=600)
        
        try:
            # Try to parse as JSON
            entities = json.loads(response)
            return entities
        except json.JSONDecodeError:
            # Fallback parsing if JSON parsing fails
            return self._fallback_entity_extraction(response)

    def generate_medical_summary(self, clinical_note: str) -> str:
        """
        Generate a concise medical summary of the clinical note
        
        Args:
            clinical_note (str): The clinical note text
            
        Returns:
            String containing the medical summary
        """
        system_message = self.prepare_system_message(
            "You are a medical summarization expert. Create concise, accurate clinical summaries."
        )
        
        summary_prompt = f"""
        Create a concise medical summary of this clinical note. Include:
        - Key presenting symptoms
        - Primary diagnosis/assessment
        - Important findings
        - Treatment plan highlights
        - Follow-up requirements

        Keep the summary to 3-4 sentences maximum while capturing the essential medical information.

        Clinical Note:
        {clinical_note}

        Medical Summary:
        """

        messages = [
            system_message,
            {"role": "user", "content": summary_prompt}
        ]

        summary = self.call_llama(messages, max_tokens=300)
        return summary.strip()

    def _parse_extraction_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response and structure it properly"""
        try:
            # Try to parse as JSON first
            if "{" in response and "}" in response:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback: structured parsing
        return self._structured_text_parsing(response)

    def _structured_text_parsing(self, response: str) -> Dict[str, Any]:
        """Fallback method to parse structured text when JSON parsing fails"""
        structured_data = {
            "demographics": [],
            "chief_complaint": [],
            "present_illness": [],
            "medical_history": [],
            "medications": [],
            "allergies": [],
            "vital_signs": [],
            "physical_exam": [],
            "assessment": [],
            "plan": []
        }
        
        # Simple keyword-based extraction
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            if any(keyword in line.lower() for keyword in ['demographic', 'age', 'gender']):
                current_section = 'demographics'
            elif any(keyword in line.lower() for keyword in ['chief complaint', 'presenting']):
                current_section = 'chief_complaint'
            elif any(keyword in line.lower() for keyword in ['present illness', 'history of present']):
                current_section = 'present_illness'
            elif any(keyword in line.lower() for keyword in ['medical history', 'past medical']):
                current_section = 'medical_history'
            elif any(keyword in line.lower() for keyword in ['medication', 'drug', 'prescription']):
                current_section = 'medications'
            elif 'allergies' in line.lower():
                current_section = 'allergies'
            elif any(keyword in line.lower() for keyword in ['vital signs', 'vitals']):
                current_section = 'vital_signs'
            elif any(keyword in line.lower() for keyword in ['physical exam', 'examination']):
                current_section = 'physical_exam'
            elif any(keyword in line.lower() for keyword in ['assessment', 'diagnosis']):
                current_section = 'assessment'
            elif any(keyword in line.lower() for keyword in ['plan', 'treatment']):
                current_section = 'plan'
            elif current_section and line:
                # Add content to current section
                structured_data[current_section].append(line)
        
        return structured_data

    def _fallback_entity_extraction(self, response: str) -> Dict[str, List[str]]:
        """Fallback entity extraction when JSON parsing fails"""
        entities = {
            "symptoms": [],
            "conditions": [],
            "medications": [],
            "procedures": [],
            "anatomy": []
        }
        
        # Simple regex-based extraction (basic implementation)
        lines = response.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if 'symptom' in line.lower():
                current_category = 'symptoms'
            elif 'condition' in line.lower() or 'diagnosis' in line.lower():
                current_category = 'conditions'
            elif 'medication' in line.lower() or 'drug' in line.lower():
                current_category = 'medications'
            elif 'procedure' in line.lower() or 'test' in line.lower():
                current_category = 'procedures'
            elif 'anatomy' in line.lower() or 'body' in line.lower():
                current_category = 'anatomy'
            elif current_category and line and not line.startswith('-'):
                # Extract items (basic comma-separated parsing)
                items = [item.strip() for item in line.split(',')]
                entities[current_category].extend(items)
        
        return entities

    def _calculate_confidence_score(self, structured_data: Dict[str, Any]) -> float:
        """Calculate a confidence score for the extraction"""
        total_sections = len(structured_data) - 1  # Exclude metadata
        filled_sections = sum(1 for key, value in structured_data.items() 
                            if key != 'metadata' and value and value != ["Not mentioned"])
        
        return round(filled_sections / total_sections, 2) if total_sections > 0 else 0.0

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()

    def validate_input(self, input_data: Any) -> bool:
        """Enhanced input validation for clinical notes"""
        if not super().validate_input(input_data):
            return False
        
        # Check minimum length for meaningful clinical note
        if len(input_data.strip()) < 20:
            return False
            
        return True