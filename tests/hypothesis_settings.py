"""
Hypothesis settings for property-based testing.
Configurações otimizadas para evitar flaky tests e garantir reprodutibilidade.
"""
from hypothesis import settings, Verbosity
from hypothesis.database import DirectoryBasedExampleDatabase
import os

# Configuração base para testes rápidos e determinísticos
settings.register_profile(
    "default",
    max_examples=100,  # Limitar exemplos para evitar testes lentos
    deadline=5000,  # 5 segundos de deadline
    database=DirectoryBasedExampleDatabase(".hypothesis/examples"),
    derandomize=True,  # Tornar testes determinísticos
    print_blob=True,  # Imprimir exemplo que falhou
)

# Configuração para CI - mais rigorosa
settings.register_profile(
    "ci",
    max_examples=200,  # Mais exemplos em CI
    deadline=10000,  # 10 segundos de deadline
    database=DirectoryBasedExampleDatabase(".hypothesis/examples"),
    derandomize=True,
    print_blob=True,
    verbosity=Verbosity.verbose,  # Mais detalhes em CI
    suppress_health_check=[],  # Não suprimir health checks
)

# Configuração para desenvolvimento - mais rápida
settings.register_profile(
    "dev",
    max_examples=50,  # Menos exemplos para feedback rápido
    deadline=2000,  # 2 segundos de deadline
    database=DirectoryBasedExampleDatabase(".hypothesis/examples"),
    derandomize=False,  # Permitir aleatoriedade em dev
    print_blob=True,
)

# Configuração para debugging
settings.register_profile(
    "debug",
    max_examples=10,  # Poucos exemplos
    deadline=None,  # Sem deadline
    database=None,  # Sem cache
    verbosity=Verbosity.verbose,  # Máximo de detalhes
    print_blob=True,
)

# Selecionar profile baseado no ambiente
profile = os.getenv("HYPOTHESIS_PROFILE", "default")
if os.getenv("CI"):
    profile = "ci"
    
settings.load_profile(profile)