import uuid
from datetime import datetime, timezone

import chess

from clone_engine_v3 import get_clone_move


_sessions = {}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _board_to_state(board, session):
    return {
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "is_game_over": board.is_game_over(),
        "result": _game_result(board),
        "move_history": session["move_history"],
        "captured": session["captured"],
        "status": session["status"],
    }


def _game_result(board):
    if not board.is_game_over():
        return None

    if board.is_checkmate():
        winner = "black" if board.turn == chess.WHITE else "white"
        return f"{winner} wins by checkmate"

    if board.is_stalemate():
        return "draw by stalemate"

    if board.is_insufficient_material():
        return "draw by insufficient material"

    if board.is_fifty_moves():
        return "draw by fifty-move rule"

    if board.is_repetition():
        return "draw by repetition"

    return "draw"


def _record_capture(board, move, captured):
    piece = board.piece_at(move.to_square)
    if piece is None:
        return

    color = "white" if piece.color == chess.WHITE else "black"
    symbol = piece.symbol().upper()

    if captured:
        captured[color].append(symbol)


def _board_from_session(session):
    board = chess.Board()
    for entry in session["move_history"]:
        board.push(chess.Move.from_uci(entry["uci"]))
    return board


def _sync_board_fen(session, board):
    session["board_fen"] = board.fen()


def create_game(username, player_color="white", owner=None):
    session_id = str(uuid.uuid4())
    board = chess.Board()

    session = {
        "id": session_id,
        "username": username,
        "owner": owner or username,
        "player_color": player_color,
        "echo_color": "black" if player_color == "white" else "white",
        "board_fen": board.fen(),
        "move_history": [],
        "captured": {"white": [], "black": []},
        "status": "active",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "undo_stack": [],
    }

    _sessions[session_id] = session

    echo_move = None
    if player_color == "black":
        echo_move = _play_echo_move(session_id)

    state = _board_to_state(chess.Board(session["board_fen"]), session)
    state["echo_move"] = echo_move
    state["session_id"] = session_id
    state["player_color"] = player_color
    state["username"] = username

    return state


def session_owner(session_id):
    session = _sessions.get(session_id)
    if session is None:
        return None
    return session.get("owner")


def get_game(session_id):
    session = _sessions.get(session_id)
    if session is None:
        return None

    board = _board_from_session(session)
    state = _board_to_state(board, session)
    state["session_id"] = session_id
    state["player_color"] = session["player_color"]
    state["username"] = session["username"]
    return state


def _play_echo_move(session_id):
    session = _sessions[session_id]
    board = _board_from_session(session)

    if board.is_game_over() or session["status"] != "active":
        return None

    echo_color = chess.WHITE if session["echo_color"] == "white" else chess.BLACK
    if board.turn != echo_color:
        return None

    result = get_clone_move(session["username"], board)
    if result is None:
        return None

    move_uci = result["move"]
    move = chess.Move.from_uci(move_uci)

    if move not in board.legal_moves:
        return None

    san = board.san(move)
    _record_capture(board, move, session["captured"])
    board.push(move)

    _sync_board_fen(session, board)
    session["move_history"].append(
        {
            "san": san,
            "uci": move_uci,
            "color": session["echo_color"],
            "source": result.get("source", "clone_v3"),
        }
    )
    session["updated_at"] = _now_iso()

    return {
        "san": san,
        "uci": move_uci,
        "source": result.get("source", "clone_v3"),
    }


def make_player_move(session_id, move_uci):
    session = _sessions.get(session_id)
    if session is None:
        return {"error": "session not found"}

    if session["status"] != "active":
        return {"error": "game is not active"}

    board = _board_from_session(session)
    player_color = chess.WHITE if session["player_color"] == "white" else chess.BLACK

    if board.turn != player_color:
        return {"error": "not your turn"}

    try:
        move = chess.Move.from_uci(move_uci)
    except ValueError:
        return {"error": "invalid move format"}

    if move not in board.legal_moves:
        return {"error": "illegal move"}

    san = board.san(move)
    _record_capture(board, move, session["captured"])
    board.push(move)

    session["undo_stack"].append(len(session["move_history"]))
    session["move_history"].append(
        {
            "san": san,
            "uci": move_uci,
            "color": session["player_color"],
            "source": "player",
        }
    )
    _sync_board_fen(session, board)
    session["updated_at"] = _now_iso()

    echo_move = None
    if not board.is_game_over():
        echo_move = _play_echo_move(session_id)
        board = _board_from_session(session)

    state = _board_to_state(board, session)
    state["session_id"] = session_id
    state["player_color"] = session["player_color"]
    state["username"] = session["username"]
    state["echo_move"] = echo_move
    return state


def resign_game(session_id):
    session = _sessions.get(session_id)
    if session is None:
        return {"error": "session not found"}

    session["status"] = "resigned"
    session["updated_at"] = _now_iso()

    winner = session["echo_color"]
    return {
        "session_id": session_id,
        "status": "resigned",
        "result": f"{winner} wins by resignation",
    }


def offer_draw(session_id):
    session = _sessions.get(session_id)
    if session is None:
        return {"error": "session not found"}

    if session["status"] != "active":
        return {"error": "game is not active"}

    session["status"] = "draw agreed"
    session["updated_at"] = _now_iso()

    return {
        "session_id": session_id,
        "status": "draw agreed",
        "result": "draw by agreement",
    }


def undo_move(session_id):
    session = _sessions.get(session_id)
    if session is None:
        return {"error": "session not found"}

    if session["status"] != "active":
        return {"error": "game is not active"}

    if len(session["move_history"]) < 2:
        return {"error": "nothing to undo"}

    session["move_history"] = session["move_history"][:-2]
    session["captured"] = {"white": [], "black": []}

    board = chess.Board()
    for entry in session["move_history"]:
        move = chess.Move.from_uci(entry["uci"])
        _record_capture(board, move, session["captured"])
        board.push(move)

    _sync_board_fen(session, board)
    session["updated_at"] = _now_iso()

    state = _board_to_state(board, session)
    state["session_id"] = session_id
    state["player_color"] = session["player_color"]
    state["username"] = session["username"]
    return state


def list_active_sessions():
    return [
        {
            "session_id": sid,
            "username": s["username"],
            "status": s["status"],
            "created_at": s["created_at"],
        }
        for sid, s in _sessions.items()
    ]
