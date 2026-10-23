# AgroVision

Projeto de inteligência artificial com aplicação FastAPI, chat e componentes de visão computacional. Inclui material de estudo e documentação para implementação.

## Comece por aqui

- [Instalação e execução](QUICKSTART.md)
- [Guia para alunos](GUIA_ALUNOS.md)
- [Exercícios e exemplos](EXERCICIOS_E_EXEMPLOS.md)
- [Perguntas frequentes](FAQ.md)
- [Manual de implementação do chat](MANUAL_CHAT_IMPLEMENTACAO.md)

## Execução local

Requisito documentado: Python 3.10 ou superior.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

No Windows, ative o ambiente com `.venv\\Scripts\\Activate.ps1`.

Abra `http://127.0.0.1:8000`. Consulte o guia rápido para requisitos opcionais de webcam, modelos e dados.

## Estrutura

- `app.py`: aplicação principal
- `services/`: serviços da aplicação
- `templates/`: interface web
- `train_model.py`: entrada para treinamento do modelo
- `requirements.txt`: dependências Python

Esta revisão organiza a documentação existente; não certifica a execução ou a qualidade dos modelos.
