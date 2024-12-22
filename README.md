# ClipsFlix

Uma plataforma para compartilhamento de clipes de jogos, construída com Flask e Cloudinary.

## Funcionalidades

- Upload de vídeos com armazenamento na nuvem
- Sistema de autenticação de usuários
- Interface moderna e responsiva
- Otimização automática de vídeos
- Visualização de clipes em alta qualidade

## Tecnologias Utilizadas

- Flask
- SQLAlchemy
- Flask-Login
- Cloudinary
- Bootstrap 5
- HTML5/CSS3
- JavaScript

## Como Configurar

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/clipsflix.git
cd clipsflix
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com:
```
SECRET_KEY=sua_chave_secreta
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret
```

4. Inicie o servidor:
```bash
python app.py
```

5. Acesse http://localhost:5000

## Contribuindo

Sinta-se à vontade para contribuir com o projeto! Abra uma issue ou envie um pull request.
