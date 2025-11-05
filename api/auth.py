from fastapi import APIRouter, HTTPException
from models import Token, UserLogin, TokenRefresh
from auth_utils import (
    verify_password_simple,
    create_access_token, 
    create_refresh_token, 
    decode_token,
    TEST_USER
)
from jose import JWTError

router = APIRouter(
    prefix="/v1/auth",
    tags=["Autenticação"],
)


# Obtém o token
@router.post("/login", response_model=Token, summary="Obtém Access e Refresh Token")
async def login_for_access_token(user_data: UserLogin):
    """
    Autentica o usuário e retorna um Access Token (curta duração) e um Refresh Token (longa duração).
    """
    user = TEST_USER.get(user_data.username)
    
    # Verifica a senha
    if not user or not verify_password_simple(user_data.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Payload para o token
    token_data = {"username": user["username"]}
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return Token(
        access_token=access_token, 
        refresh_token=refresh_token
    )

# Renova o token
@router.post("/refresh", response_model=Token, summary="Renova o Access Token usando o Refresh Token")
async def refresh_access_token(token_refresh: TokenRefresh):
    """
    Usa o Refresh Token para obter um novo Access Token e um novo Refresh Token.
    """
    try:
        payload = decode_token(token_refresh.refresh_token)
        # O token DEVE ser do tipo "refresh"
        if payload.get("sub") != "refresh":
             raise HTTPException(status_code=401, detail="Token inválido. É necessário um Refresh Token.")
        
        username = payload.get("username")
        
        if username is None:
             raise HTTPException(status_code=401, detail="Token inválido ou sem usuário associado.")

        # Gera novos tokens
        token_data = {"username": username}
        new_access_token = create_access_token(data=token_data)
        new_refresh_token = create_refresh_token(data=token_data) # Opcional: renovar o refresh token também
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Refresh Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )