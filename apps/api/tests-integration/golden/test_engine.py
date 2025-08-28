#!/usr/bin/env python3
import json
from pathlib import Path

from rule_engine import RuleEngine, load_ruleset


def test_basic_rules():
    """Testa as 3 regras básicas com casos PASS, FAIL e FIXED"""
    
    # Carregar engine
    base_path = Path(__file__).parent.parent.parent / 'rulesets' / 'base'
    engine = load_ruleset(
        str(base_path / 'rules.yml'),
        str(base_path / 'mappings.yml')
    )
    
    print("\n=== Teste 1: SKU ausente (deve FAIL) ===")
    row1 = {"price": 10.0, "brand": "Nike"}
    results1 = engine.execute(row1, auto_fix=False)
    for r in results1:
        print(f"  {r.rule_id}: {r.status} - {r.message}")
    assert any(r.rule_id == "sku_required" and r.status == "FAIL" for r in results1)
    
    print("\n=== Teste 2: SKU ausente com auto_fix (deve FIXED) ===")
    row2 = {"price": 10.0, "brand": "Nike"}
    results2 = engine.execute(row2, auto_fix=True)
    for r in results2:
        print(f"  {r.rule_id}: {r.status} - {r.message}")
    assert any(r.rule_id == "sku_required" and r.status == "FIXED" for r in results2)
    assert row2.get("sku") == "SKU-PENDING"
    
    print("\n=== Teste 3: Preço inválido (deve FAIL) ===")
    row3 = {"sku": "ABC123", "price": -5, "brand": "Nike"}
    results3 = engine.execute(row3, auto_fix=False)
    for r in results3:
        print(f"  {r.rule_id}: {r.status} - {r.message}")
    assert any(r.rule_id == "price_min" and r.status == "FAIL" for r in results3)
    
    print("\n=== Teste 4: Preço inválido com auto_fix (deve FIXED) ===")
    row4 = {"sku": "ABC123", "price": -5, "brand": "Nike"}
    results4 = engine.execute(row4, auto_fix=True)
    for r in results4:
        print(f"  {r.rule_id}: {r.status} - {r.message}")
    assert any(r.rule_id == "price_min" and r.status == "FIXED" for r in results4)
    assert row4.get("price") == 0.01
    
    print("\n=== Teste 5: Brand normalização (marketplace=amazon) ===")
    row5 = {"sku": "ABC123", "price": 10, "brand": "nike", "marketplace": "amazon"}
    results5 = engine.execute(row5, auto_fix=True)
    for r in results5:
        print(f"  {r.rule_id}: {r.status} - {r.message}")
    assert any(r.rule_id == "brand_normalize" and r.status == "FIXED" for r in results5)
    assert row5.get("brand") == "Nike"
    
    print("\n=== Teste 6: Tudo válido (deve tudo PASS) ===")
    row6 = {"sku": "ABC123", "price": 10, "brand": "Nike", "marketplace": "amazon"}
    results6 = engine.execute(row6, auto_fix=False)
    for r in results6:
        print(f"  {r.rule_id}: {r.status} - {r.message}")
    assert all(r.status in ["PASS", "SKIP"] for r in results6)
    
    print("\n✅ Todos os testes passaram!")
    return True


def test_golden_snapshot():
    """Teste golden com snapshot simples"""
    base_path = Path(__file__).parent.parent.parent / 'rulesets' / 'base'
    engine = load_ruleset(
        str(base_path / 'rules.yml'),
        str(base_path / 'mappings.yml')
    )
    
    # Caso teste
    test_row = {
        "price": 0.005,  # Abaixo do mínimo
        "brand": "MICROSOFT",  # Precisa normalização
        "marketplace": "amazon"
    }
    
    results = engine.execute(test_row, auto_fix=True)
    
    # Snapshot esperado
    expected_statuses = {
        "sku_required": "FIXED",
        "price_min": "FIXED",
        "brand_normalize": "FIXED"
    }
    
    # Verificar
    for result in results:
        if result.rule_id in expected_statuses:
            assert result.status == expected_statuses[result.rule_id], \
                f"Rule {result.rule_id} expected {expected_statuses[result.rule_id]}, got {result.status}"
    
    # Verificar valores corrigidos
    assert test_row["sku"] == "SKU-PENDING"
    assert test_row["price"] == 0.01
    assert test_row["brand"] == "Microsoft"
    
    print("✅ Golden snapshot test passed!")
    return True


if __name__ == "__main__":
    import logging
    
    # Configurar logging para DEBUG durante testes
    logging.getLogger("rule_engine").setLevel(logging.DEBUG)
    
    success = True
    try:
        test_basic_rules()
        test_golden_snapshot()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        success = False
    
    sys.exit(0 if success else 1)