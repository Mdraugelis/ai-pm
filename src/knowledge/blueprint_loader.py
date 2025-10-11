"""
Blueprint Loader
Geisinger AI Product Manager Agent - Layer 7: Knowledge Management

Load and manage blueprints as runtime knowledge.

IMPORTANT: Blueprints are NOT workflows to execute.
Blueprints are KNOWLEDGE for the agent to consult.

The orchestrator uses blueprints to inform planning, but doesn't
follow them as rigid steps.

Architecture:
- Loads YAML blueprints from docs/blueprints/
- Caches loaded blueprints for performance
- Provides knowledge (guidance, policies, examples)
- Does NOT provide executable workflows
"""

import yaml
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Blueprint Loader
# ============================================================================


class BlueprintLoader:
    """
    Load and manage blueprints as runtime knowledge

    Blueprints provide:
    - Policies: Rules to follow (MUST/SHOULD/MAY)
    - Guidelines: Best practices
    - Examples: Reference implementations
    - Success criteria: What good looks like

    Blueprints do NOT provide:
    - Hardcoded workflows to execute
    - Mandatory step sequences
    - Rigid processes

    Example:
        >>> loader = BlueprintLoader()
        >>> meta = loader.load_meta_blueprint()
        >>> discovery = loader.load_workflow_as_knowledge("discovery")
    """

    def __init__(self, blueprints_dir: str = "docs/blueprints", document_store=None):
        """
        Initialize blueprint loader

        Args:
            blueprints_dir: Directory containing blueprint YAML files
            document_store: Optional DocumentStore instance for loading user-uploaded blueprints
        """
        self.blueprints_dir = Path(blueprints_dir)
        self.document_store = document_store
        self._cache: Dict[str, Any] = {}
        self._user_blueprint_cache: Dict[str, List[Dict[str, Any]]] = {}

        logger.info(
            "BlueprintLoader initialized",
            blueprints_dir=str(self.blueprints_dir),
            has_document_store=document_store is not None,
        )

    def load_meta_blueprint(self) -> Dict[str, Any]:
        """
        Load meta-blueprint (universal policies)

        Returns:
            Meta-blueprint with universal policies and governance rules
        """
        logger.info("Loading meta-blueprint")
        return self._load_yaml("meta-blueprint.yaml")

    def load_domain_blueprint(self, domain: str) -> Dict[str, Any]:
        """
        Load domain-specific blueprint

        Args:
            domain: Domain name (e.g., "product_management")

        Returns:
            Domain blueprint with domain-specific policies and guidelines
        """
        logger.info("Loading domain blueprint", domain=domain)

        if domain == "product_management":
            return self._load_yaml("product-mgmt-blueprint.yaml")
        else:
            logger.warning(f"Unknown domain: {domain}, returning empty blueprint")
            return {}

    def load_workflow_as_knowledge(self, workflow_name: str) -> Dict[str, Any]:
        """
        Load workflow as KNOWLEDGE, not PROCESS

        This returns guidance, not steps to execute.
        The orchestrator uses this to inform planning, but doesn't
        blindly follow the steps.

        Args:
            workflow_name: Workflow name (e.g., "discovery", "risk-assessment")

        Returns:
            Dict with:
            - guidance: Suggested steps (not mandatory sequence)
            - success_criteria: What good output looks like
            - examples: Reference examples
        """
        logger.info("Loading workflow as knowledge", workflow=workflow_name)

        yaml_data = self._load_yaml(f"{workflow_name}-workflow.yaml")

        if not yaml_data:
            logger.warning(f"Workflow not found: {workflow_name}")
            return {}

        # Extract knowledge (not process!)
        knowledge = {
            "guidance": yaml_data.get("steps", []),
            "success_criteria": yaml_data.get("workflow_success_metrics", {}),
            "examples": yaml_data.get("example_execution", {}),
            "agent_instructions": yaml_data.get("agent_instructions", {}),
        }

        logger.info(
            "Workflow knowledge loaded",
            workflow=workflow_name,
            steps_guidance=len(knowledge.get("guidance", [])),
        )

        return knowledge

    def load_form_template(self, template_name: str) -> Dict[str, Any]:
        """
        Load document template

        Args:
            template_name: Template name (e.g., "ai-discovery-form")

        Returns:
            Template structure and field definitions
        """
        logger.info("Loading form template", template=template_name)

        yaml_data = self._load_yaml(f"{template_name}.yaml")

        if not yaml_data:
            logger.warning(f"Template not found: {template_name}")
            return {}

        return yaml_data

    def load_all_for_mode(self, mode: str) -> Dict[str, Any]:
        """
        Load all blueprints relevant for a specific mode

        Args:
            mode: Operating mode (e.g., "ai_discovery", "risk_assessment")

        Returns:
            Dict with all relevant blueprints
        """
        logger.info("Loading blueprints for mode", mode=mode)

        blueprints = {
            "meta": self.load_meta_blueprint(),
            "domain": self.load_domain_blueprint("product_management"),
        }

        # Mode-specific blueprints
        if mode == "ai_discovery":
            blueprints["workflow"] = self.load_workflow_as_knowledge("discovery")
            blueprints["form_template"] = self.load_form_template(
                "ai-discovery-form"
            )

        elif mode == "risk_assessment":
            # Add risk-specific blueprints when available
            pass

        elif mode == "poc_planning":
            # Add POC-specific blueprints when available
            pass

        logger.info(
            "Blueprints loaded for mode",
            mode=mode,
            blueprints_loaded=list(blueprints.keys()),
        )

        return blueprints

    def get_policies(
        self, blueprint_type: str = "meta"
    ) -> List[Dict[str, Any]]:
        """
        Extract policies from blueprint

        Args:
            blueprint_type: Type of blueprint ("meta" or "domain")

        Returns:
            List of policies
        """
        if blueprint_type == "meta":
            blueprint = self.load_meta_blueprint()
        else:
            blueprint = self.load_domain_blueprint("product_management")

        return blueprint.get("policies", [])

    def get_guidelines(
        self, blueprint_type: str = "domain"
    ) -> List[Dict[str, Any]]:
        """
        Extract guidelines from blueprint

        Args:
            blueprint_type: Type of blueprint

        Returns:
            List of guidelines
        """
        if blueprint_type == "meta":
            blueprint = self.load_meta_blueprint()
        else:
            blueprint = self.load_domain_blueprint("product_management")

        return blueprint.get("guidelines", [])

    def load_user_blueprints(self, project_id: str = "default") -> List[Dict[str, Any]]:
        """
        Load user-uploaded blueprints from DocumentStore

        Args:
            project_id: Project ID to load blueprints for

        Returns:
            List of user-uploaded blueprint documents
        """
        # Check if DocumentStore is available
        if self.document_store is None:
            logger.debug("DocumentStore not available, skipping user blueprints")
            return []

        # Check cache
        cache_key = f"user_blueprints_{project_id}"
        if cache_key in self._user_blueprint_cache:
            logger.debug("User blueprints loaded from cache", project_id=project_id)
            return self._user_blueprint_cache[cache_key]

        try:
            # Query DocumentStore for blueprint_knowledge documents
            blueprints = self.document_store.get_blueprints(
                blueprint_subtype=None,  # Get all subtypes
                project_id=project_id
            )

            logger.info(
                "User blueprints loaded from database",
                project_id=project_id,
                count=len(blueprints)
            )

            # Cache the results
            self._user_blueprint_cache[cache_key] = blueprints

            return blueprints

        except Exception as e:
            logger.error(
                "Failed to load user blueprints from database",
                project_id=project_id,
                error=str(e),
                exc_info=True
            )
            return []

    def get_user_blueprints_by_subtype(
        self, blueprint_subtype: str, project_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """
        Get user-uploaded blueprints filtered by subtype

        Args:
            blueprint_subtype: Subtype filter (policy, guideline, procedure, reference, example)
            project_id: Project ID

        Returns:
            List of matching blueprint documents
        """
        if self.document_store is None:
            return []

        try:
            blueprints = self.document_store.get_blueprints(
                blueprint_subtype=blueprint_subtype,
                project_id=project_id
            )

            logger.debug(
                "User blueprints filtered by subtype",
                subtype=blueprint_subtype,
                count=len(blueprints)
            )

            return blueprints

        except Exception as e:
            logger.error(
                "Failed to load user blueprints by subtype",
                subtype=blueprint_subtype,
                error=str(e),
                exc_info=True
            )
            return []

    def get_all_policies(self, project_id: str = "default") -> List[Dict[str, Any]]:
        """
        Get all policies: YAML blueprints + user-uploaded policy documents

        User-uploaded policies take precedence over YAML policies.

        Args:
            project_id: Project ID

        Returns:
            Combined list of policies (user + YAML)
        """
        # Load YAML policies
        yaml_policies = []
        meta_blueprint = self.load_meta_blueprint()
        domain_blueprint = self.load_domain_blueprint("product_management")

        yaml_policies.extend(meta_blueprint.get("policies", []))
        yaml_policies.extend(domain_blueprint.get("policies", []))

        # Load user-uploaded policies
        user_policies = self.get_user_blueprints_by_subtype("policy", project_id)

        # Convert user policies to policy format
        user_policy_dicts = []
        for doc in user_policies:
            metadata = doc.get("metadata", {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}

            user_policy_dicts.append({
                "id": f"USER-POLICY-{doc['id'][:8]}",
                "rule": metadata.get("summary", doc.get("filename", "User policy")),
                "enforcement": "MUST",  # User policies default to MUST
                "source": "user_upload",
                "document_id": doc["id"],
                "filename": doc.get("filename", "Unknown"),
                "key_concepts": metadata.get("key_concepts", []),
                "confidence": metadata.get("classification_confidence", 1.0)
            })

        # User policies come first (higher priority)
        combined = user_policy_dicts + yaml_policies

        logger.info(
            "Combined policies loaded",
            user_policies=len(user_policy_dicts),
            yaml_policies=len(yaml_policies),
            total=len(combined)
        )

        return combined

    def get_all_guidelines(self, project_id: str = "default") -> List[Dict[str, Any]]:
        """
        Get all guidelines: YAML blueprints + user-uploaded guideline documents

        Args:
            project_id: Project ID

        Returns:
            Combined list of guidelines (user + YAML)
        """
        # Load YAML guidelines
        yaml_guidelines = []
        meta_blueprint = self.load_meta_blueprint()
        domain_blueprint = self.load_domain_blueprint("product_management")

        yaml_guidelines.extend(meta_blueprint.get("guidelines", []))
        yaml_guidelines.extend(domain_blueprint.get("guidelines", []))

        # Load user-uploaded guidelines
        user_guidelines = self.get_user_blueprints_by_subtype("guideline", project_id)

        # Convert user guidelines to guideline format
        user_guideline_dicts = []
        for doc in user_guidelines:
            metadata = doc.get("metadata", {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}

            user_guideline_dicts.append({
                "id": f"USER-GUIDE-{doc['id'][:8]}",
                "recommendation": metadata.get("summary", doc.get("filename", "User guideline")),
                "enforcement": "SHOULD",
                "source": "user_upload",
                "document_id": doc["id"],
                "filename": doc.get("filename", "Unknown"),
                "key_concepts": metadata.get("key_concepts", [])
            })

        # User guidelines come first
        combined = user_guideline_dicts + yaml_guidelines

        logger.info(
            "Combined guidelines loaded",
            user_guidelines=len(user_guideline_dicts),
            yaml_guidelines=len(yaml_guidelines),
            total=len(combined)
        )

        return combined

    def clear_cache(self) -> None:
        """Clear the blueprint cache"""
        logger.info(
            "Clearing blueprint cache",
            cached_blueprints=len(self._cache),
            cached_user_blueprints=len(self._user_blueprint_cache)
        )
        self._cache = {}
        self._user_blueprint_cache = {}

    # ========================================================================
    # Internal Methods
    # ========================================================================

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML file with caching

        Args:
            filename: Blueprint filename

        Returns:
            Blueprint data or empty dict if not found
        """
        # Check cache
        if filename in self._cache:
            logger.debug(f"Blueprint loaded from cache: {filename}")
            return self._cache[filename]

        # Load from file
        path = self.blueprints_dir / filename

        if not path.exists():
            logger.warning(f"Blueprint file not found: {path}")
            return {}

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

                # Cache it
                self._cache[filename] = data

                logger.debug(f"Blueprint loaded and cached: {filename}")
                return data

        except yaml.YAMLError as e:
            logger.error(
                f"Failed to parse YAML blueprint: {filename}",
                error=str(e),
                exc_info=True,
            )
            return {}

        except Exception as e:
            logger.error(
                f"Failed to load blueprint: {filename}",
                error=str(e),
                exc_info=True,
            )
            return {}

    def _validate_blueprint(self, blueprint: Dict[str, Any]) -> bool:
        """
        Validate blueprint structure

        Args:
            blueprint: Blueprint data to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic validation (can be expanded)
        required_fields = ["name", "version", "type"]

        for field in required_fields:
            if field not in blueprint:
                logger.warning(
                    f"Blueprint missing required field: {field}",
                    blueprint=blueprint.get("name", "unknown"),
                )
                return False

        return True


# ============================================================================
# Helper Functions
# ============================================================================


def load_blueprint_for_orchestrator(
    blueprint_loader: BlueprintLoader, domain: str
) -> Dict[str, Any]:
    """
    Load blueprints in format expected by orchestrator

    Args:
        blueprint_loader: BlueprintLoader instance
        domain: Domain name

    Returns:
        Dict with meta_blueprint and domain_blueprint
    """
    return {
        "meta_blueprint": blueprint_loader.load_meta_blueprint(),
        "domain_blueprint": blueprint_loader.load_domain_blueprint(domain),
    }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "BlueprintLoader",
    "load_blueprint_for_orchestrator",
]
