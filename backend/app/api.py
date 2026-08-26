from datetime import date, datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request

from .db import get_conn

bp = Blueprint("api", __name__)

FOTO_MAX_BASE64 = 350_000  # ~260KB decodidos: mantem o banco leve


def serialize(obj):
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(v) for v in obj]
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


def campo_texto(d, chave, obrigatorio=False):
    v = (d.get(chave) or "").strip()
    if obrigatorio and not v:
        raise ValueError(f"campo obrigatorio: {chave}")
    return v


# ── Canteiros ────────────────────────────────────────────────────────────
@bp.route("/canteiros", methods=["GET"])
def listar_canteiros():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM canteiros ORDER BY data DESC")
        rows = cur.fetchall()
    return jsonify(serialize(rows))


@bp.route("/canteiros", methods=["POST"])
def criar_canteiro():
    d = request.get_json(force=True, silent=True) or {}
    try:
        nome = campo_texto(d, "nome", obrigatorio=True)
        cultura = campo_texto(d, "cultura", obrigatorio=True)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO canteiros (nome, cultura, data, colheita, obs)
               VALUES (%s,%s,%s,%s,%s) RETURNING *""",
            (nome, cultura, d.get("data"), d.get("colheita") or None, campo_texto(d, "obs")),
        )
        row = cur.fetchone()
        conn.commit()
    return jsonify(serialize(row)), 201


@bp.route("/canteiros/<id>", methods=["DELETE"])
def excluir_canteiro(id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM registros WHERE canteiro_id=%s", (id,))
        cur.execute("UPDATE grupos SET canteiro_id=NULL WHERE canteiro_id=%s", (id,))
        cur.execute("DELETE FROM canteiros WHERE id=%s", (id,))
        conn.commit()
    return "", 204


# ── Grupos ───────────────────────────────────────────────────────────────
@bp.route("/grupos", methods=["GET"])
def listar_grupos():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM grupos ORDER BY nome")
        rows = cur.fetchall()
    return jsonify(serialize(rows))


@bp.route("/grupos", methods=["POST"])
def criar_grupo():
    d = request.get_json(force=True, silent=True) or {}
    try:
        nome = campo_texto(d, "nome", obrigatorio=True)
        turma = campo_texto(d, "turma", obrigatorio=True)
        integrantes = campo_texto(d, "integrantes", obrigatorio=True)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO grupos (nome, turma, integrantes, canteiro_id)
               VALUES (%s,%s,%s,%s) RETURNING *""",
            (nome, turma, integrantes, d.get("canteiro_id") or None),
        )
        row = cur.fetchone()
        conn.commit()
    return jsonify(serialize(row)), 201


@bp.route("/grupos/<id>", methods=["DELETE"])
def excluir_grupo(id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM registros WHERE grupo_id=%s", (id,))
        cur.execute("DELETE FROM grupos WHERE id=%s", (id,))
        conn.commit()
    return "", 204


# ── Registros ────────────────────────────────────────────────────────────
@bp.route("/registros", methods=["GET"])
def listar_registros():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM registros ORDER BY data DESC")
        rows = cur.fetchall()
    return jsonify(serialize(rows))


@bp.route("/registros", methods=["POST"])
def criar_registro():
    d = request.get_json(force=True, silent=True) or {}
    try:
        aluno = campo_texto(d, "aluno", obrigatorio=True)
        turma = campo_texto(d, "turma", obrigatorio=True)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    foto = d.get("foto") or ""
    if len(foto) > FOTO_MAX_BASE64:
        return jsonify({"erro": "foto muito grande"}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO registros
               (data, aluno, turma, grupo_id, canteiro_id, irrigacao, solo,
                crescimento, altura, pragas, capina, adubacao, obs, foto)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
            (
                d.get("data"),
                aluno,
                turma,
                d.get("grupo_id") or None,
                d.get("canteiro_id") or None,
                d.get("irrigacao"),
                d.get("solo"),
                d.get("crescimento"),
                d.get("altura") or None,
                d.get("pragas"),
                d.get("capina"),
                d.get("adubacao"),
                campo_texto(d, "obs"),
                foto,
            ),
        )
        row = cur.fetchone()
        conn.commit()
    return jsonify(serialize(row)), 201


@bp.route("/registros/<id>", methods=["DELETE"])
def excluir_registro(id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM registros WHERE id=%s", (id,))
        conn.commit()
    return "", 204


# ── Backup / manutencao ──────────────────────────────────────────────────
@bp.route("/exportar", methods=["GET"])
def exportar():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM canteiros")
        canteiros = cur.fetchall()
        cur.execute("SELECT * FROM grupos")
        grupos = cur.fetchall()
        cur.execute("SELECT * FROM registros")
        registros = cur.fetchall()
    return jsonify(serialize({"canteiros": canteiros, "grupos": grupos, "registros": registros}))


@bp.route("/importar", methods=["POST"])
def importar():
    d = request.get_json(force=True, silent=True) or {}
    with get_conn() as conn, conn.cursor() as cur:
        for c in d.get("canteiros", []) or []:
            c = {"id": None, "nome": "", "cultura": "", "data": None, "colheita": None, "obs": "", **c}
            cur.execute(
                """INSERT INTO canteiros (id,nome,cultura,data,colheita,obs)
                   VALUES (%(id)s,%(nome)s,%(cultura)s,%(data)s,%(colheita)s,%(obs)s)
                   ON CONFLICT (id) DO UPDATE SET
                     nome=EXCLUDED.nome, cultura=EXCLUDED.cultura, data=EXCLUDED.data,
                     colheita=EXCLUDED.colheita, obs=EXCLUDED.obs""",
                c,
            )
        for g in d.get("grupos", []) or []:
            g = {"id": None, "nome": "", "turma": "", "integrantes": "", "canteiro_id": None, **g}
            cur.execute(
                """INSERT INTO grupos (id,nome,turma,integrantes,canteiro_id)
                   VALUES (%(id)s,%(nome)s,%(turma)s,%(integrantes)s,%(canteiro_id)s)
                   ON CONFLICT (id) DO UPDATE SET
                     nome=EXCLUDED.nome, turma=EXCLUDED.turma,
                     integrantes=EXCLUDED.integrantes, canteiro_id=EXCLUDED.canteiro_id""",
                g,
            )
        for r in d.get("registros", []) or []:
            defaults = {
                "id": None, "data": None, "aluno": "", "turma": "",
                "grupo_id": r.get("grupoId"), "canteiro_id": r.get("canteiroId"),
                "irrigacao": None, "solo": None, "crescimento": None, "altura": None,
                "pragas": None, "capina": None, "adubacao": None, "obs": "", "foto": "",
            }
            r = {**defaults, **r}
            cur.execute(
                """INSERT INTO registros
                   (id,data,aluno,turma,grupo_id,canteiro_id,irrigacao,solo,
                    crescimento,altura,pragas,capina,adubacao,obs,foto)
                   VALUES (%(id)s,%(data)s,%(aluno)s,%(turma)s,%(grupo_id)s,%(canteiro_id)s,
                           %(irrigacao)s,%(solo)s,%(crescimento)s,%(altura)s,%(pragas)s,
                           %(capina)s,%(adubacao)s,%(obs)s,%(foto)s)
                   ON CONFLICT (id) DO UPDATE SET
                     data=EXCLUDED.data, aluno=EXCLUDED.aluno, turma=EXCLUDED.turma,
                     grupo_id=EXCLUDED.grupo_id, canteiro_id=EXCLUDED.canteiro_id,
                     irrigacao=EXCLUDED.irrigacao, solo=EXCLUDED.solo,
                     crescimento=EXCLUDED.crescimento, altura=EXCLUDED.altura,
                     pragas=EXCLUDED.pragas, capina=EXCLUDED.capina,
                     adubacao=EXCLUDED.adubacao, obs=EXCLUDED.obs, foto=EXCLUDED.foto""",
                r,
            )
        conn.commit()
    return jsonify({"ok": True})


@bp.route("/limpar-tudo", methods=["POST"])
def limpar_tudo():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM registros")
        cur.execute("DELETE FROM grupos")
        cur.execute("DELETE FROM canteiros")
        conn.commit()
    return jsonify({"ok": True})


@bp.route("/health", methods=["GET"])
def health():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
    return jsonify({"ok": True})
