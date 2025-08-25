from pathlib import Path
from rule_engine import load_ruleset


def test_load_existing_ruleset():
    ruleset_path = Path("rulesets/mercadolivre.yaml")
    engine = load_ruleset(str(ruleset_path))
    assert engine.rules  # engine has rules loaded


def test_load_default_ruleset():
    ruleset_path = Path("rulesets/default.yaml")
    engine = load_ruleset(str(ruleset_path))
    assert engine.rules  # engine has default rules
