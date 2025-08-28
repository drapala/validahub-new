import logging
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# Configuração básica do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("rule_engine")


@dataclass
class RuleResult:
    rule_id: str
    status: str  # PASS, FAIL, FIXED, ERROR
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuleEngine:
    """Engine interpretativa para regras YAML"""
    
    def __init__(self):
        self.rules = []
        self.mappings = {}
        
    def load_ruleset(self, rules_path: str, mappings_path: Optional[str] = None):
        """Carrega regras e mappings de arquivos YAML"""
        logger.debug(f"Loading ruleset from {rules_path}")
        
        # Carregar regras e mappings do mesmo arquivo
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules_data = yaml.safe_load(f)
            self.rules = rules_data.get('rules', [])
            # Carregar mappings do mesmo arquivo se existir
            self.mappings = rules_data.get('mappings', {})
        
        # Carregar mappings adicionais se fornecido
        if mappings_path:
            logger.debug(f"Loading additional mappings from {mappings_path}")
            with open(mappings_path, 'r', encoding='utf-8') as f:
                mappings_data = yaml.safe_load(f)
                # Merge com mappings existentes
                self.mappings.update(mappings_data.get('mappings', {}))
        
        logger.debug(f"Loaded {len(self.rules)} rules and {len(self.mappings)} mappings")
    
    def execute(self, row: Dict[str, Any], auto_fix: bool = False) -> List[RuleResult]:
        """Executa todas as regras sobre um row"""
        logger.debug(f"Executing {len(self.rules)} rules, auto_fix={auto_fix}")
        results = []
        
        for rule in self.rules:
            try:
                result = self._execute_rule(rule, row, auto_fix)
                results.append(result)
                
                # Log baseado no status
                if result.status == "FAIL":
                    logger.warning(f"Rule {result.rule_id}: {result.message}")
                elif result.status == "FIXED":
                    logger.info(f"Rule {result.rule_id}: {result.message}")
                    
            except Exception as e:
                logger.error(f"Error executing rule {rule.get('id', 'unknown')}: {e}")
                results.append(RuleResult(
                    rule_id=rule.get('id', 'unknown'),
                    status="ERROR",
                    message=str(e)
                ))
        
        return results
    
    def _execute_rule(self, rule: Dict[str, Any], row: Dict[str, Any], auto_fix: bool) -> RuleResult:
        """Executa uma regra individual"""
        rule_id = rule['id']
        logger.debug(f"Evaluating rule {rule_id}")
        
        # Avaliar condição 'when' se existir
        if 'when' in rule:
            if not self._eval_when(rule['when'], row):
                return RuleResult(rule_id=rule_id, status="SKIP", message="Condition not met")
        
        # Executar check
        check = rule.get('check', {})
        check_type = check.get('type')
        passed = False
        
        if check_type == 'required':
            field = check['field']
            passed = field in row and row[field] not in [None, "", []]
            
        elif check_type == 'numeric_min':
            field = check['field']
            # Support both 'value' and 'min' for backward compatibility
            min_val = check.get('value', check.get('min'))
            if min_val is None:
                logger.error(f"Rule {rule_id}: 'numeric_min' check missing 'value' or 'min' field.")
                passed = False
            elif field in row and row[field] is not None:
                try:
                    passed = float(row[field]) >= min_val
                except (ValueError, TypeError):
                    passed = False
            else:
                passed = False
                
        elif check_type == 'in_set':
            field = check['field']
            valid_set = check.get('values', [])
            # Pode referenciar mappings
            if 'mapping' in check:
                valid_set = self.mappings.get(check['mapping'], [])
            passed = row.get(field) in valid_set
        
        # Se passou, retornar sucesso
        if passed:
            return RuleResult(
                rule_id=rule_id,
                status="PASS",
                message=f"{rule.get('name', rule_id)}: OK"
            )
        
        # Se falhou e auto_fix está habilitado, tentar corrigir
        if auto_fix and 'fix' in rule:
            fix = rule['fix']
            fix_type = fix.get('type')
            
            if fix_type == 'set_default':
                field = fix['field']
                value = fix['value']
                row[field] = value
                return RuleResult(
                    rule_id=rule_id,
                    status="FIXED",
                    message=f"{rule.get('name', rule_id)}: Fixed - set {field}={value}",
                    metadata={
                        'field': field,
                        'fixed_value': value,
                        'fix_type': 'set_default',
                        'severity': rule.get('meta', {}).get('severity', 'INFO')
                    }
                )
                
            elif fix_type == 'map_value':
                field = fix['field']
                mapping_name = fix.get('mapping')
                default_value = fix.get('default')
                
                if mapping_name and mapping_name in self.mappings:
                    mapping_dict = self.mappings[mapping_name]
                    current_val = row.get(field)
                    
                    # Try to map the value
                    if current_val in mapping_dict:
                        new_val = mapping_dict[current_val]
                    elif default_value is not None:
                        # Use default if value not in mapping
                        new_val = default_value
                    else:
                        # No mapping found and no default
                        new_val = None
                    
                    if new_val is not None:
                        row[field] = new_val
                        return RuleResult(
                            rule_id=rule_id,
                            status="FIXED",
                            message=f"{rule.get('name', rule_id)}: Fixed - set {field}={new_val}",
                            metadata={
                                'field': field,
                                'fixed_value': new_val,
                                'original_value': current_val,
                                'fix_type': 'map_value',
                                'severity': rule.get('meta', {}).get('severity', 'INFO')
                            }
                        )
        
        # Falhou sem correção
        field = check.get('field', '')
        return RuleResult(
            rule_id=rule_id,
            status="FAIL",
            message=f"{rule.get('name', rule_id)}: Failed",
            metadata={
                'field': field,
                'value': row.get(field) if field else None,
                'severity': rule.get('meta', {}).get('severity', 'ERROR'),
                'expected': rule.get('meta', {}).get('expected')
            }
        )
    
    def _eval_when(self, condition: str, row: Dict[str, Any]) -> bool:
        """Avalia condição 'when' de forma segura"""
        try:
            # Se a condição é apenas um nome de campo, verifica se existe e não é vazio
            if '==' not in condition and '!=' not in condition:
                field = condition.strip()
                value = row.get(field)
                return value is not None and value != "" and value != []
            
            # Suporta field == value
            if '==' in condition:
                field, value = condition.split('==')
                field = field.strip()
                value = value.strip().strip('"').strip("'")
                return str(row.get(field)) == value
                
            # Suporta field != value
            if '!=' in condition:
                field, value = condition.split('!=')
                field = field.strip()
                value = value.strip().strip('"').strip("'")
                return str(row.get(field)) != value
                
            return True
        except:
            return True


def load_ruleset(rules_path: str, mappings_path: Optional[str] = None) -> RuleEngine:
    """Helper para carregar e retornar engine configurada"""
    engine = RuleEngine()
    engine.load_ruleset(rules_path, mappings_path)
    return engine

