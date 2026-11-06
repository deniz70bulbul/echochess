# EchoChess

Create an Echo from chess games and play against it.

## Setup

### Backend

```bash
python -m pip install -r requirements.txt
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Stockfish binary should be in the project root as `stockfish-windows-x86-64-avx2.exe` (or update `ENGINE_PATH` in `engine_wrapper.py`).

Registration requires an invite code. Set it with:

```bash
set ECHOCHESS_INVITE_CODE=your-code
```

If unset, the server uses its configured default. The code is validated on the backend only.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173

## Accounts

- Create an account, then log in.
- Passwords are hashed. They are not stored as plain text.
- Each account can access only its own Echo and PGN files.
- Existing bot profiles are kept. Log in with the same username to use them.

## Flow

1. Log in
2. Create Echo (upload PGN files)
3. View Echo profile
4. Play against the Echo
