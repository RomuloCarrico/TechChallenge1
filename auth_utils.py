from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
#from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from models import AuthenticatedUser # Importado para a função get_current_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 

# Configurações JWT
SECRET_KEY = "sua_chave_secreta_aqui_em_producao_use_uma_variavel_ambiente"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7 

# Define o esquema de segurança para o FastAPI
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
http_bearer = HTTPBearer(auto_error=False)


TEST_USER = {
    "admin": {
        "username": "admin",
        "password": "senha"
    }
}

# Verificação da senha
def verify_password_simple(plain_password: str, stored_password: str) -> bool:
    """Compara senhas em texto plano. MÁ PRÁTICA EM PRODUÇÃO."""
    return plain_password == stored_password

# Funções de Geração de Token 
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Gera um JWT de acesso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "sub": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Gera um JWT de renovação."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode.update({"exp": expire, "sub": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
# Funções de Decodificação e Dependência
def decode_token(token: str):
    """Decodifica e verifica um token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # Lança exceção se o token for inválido (expirado, assinatura incorreta, etc.)
        raise JWTError(f"Token inválido ou expirado: {e}")

async def get_current_user(
    # Agora espera credenciais HTTP Bearer em vez de string
    security_credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> AuthenticatedUser:
    """Decodifica o token e retorna o objeto AuthenticatedUser."""
    
    # Se security_credentials for None, o token está faltando
    if security_credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação é obrigatório (Bearer <token>)",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = security_credentials.credentials # Obtém a string do token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        username: str = payload.get("username")
        
        # O token DEVE ser do tipo "access"
        if username is None or payload.get("sub") != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    return AuthenticatedUser(username=username)