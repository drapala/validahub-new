from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import hashlib
import json
from datetime import datetime


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class RuleResult:
    rule_id: str
    passed: bool
    message: str
    severity: Severity
    fix_available: bool = False
    fix_applied: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Rule:
    id: str
    name: str
    description: str
    category: str
    severity: Severity
    check: Callable[[Dict[str, Any]], bool]
    fix: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def execute(self, context: Dict[str, Any], auto_fix: bool = False) -> RuleResult:
        try:
            passed = self.check(context)
            result = RuleResult(
                rule_id=self.id,
                passed=passed,
                message=f"{self.name}: {'Passed' if passed else 'Failed'}",
                severity=self.severity,
                fix_available=(self.fix is not None)
            )
            
            if not passed and auto_fix and self.fix:
                try:
                    fixed_context = self.fix(context)
                    if self.check(fixed_context):
                        result.fix_applied = True
                        result.message += " (Fixed)"
                        context.update(fixed_context)
                except Exception as e:
                    result.metadata['fix_error'] = str(e)
                    
            return result
        except Exception as e:
            return RuleResult(
                rule_id=self.id,
                passed=False,
                message=f"Rule execution error: {str(e)}",
                severity=Severity.ERROR,
                fix_available=False
            )


@dataclass
class Report:
    id: str
    timestamp: datetime
    results: List[RuleResult]
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.summary = self._calculate_summary()
    
    def _calculate_summary(self) -> Dict[str, Any]:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        fixed = sum(1 for r in self.results if r.fix_applied)
        
        by_severity = {}
        for sev in Severity:
            count = sum(1 for r in self.results if not r.passed and r.severity == sev)
            if count > 0:
                by_severity[sev.value] = count
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'fixed': fixed,
            'pass_rate': (passed / total * 100) if total > 0 else 100,
            'by_severity': by_severity
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'summary': self.summary,
            'results': [
                {
                    'rule_id': r.rule_id,
                    'passed': r.passed,
                    'message': r.message,
                    'severity': r.severity.value,
                    'fix_available': r.fix_available,
                    'fix_applied': r.fix_applied,
                    'metadata': r.metadata
                }
                for r in self.results
            ]
        }


class RuleEngine:
    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.categories: Dict[str, List[str]] = {}
    
    def register_rule(self, rule: Rule):
        self.rules[rule.id] = rule
        if rule.category not in self.categories:
            self.categories[rule.category] = []
        self.categories[rule.category].append(rule.id)
    
    def run(
        self,
        context: Dict[str, Any],
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        auto_fix: bool = False
    ) -> Report:
        rules_to_run = self._select_rules(categories, tags)
        results = []
        
        for rule_id in rules_to_run:
            rule = self.rules[rule_id]
            result = rule.execute(context, auto_fix)
            results.append(result)
        
        report_id = self._generate_report_id(context)
        return Report(
            id=report_id,
            timestamp=datetime.utcnow(),
            results=results
        )
    
    def _select_rules(
        self,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> List[str]:
        if categories is None and tags is None:
            return list(self.rules.keys())
        
        selected = set()
        
        if categories:
            for cat in categories:
                if cat in self.categories:
                    selected.update(self.categories[cat])
        
        if tags:
            for rule_id, rule in self.rules.items():
                if any(tag in rule.tags for tag in tags):
                    selected.add(rule_id)
        
        return list(selected)
    
    def _generate_report_id(self, context: Dict[str, Any]) -> str:
        content = json.dumps(context, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

