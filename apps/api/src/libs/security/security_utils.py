"""
Utilitários de segurança seguindo o hardening checklist.
Implementa práticas recomendadas de segurança.
"""
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import jwt
import yaml
from functools import wraps
import os
import re

# Configurações de segurança
JWT_ALGORITHM = "HS256"  # Algoritmo fixo para prevenir algorithm confusion
JWT_ALGORITHMS_ALLOWED = ["HS256"]  # Lista explícita de algoritmos permitidos
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {".json", ".yaml", ".yml", ".csv", ".txt", ".xml"}
PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",  # ../
    r"\.\.",   # ..
    r"%2e%2e",  # URL encoded ..
    r"\.%2e",   # Mixed encoding
    r"%252e",   # Double encoding
]

class SecurityError(Exception):
    """Exceção base para erros de segurança."""
    pass

class PathTraversalError(SecurityError):
    """Erro de path traversal detectado."""
    pass

class InvalidTokenError(SecurityError):
    """Token JWT inválido ou inseguro."""
    pass

def validate_jwt_algorithm(token: str, secret: str, algorithm: str = JWT_ALGORITHM) -> Dict[Any, Any]:
    """
    Valida e decodifica JWT com algoritmo fixo.
    Previne algorithm confusion attacks.
    """
    if algorithm not in JWT_ALGORITHMS_ALLOWED:
        raise InvalidTokenError(f"Algorithm {algorithm} not allowed")
    
    try:
        # Decodifica especificando explicitamente o algoritmo esperado
        payload = jwt.decode(
            token,
            secret,
            algorithms=[algorithm],  # Lista explícita de algoritmos
            options={"verify_signature": True}
        )
        return payload
    except jwt.InvalidAlgorithmError:
        raise InvalidTokenError("Invalid algorithm in token")
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")

def create_secure_jwt(payload: Dict[Any, Any], secret: str, expires_in: int = 3600) -> str:
    """
    Cria JWT seguro com algoritmo fixo e expiração.
    """
    payload = payload.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload["iat"] = datetime.now(timezone.utc)
    payload["jti"] = secrets.token_urlsafe(16)  # JWT ID único
    
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)

def validate_path(file_path: str, base_dir: str) -> Path:
    """
    Valida caminho contra path traversal.
    Retorna caminho seguro ou levanta exceção.
    """
    # Verificar padrões suspeitos
    for pattern in PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            raise PathTraversalError(f"Path traversal attempt detected: {file_path}")
    
    # Resolver e validar caminho
    base = Path(base_dir).resolve()
    target = Path(base_dir, file_path).resolve()
    
    # Verificar se o caminho resolvido está dentro do diretório base
    try:
        target.relative_to(base)
    except ValueError:
        raise PathTraversalError(f"Path outside base directory: {file_path}")
    
    # Verificar symlinks
    if target.is_symlink():
        real_path = target.readlink()
        if not real_path.is_relative_to(base):
            raise PathTraversalError(f"Symlink points outside base directory: {file_path}")
    
    return target

def safe_yaml_load(content: str) -> Any:
    """
    Carrega YAML de forma segura, prevenindo deserialização perigosa.
    """
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise SecurityError(f"Failed to parse YAML safely: {str(e)}")

def safe_yaml_dump(data: Any) -> str:
    """
    Serializa dados para YAML de forma segura.
    """
    try:
        return yaml.safe_dump(data, default_flow_style=False)
    except yaml.YAMLError as e:
        raise SecurityError(f"Failed to serialize to YAML: {str(e)}")

def get_secure_headers() -> Dict[str, str]:
    """
    Retorna headers de segurança recomendados.
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }

def monotonic_timer():
    """
    Retorna tempo monotônico para métricas.
    Não afetado por ajustes de relógio do sistema.
    """
    return time.monotonic()

def utc_now() -> datetime:
    """
    Retorna datetime atual em UTC com timezone.
    """
    return datetime.now(timezone.utc)

def format_datetime_iso(dt: datetime) -> str:
    """
    Formata datetime para ISO 8601 com timezone.
    """
    if dt.tzinfo is None:
        # Adiciona UTC se não tiver timezone
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def generate_secure_id() -> str:
    """
    Gera ID seguro e único (UUID completo).
    """
    import uuid
    return str(uuid.uuid4())  # UUID completo, sem truncar

def constant_time_compare(a: str, b: str) -> bool:
    """
    Comparação de strings em tempo constante.
    Previne timing attacks.
    """
    return hmac.compare_digest(a.encode(), b.encode())

def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    """
    Hash de senha usando algoritmo seguro (SHA256 + salt).
    Retorna (hash, salt) em base64.
    """
    import base64
    
    if salt is None:
        salt = secrets.token_bytes(32)
    
    # Usar PBKDF2 para key derivation
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    return (
        base64.b64encode(key).decode('ascii'),
        base64.b64encode(salt).decode('ascii')
    )

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """
    Verifica senha contra hash de forma segura.
    """
    import base64
    
    salt_bytes = base64.b64decode(salt.encode('ascii'))
    new_hash, _ = hash_password(password, salt_bytes)
    
    return constant_time_compare(new_hash, password_hash)

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo removendo caracteres perigosos.
    """
    # Remove path separators e caracteres especiais
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    
    # Limita tamanho
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext

def validate_file_upload(file_path: str, content_length: int) -> None:
    """
    Valida upload de arquivo.
    """
    # Verificar tamanho
    if content_length > MAX_FILE_SIZE:
        raise SecurityError(f"File too large: {content_length} bytes")
    
    # Verificar extensão
    ext = Path(file_path).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise SecurityError(f"File type not allowed: {ext}")

def rate_limit_key(identifier: str) -> str:
    """
    Gera chave para rate limiting.
    """
    return f"rate_limit:{identifier}:{int(time.time() // 60)}"  # Janela de 1 minuto

class RateLimiter:
    """
    Rate limiter com janela deslizante.
    """
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Verifica se requisição é permitida.
        """
        now = time.monotonic()
        window_start = now - self.window_seconds
        
        # Limpar requisições antigas
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Verificar limite
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Registrar nova requisição
        self.requests[identifier].append(now)
        return True
    
    def cleanup(self) -> None:
        """
        Limpa dados antigos (garbage collection).
        """
        now = time.monotonic()
        window_start = now - self.window_seconds
        
        # Remover identifiers sem requisições recentes
        self.requests = {
            ident: times for ident, times in self.requests.items()
            if any(t > window_start for t in times)
        }

def secure_random_string(length: int = 32) -> str:
    """
    Gera string aleatória criptograficamente segura.
    """
    return secrets.token_urlsafe(length)

def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mascara dados sensíveis mostrando apenas alguns caracteres.
    """
    if len(data) <= visible_chars * 2:
        return "*" * len(data)
    
    return data[:visible_chars] + "*" * (len(data) - visible_chars * 2) + data[-visible_chars:]

def validate_cors_origin(origin: str, allowed_origins: List[str]) -> bool:
    """
    Valida origem CORS de forma segura.
    """
    # Não usar wildcard em produção
    if "*" in allowed_origins and os.getenv("ENV") == "production":
        raise SecurityError("Wildcard CORS not allowed in production")
    
    # Validação exata
    return origin in allowed_origins

def secure_json_parse(json_str: str, max_size: int = 1024 * 1024) -> Any:
    """
    Parse seguro de JSON com limite de tamanho.
    """
    import json
    
    if len(json_str) > max_size:
        raise SecurityError(f"JSON too large: {len(json_str)} bytes")
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise SecurityError(f"Invalid JSON: {str(e)}")