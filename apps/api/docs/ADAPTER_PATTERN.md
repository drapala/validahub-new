# Adapter Pattern - JobService

## Problema Identificado

O `JobServiceAdapter` original tinha muitos `if`s porque estava:
1. **Verificando se métodos existem** (`if hasattr(...)`)
2. **Implementando lógica de negócio** ao invés de apenas adaptar
3. **Misturando responsabilidades** de adaptação e implementação

## Solução: Adapter Simples

### Princípios

1. **Single Responsibility**: O adapter só adapta interfaces
2. **Delegation Pattern**: Toda lógica é delegada ao serviço subjacente
3. **No Business Logic**: Nenhuma lógica de negócio no adapter

### Comparação

#### ❌ Adapter Complexo (Problema)
```python
class JobServiceAdapter(IJobService):
    def get_job(self, job_id: str, user_id: Optional[str] = None):
        # Muitos IFs e lógica de negócio
        if hasattr(self.legacy_service, 'get_job'):
            return self.legacy_service.get_job(job_id, user_id)
        
        job = self.db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return None
        
        if user_id and str(job.user_id) != user_id:
            logger.warning(f"User {user_id} attempted...")
            return None
        
        return JobOut.model_validate(job)
```

#### ✅ Adapter Simples (Solução)
```python
class JobServiceSimpleAdapter(IJobService):
    def get_job(self, job_id: str, user_id: Optional[str] = None):
        # Apenas delega
        return self.service.get_job(job_id, user_id)
```

## Quando Usar Cada Abordagem

### Adapter Simples
- Quando o serviço subjacente já implementa toda a lógica
- Para manter separação clara de responsabilidades
- Facilita testes e manutenção

### Adapter com Lógica
- Durante migração gradual de sistemas legados
- Quando precisa compatibilidade com múltiplas versões
- Como solução temporária durante refatoração

## Problema Atual: JobService

O `JobService` atual tem problemas de design:
1. **Lança HTTPException** (deveria retornar Result/Option)
2. **Acoplado ao FastAPI** (status codes HTTP)
3. **Mistura camadas** (serviço conhece detalhes HTTP)

### Solução Futura

```python
# Serviço retorna Result pattern
class JobService:
    def get_job(self, job_id: str, user_id: str) -> Result[JobOut, JobError]:
        job = self._find_job(job_id, user_id)
        if not job:
            return Err(JobError.NOT_FOUND)
        return Ok(JobOut.from_model(job))

# Controller traduz para HTTP
class JobController:
    def get_job(self, job_id: str, user_id: str):
        result = self.service.get_job(job_id, user_id)
        if result.is_err():
            if result.error == JobError.NOT_FOUND:
                raise HTTPException(404, "Job not found")
        return result.value
```

## Checklist para Adapters

- [ ] Adapter tem apenas uma responsabilidade (adaptar interface)?
- [ ] Toda lógica de negócio está no serviço subjacente?
- [ ] Não há `if`s desnecessários verificando existência de métodos?
- [ ] Adapter é facilmente testável com mock do serviço?
- [ ] Interface está bem definida e documentada?

## Conclusão

O excesso de `if`s no adapter original indica violação do Single Responsibility Principle. A solução é:
1. Manter adapters simples (apenas delegação)
2. Garantir que serviços implementem todos os métodos necessários
3. Usar Result pattern ao invés de exceções para erros de negócio
4. Separar concerns HTTP da lógica de negócio