# ADR-002: DSL v1 - Primitivas Congeladas para Sprint Atual

## Status
Aceito

## Contexto
Precisamos definir e congelar o conjunto mínimo de primitivas DSL para completar o MVP na sprint atual. Após análise do mercado e requisitos dos marketplaces principais (Amazon, MercadoLibre, Shopify), identificamos as primitivas essenciais.

## Decisão
Congelamos as seguintes primitivas para a DSL v1:

### Checks (Validações)
1. **required** - Campo obrigatório
   ```yaml
   check:
     type: required
     field: sku
   ```

2. **numeric_min** - Valor numérico mínimo
   ```yaml
   check:
     type: numeric_min
     field: price
     min: 0.01
   ```

3. **numeric_max** - Valor numérico máximo
   ```yaml
   check:
     type: numeric_max
     field: quantity
     max: 10000
   ```

4. **in_set** - Valor em conjunto permitido
   ```yaml
   check:
     type: in_set
     field: category
     values: [electronics, books, clothing]
     # ou via mapping:
     mapping: valid_categories
   ```

5. **regex** - Validação por expressão regular
   ```yaml
   check:
     type: regex
     field: ean
     pattern: "^[0-9]{13}$"
   ```

6. **length_min** - Comprimento mínimo de string
   ```yaml
   check:
     type: length_min
     field: description
     min: 10
   ```

7. **length_max** - Comprimento máximo de string
   ```yaml
   check:
     type: length_max
     field: title
     max: 200
   ```

### Fixes (Correções)
1. **set_default** - Define valor padrão
   ```yaml
   fix:
     type: set_default
     field: status
     value: active
   ```

2. **map_value** - Mapeia valores via dicionário
   ```yaml
   fix:
     type: map_value
     field: brand
     mapping: brand_corrections
   ```

3. **truncate** - Trunca string no limite
   ```yaml
   fix:
     type: truncate
     field: title
     max: 200
   ```

4. **pad** - Adiciona padding em string/número
   ```yaml
   fix:
     type: pad
     field: sku
     length: 10
     char: "0"
     side: left  # left|right
   ```

5. **normalize** - Normalização de texto
   ```yaml
   fix:
     type: normalize
     field: brand
     operations: [trim, lowercase, capitalize]
   ```

### Condicionais
1. **when** - Execução condicional
   ```yaml
   when: "marketplace == amazon"
   ```

2. **skip_if** - Pular se condição verdadeira
   ```yaml
   skip_if: "category == digital"
   ```

## Consequências

### Positivas
- Conjunto mínimo mas completo para 80% dos casos
- Todas primitivas são idempotentes
- Fácil de implementar e testar
- Cobre requisitos dos 3 marketplaces principais

### Negativas
- Não suporta transformações complexas (será v2)
- Sem suporte a validações cross-field (será v2)
- Sem agregações ou cálculos (será v2)

### Futuro (v2 - Não nesta sprint)
- **check_cross**: Validação entre campos
- **aggregate**: Operações de agregação
- **calculate**: Cálculos derivados
- **external_api**: Validação via API externa
- **ml_predict**: Predições via modelo ML

## Notas de Implementação
1. Todas as primitivas devem ser idempotentes
2. Fixes só executam se check falhar
3. Logging estruturado obrigatório
4. Suporte a templates básicos: `{{now}}`, `{{uuid}}`
5. Mappings carregados de `mappings.yml` separado

## Referências
- [Documentação Amazon SP-API](https://developer-docs.amazon.com/sp-api/)
- [MercadoLibre API Docs](https://developers.mercadolibre.com.ar/)
- [Shopify Admin API](https://shopify.dev/api/admin)

## Data
2024-08-14

## Autores
- ValidaHub Team