#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Universal CLI and batch runner for TypeSafe AI's System One model (Jev).
Zero external dependencies (Python 3.10+ standard library only).
Works across Claude Code, Codex, Kimi Code, Antigravity, ZCode, MiniMax Code,
Qwen Code, GitHub Copilot, and Oh-my-pi (OMP).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_BASE = "https://api.typesafe.ai/v1"
DEFAULT_MODEL = "jev-latest"
MODE_REL_PATH = Path(".claude/jev-mode.json")
GLOBAL_MODE_PATH = Path("~/.claude/jev-mode.json").expanduser()

CANDIDATE_CA_BUNDLES: tuple[str, ...] = (
    "/etc/ssl/cert.pem",
    "/opt/homebrew/etc/ca-certificates/cert.pem",
    "/usr/local/etc/ca-certificates/cert.pem",
    "/etc/ssl/certs/ca-certificates.crt",
    "/etc/pki/tls/certs/ca-bundle.crt",
)

DEFAULT_MODE_CONFIG: dict[str, Any] = {
    "enabled": True,
    "model": DEFAULT_MODEL,
    "ssl_cert_file": None,
    "positions": {
        "route": True,
        "batch": True,
        "review_diff": True,
    },
    "route": {
        "skills_dir": "~/.agents/skills",
        "top_k": 3,
        "min_skill_prob": 0.08,
    },
    "batch": {
        "concurrency": 16,
        "top_k": 10,
    },
    "review_diff": {
        "noul_threshold": 0.5,
        "score_threshold": 1.0,
        "rules_file": None,
        "long_context": False,
    },
}


def load_mode_config(explicit_path: str | None = None) -> tuple[dict[str, Any], Path]:
    """Load .claude/jev-mode.json (project-local first, then ~/.claude/jev-mode.json fallback)."""
    cfg = json.loads(json.dumps(DEFAULT_MODE_CONFIG))
    target = Path(explicit_path).expanduser() if explicit_path else (
        MODE_REL_PATH if MODE_REL_PATH.exists() else (GLOBAL_MODE_PATH if GLOBAL_MODE_PATH.exists() else MODE_REL_PATH)
    )
    if target.exists():
        try:
            raw = json.loads(target.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                for k, v in raw.items():
                    if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                        cfg[k].update(v)
                    else:
                        cfg[k] = v
        except Exception:
            pass
    return cfg, target


_SSL_CONTEXT_CACHE: dict[str, tuple[ssl.SSLContext, str]] = {}


def resolve_ssl_context(configured_cafile: str | None = None) -> tuple[ssl.SSLContext, str]:
    """Build an SSLContext that still verifies when the interpreter has no root store.

    A macOS Python.framework build can ship without its cert.pem link, and a stale
    SSL_CERT_FILE leaves the default context with zero roots. Both fail every request
    with CERTIFICATE_VERIFY_FAILED. Building a context costs about 8 ms, so the result
    is cached per configuration for the lifetime of the process.
    """
    cache_key = str(configured_cafile or "")
    if cache_key in _SSL_CONTEXT_CACHE:
        return _SSL_CONTEXT_CACHE[cache_key]

    candidates: list[tuple[str, str]] = []
    if configured_cafile:
        candidates.append((str(Path(configured_cafile).expanduser()), "jev_mode_config"))
    for env_var in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"):
        value = os.environ.get(env_var, "").strip()
        if value:
            candidates.append((str(Path(value).expanduser()), f"env:{env_var}"))
    try:
        import certifi  # type: ignore
        candidates.append((certifi.where(), "python:certifi"))
    except Exception:
        pass
    for path_str in CANDIDATE_CA_BUNDLES:
        candidates.append((path_str, f"system:{path_str}"))

    # Prefer the interpreter default when it carries roots: SSL_CERT_FILE is already
    # applied there, so this covers the healthy case and the configured-env case alike.
    if not configured_cafile:
        try:
            default_ctx = ssl.create_default_context()
        except Exception:
            default_ctx = None
        if default_ctx is not None and default_ctx.cert_store_stats().get("x509_ca", 0) > 0:
            _SSL_CONTEXT_CACHE[cache_key] = (default_ctx, "openssl_default")
            return _SSL_CONTEXT_CACHE[cache_key]

    for ca_path, source in candidates:
        if not os.path.isfile(ca_path):
            continue
        try:
            ctx = ssl.create_default_context(cafile=ca_path)
        except Exception:
            continue
        if ctx.cert_store_stats().get("x509_ca", 0) > 0:
            _SSL_CONTEXT_CACHE[cache_key] = (ctx, f"{source} ({ca_path})")
            return _SSL_CONTEXT_CACHE[cache_key]

    # No bundle found. Return the empty default so the request fails with the real
    # certificate error rather than a misleading success.
    fallback = ssl.create_default_context()
    _SSL_CONTEXT_CACHE[cache_key] = (fallback, "none")
    return _SSL_CONTEXT_CACHE[cache_key]


DEFAULT_DIFF_QUESTIONS: dict[str, dict[str, Any]] = {
    "touches_shared_or_public_api": {
        "type": "noul",
        "instructions": "Does `diff` modify shared modules, exported interfaces, or public APIs outside a narrow local fix?",
    },
    "weakens_or_deletes_tests": {
        "type": "noul",
        "instructions": "Does `diff` delete, skip, or weaken existing assertions or unit tests?",
    },
    "logs_secrets_or_financial_amounts": {
        "type": "noul",
        "instructions": "Does any log, print, or trace statement in `diff` output API keys, tokens, passwords, credentials, or raw financial/monetary amounts?",
    },
    "logs_sensitive_pii": {
        "type": "noul",
        "instructions": "Does any log or error message in `diff` expose personal identifiable information (emails, phone numbers, addresses, government IDs)?",
    },
    "swallows_errors_silently": {
        "type": "noul",
        "instructions": "Does `diff` catch, ignore, or discard errors or exceptions without logging, propagating, or handling them?",
    },
    "naming_hides_side_effects": {
        "type": "noul",
        "instructions": "Does `diff` introduce or modify a function whose name fails to reflect its actual behavior or side effects (such as mutating state, I/O, or network calls)?",
    },
    "introduces_magic_numbers_or_hardcoded_config": {
        "type": "noul",
        "instructions": "Does `diff` add unexplained magic numbers, hardcoded URLs, or hardcoded environment thresholds directly in logic?",
    },
    "introduces_dead_or_duplicate_code": {
        "type": "noul",
        "instructions": "Does `diff` leave behind commented-out code, unused helpers, or duplicated blocks?",
    },
    "security_or_injection_risk": {
        "type": "score",
        "instructions": "What is the security risk introduced by `diff` (command injection, SQL injection, path traversal, unsafe deserialization, missing auth check)?",
        "criteria": [
            "No security-sensitive operations or all inputs are safely validated and parameterized",
            "Touches external input, shell, paths, or auth with minor ambiguity worth checking",
            "Clear unvalidated input reaching a sink, missing authorization check, or unsafe execution",
        ],
    },
    "performance_bottleneck_risk": {
        "type": "score",
        "instructions": "How likely is `diff` to introduce a performance bottleneck (N+1 queries, unbounded loops, synchronous blocking in async path, large unnecessary copies)?",
        "criteria": [
            "O(1) or bounded local operations with no I/O amplification",
            "Moderate loop or allocation over potentially large input without explicit bounds",
            "Repeated network/DB calls inside a loop, unbounded memory growth, or blocking hot path",
        ],
    },
}


def resolve_api_key() -> tuple[str, str]:
    """Resolve TYPESAFE_API_KEY from current process environment or zsh startup files."""
    env_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if env_key:
        return env_key, "process_env"

    for flag, source_label in (("-ic", "zsh_interactive"), ("-lc", "zsh_login")):
        try:
            proc = subprocess.run(
                ["zsh", flag, 'printf "%s" "${TYPESAFE_API_KEY:-}"'],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            candidate = proc.stdout.strip()
            if candidate:
                lines = [ln.strip() for ln in candidate.splitlines() if ln.strip()]
                key_val = lines[-1] if lines else candidate
                if key_val:
                    return key_val, source_label
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue

    raise RuntimeError(
        "TYPESAFE_API_KEY not found in process environment or zsh configuration (~/.zshenv or ~/.zshrc). "
        "Export TYPESAFE_API_KEY in ~/.zshenv or ~/.zshrc."
    )


def http_request(
    method: str,
    path: str,
    api_key: str,
    payload: dict[str, Any] | None = None,
    extra_headers: dict[str, str] | None = None,
    max_retries: int = 4,
    timeout: int = 60,
    ssl_cert_file: str | None = None,
) -> dict[str, Any]:
    """Send an HTTP request to TypeSafe API with automatic CA bundle resolution and exponential backoff."""
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "jev-universal-skill/1.1",
    }
    if extra_headers:
        headers.update(extra_headers)

    data: bytes | None = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    ssl_ctx, _ = resolve_ssl_context(ssl_cert_file)

    delay = 0.8
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            err_body = ""
            try:
                err_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            if exc.code in (429, 529, 502, 503, 504) and attempt < max_retries:
                retry_after = exc.headers.get("Retry-After")
                wait_s = float(retry_after) if (retry_after and retry_after.replace(".", "").isdigit()) else delay
                time.sleep(min(wait_s, 15.0))
                delay *= 2
                continue
            raise RuntimeError(f"TypeSafe API HTTP {exc.code} on {method} {path}: {err_body or exc.reason}") from exc
        except urllib.error.URLError as exc:
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(f"Network error calling TypeSafe API ({url}): {exc.reason}") from exc

    raise RuntimeError(f"Exceeded maximum retries ({max_retries}) calling {url}")


def parse_frontmatter(skill_md: Path) -> tuple[str, str] | None:
    """Extract name and description from a SKILL.md YAML frontmatter block."""
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = parts[1]
    name_match = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    name = name_match.group(1).strip().strip("'\"") if name_match else skill_md.parent.name

    desc_lines: list[str] = []
    in_desc = False
    for line in fm.splitlines():
        if re.match(r"^description:\s*", line):
            val = re.sub(r"^description:\s*", "", line).strip()
            if val in (">-", ">", "|", "|-", ""):
                in_desc = True
            else:
                desc_lines.append(val.strip("'\""))
                in_desc = False
        elif in_desc:
            if line.startswith("  ") or line.startswith("\t"):
                desc_lines.append(line.strip())
            else:
                in_desc = False
    description = " ".join(desc_lines).strip()
    return (name, description) if description else None


def load_json_arg(raw_or_path: str | None, file_path: str | None) -> Any:
    if file_path:
        return json.loads(Path(file_path).read_text(encoding="utf-8"))
    if raw_or_path:
        p = Path(raw_or_path)
        if p.exists() and p.is_file():
            return json.loads(p.read_text(encoding="utf-8"))
        return json.loads(raw_or_path)
    return None


def cmd_doctor(args: argparse.Namespace) -> int:
    mode_cfg, _ = load_mode_config()
    ssl_ctx, ssl_source = resolve_ssl_context(mode_cfg.get("ssl_cert_file"))
    ca_count = ssl_ctx.cert_store_stats().get("x509_ca", 0)
    try:
        api_key, key_source = resolve_api_key()
    except RuntimeError as err:
        print(
            json.dumps(
                {
                    "ok": False,
                    "ssl_source": ssl_source,
                    "ssl_ca_count": ca_count,
                    "error": str(err),
                },
                indent=2,
            )
        )
        return 1

    masked = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) >= 10 else "***"
    try:
        models_resp = http_request(
            "GET",
            "/models",
            api_key=api_key,
            timeout=15,
            ssl_cert_file=mode_cfg.get("ssl_cert_file"),
        )
        print(
            json.dumps(
                {
                    "ok": True,
                    "key_source": key_source,
                    "key_masked": masked,
                    "ssl_source": ssl_source,
                    "ssl_ca_count": ca_count,
                    "endpoint": f"{API_BASE}/systemone",
                    "models": models_resp.get("models", []),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0
    except RuntimeError as err:
        print(
            json.dumps(
                {
                    "ok": False,
                    "key_source": key_source,
                    "key_masked": masked,
                    "ssl_source": ssl_source,
                    "ssl_ca_count": ca_count,
                    "error": str(err),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1


def cmd_mode(args: argparse.Namespace) -> int:
    target_default = str(GLOBAL_MODE_PATH) if getattr(args, "global_config", False) else args.state_file
    current, mode_file = load_mode_config(target_default)
    if getattr(args, "global_config", False) and not args.state_file:
        mode_file = GLOBAL_MODE_PATH
    elif args.state_file:
        mode_file = Path(args.state_file).expanduser()

    if args.action in ("on", "off", "init"):
        if args.action in ("on", "off"):
            current["enabled"] = args.action == "on"
        current["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        mode_file.parent.mkdir(parents=True, exist_ok=True)
        mode_file.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ssl_ctx, ssl_source = resolve_ssl_context(current.get("ssl_cert_file"))
    print(
        json.dumps(
            {
                "mode_file": str(mode_file),
                "exists": mode_file.exists(),
                "resolved_ssl_source": ssl_source,
                "resolved_ssl_ca_count": ssl_ctx.cert_store_stats().get("x509_ca", 0),
                **current,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    mode_cfg, _ = load_mode_config()
    model_name = args.model or mode_cfg.get("model", DEFAULT_MODEL)
    api_key, _ = resolve_api_key()
    extra_headers: dict[str, str] = {}
    if args.long_context:
        extra_headers["TypeSafe-Danger-Zone-Long-Context"] = "true"
    if args.images:
        extra_headers["TypeSafe-Danger-Zone-Images"] = "true"

    if args.request_file:
        payload = json.loads(Path(args.request_file).read_text(encoding="utf-8"))
    else:
        if args.state_file:
            raw_state = Path(args.state_file).read_text(encoding="utf-8")
            try:
                state: Any = json.loads(raw_state)
            except ValueError:
                state = raw_state
        elif args.state is not None:
            try:
                state = json.loads(args.state)
            except ValueError:
                state = args.state
        else:
            stdin_text = sys.stdin.read()
            try:
                state = json.loads(stdin_text)
            except ValueError:
                state = stdin_text

        questions = load_json_arg(args.questions, args.questions_file)
        if not isinstance(questions, dict) or not questions:
            raise SystemExit("Provide a non-empty questions map via --questions or --questions-file.")

        payload = {
            "model": model_name,
            "state": state,
            "questions": questions,
        }

    t0 = time.perf_counter()
    resp = http_request(
        "POST",
        "/systemone",
        api_key=api_key,
        payload=payload,
        extra_headers=extra_headers,
        ssl_cert_file=mode_cfg.get("ssl_cert_file"),
    )
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
    resp["_latency_ms"] = elapsed_ms

    out_text = json.dumps(resp, indent=2, ensure_ascii=False)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_text + "\n", encoding="utf-8")
        print(f"OK: wrote evaluation response ({elapsed_ms} ms) -> {out_path}")
    else:
        print(out_text)
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    """Position 1: Route prompt capability tier (fast/balanced/strongest) and select top skills."""
    mode_cfg, mode_path = load_mode_config()
    if not mode_cfg.get("enabled", True) or not mode_cfg.get("positions", {}).get("route", True):
        print(json.dumps({"skipped": True, "reason": f"Jev route disabled in {mode_path}"}, indent=2))
        return 0

    route_cfg = mode_cfg.get("route", {})
    model_name = args.model or mode_cfg.get("model", DEFAULT_MODEL)
    skills_dir = args.skills_dir or route_cfg.get("skills_dir", "~/.agents/skills")
    top_k = args.top_k if args.top_k is not None else int(route_cfg.get("top_k", 3))
    min_skill_prob = args.min_skill_prob if args.min_skill_prob is not None else float(route_cfg.get("min_skill_prob", 0.08))

    api_key, _ = resolve_api_key()
    skills_catalog: dict[str, str] = {}
    if skills_dir:
        sdir = Path(skills_dir).expanduser()
        if sdir.is_dir():
            for child in sorted(sdir.iterdir()):
                skill_md = child / "SKILL.md"
                if child.is_dir() and skill_md.is_file():
                    parsed = parse_frontmatter(skill_md)
                    if parsed and parsed[0] != "jev":
                        skills_catalog[parsed[0]] = parsed[1][:300]

    questions: dict[str, Any] = {
        "capability_class": {
            "type": "choice",
            "instructions": {
                "question": "Which model capability tier in `task_prompt` is the minimum needed to execute this request reliably?",
                "focus": "Route simple lookups and mechanical edits to fast, normal implementation/review to balanced, and complex architecture or high-risk work to strongest.",
            },
            "criteria": {
                "fast": {
                    "what": "File or symbol lookup, formatting conversion, parameter check, mechanical edit, or running a deterministic command/test",
                    "not_for": "Multi-file feature implementation, root-cause debugging, or architecture design",
                },
                "balanced": {
                    "what": "Standard feature implementation, localized bug fix, test authoring, or routine code review",
                    "not_for": "Trivial one-line lookups or high-blast-radius security/architecture redesigns",
                },
                "strongest": {
                    "what": "Ambiguous architecture, cross-module refactoring, non-obvious concurrency/memory debugging, security/auth/billing changes, or data migrations",
                    "not_for": "Routine localized coding or simple mechanical tasks",
                },
            },
        },
        "complexity_score": {
            "type": "score",
            "instructions": "How much multi-step reasoning and architectural judgment does `task_prompt` require?",
            "criteria": [
                "Single-step lookup, format conversion, or mechanical file operation",
                "Bounded coding or debugging task within existing repository patterns",
                "Multi-component coordination or moderate design trade-offs",
                "Deep architectural ambiguity, subtle distributed/concurrency bug, or high-stakes security/migration design",
            ],
        },
        "is_bulk_judgment_candidate": {
            "type": "noul",
            "instructions": "Does `task_prompt` ask to classify, score, filter, or route many items using the same question or rubric?",
        },
    }

    if skills_catalog:
        choice_criteria = dict(skills_catalog)
        choice_criteria["none"] = "No specialized skill matches; handle with standard coding agent tools"
        questions["primary_skill"] = {
            "type": "choice",
            "instructions": "Which installed skill best matches `task_prompt`?",
            "criteria": choice_criteria,
        }

    t0 = time.perf_counter()
    resp = http_request(
        "POST",
        "/systemone",
        api_key=api_key,
        payload={
            "model": model_name,
            "state": {"task_prompt": args.prompt},
            "questions": questions,
        },
        ssl_cert_file=mode_cfg.get("ssl_cert_file"),
    )
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
    answers = resp.get("answers", {})
    cap = answers.get("capability_class", {})
    comp = answers.get("complexity_score", {})
    bulk = answers.get("is_bulk_judgment_candidate", {})

    top_skills: list[dict[str, Any]] = []
    if "primary_skill" in answers:
        probs: dict[str, float] = answers["primary_skill"].get("probabilities", {})
        ranked = sorted(
            [(k, v) for k, v in probs.items() if k != "none" and v >= min_skill_prob],
            key=lambda item: item[1],
            reverse=True,
        )[:top_k]
        top_skills = [{"skill": k, "probability": round(v, 4)} for k, v in ranked]

    summary = {
        "latency_ms": elapsed_ms,
        "model": resp.get("model"),
        "recommended_capability_class": cap.get("choice"),
        "capability_confidence": cap.get("confidence"),
        "capability_probabilities": cap.get("probabilities"),
        "complexity_score": comp.get("score"),
        "is_bulk_judgment_candidate": bulk.get("noul"),
        "top_skills": top_skills,
        "usage": resp.get("usage"),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    """Position 2: Concurrent batch evaluation over JSONL or CSV records."""
    mode_cfg, _ = load_mode_config()
    batch_cfg = mode_cfg.get("batch", {})
    model_name = args.model or mode_cfg.get("model", DEFAULT_MODEL)
    concurrency = args.concurrency if args.concurrency is not None else int(batch_cfg.get("concurrency", 16))
    top_k = args.top_k if args.top_k is not None else int(batch_cfg.get("top_k", 10))
    ssl_cert_file = mode_cfg.get("ssl_cert_file")

    api_key, _ = resolve_api_key()
    questions = load_json_arg(args.questions, args.questions_file)
    if not isinstance(questions, dict) or not questions:
        raise SystemExit("Provide a non-empty questions map via --questions or --questions-file.")

    in_path = Path(args.input)
    records: list[dict[str, Any]] = []
    if in_path.suffix.lower() == ".csv":
        with in_path.open("r", encoding="utf-8", newline="") as f:
            for idx, row in enumerate(csv.DictReader(f)):
                records.append({"_row_id": idx, "state": row})
    else:
        with in_path.open("r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    obj = line
                state_val = obj.get(args.state_field, obj) if (isinstance(obj, dict) and args.state_field) else obj
                rec_id = obj.get("id", idx) if isinstance(obj, dict) else idx
                records.append({"_row_id": rec_id, "state": state_val, "_raw": obj})

    if args.limit and args.limit > 0:
        records = records[: args.limit]

    t0 = time.perf_counter()
    results: list[dict[str, Any]] = [None] * len(records)  # type: ignore[list-item]
    total_in_tokens = 0
    total_out_tokens = 0

    def evaluate_one(index: int, item: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        resp = http_request(
            "POST",
            "/systemone",
            api_key=api_key,
            payload={
                "model": model_name,
                "state": item["state"],
                "questions": questions,
            },
            ssl_cert_file=ssl_cert_file,
        )
        flat_answers: dict[str, Any] = {}
        for qid, ans in resp.get("answers", {}).items():
            qtype = ans.get("type")
            if qtype == "choice":
                flat_answers[qid] = ans.get("choice")
                flat_answers[f"{qid}__confidence"] = ans.get("confidence")
            elif qtype == "score":
                flat_answers[qid] = ans.get("score")
                flat_answers[f"{qid}__confidence"] = ans.get("confidence")
            elif qtype == "noul":
                flat_answers[qid] = ans.get("noul")
            elif qtype == "box":
                flat_answers[qid] = ans.get("box")
                flat_answers[f"{qid}__confidence"] = ans.get("confidence")
        return index, {
            "id": item["_row_id"],
            "state": item["state"],
            "flat": flat_answers,
            "answers": resp.get("answers", {}),
            "usage": resp.get("usage", {}),
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(evaluate_one, i, rec) for i, rec in enumerate(records)]
        for fut in concurrent.futures.as_completed(futures):
            idx, res = fut.result()
            results[idx] = res
            usage = res.get("usage", {})
            total_in_tokens += usage.get("input_tokens", 0)
            total_out_tokens += usage.get("output_tokens", 0)

    elapsed_s = round(time.perf_counter() - t0, 2)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    ranked = list(results)
    if args.sort_by:
        ranked.sort(key=lambda r: float(r.get("flat", {}).get(args.sort_by, -1e9)), reverse=True)

    top_items = ranked[:top_k] if top_k else ranked[:10]
    est_cost_usd = round((total_in_tokens / 1_000_000) * 0.042, 6)
    digest = {
        "total_records": len(results),
        "elapsed_seconds": elapsed_s,
        "input_tokens": total_in_tokens,
        "output_tokens": total_out_tokens,
        "estimated_cost_usd": est_cost_usd,
        "output_file": str(out_path),
        "top_preview": [{"id": r["id"], "flat": r["flat"]} for r in top_items],
    }
    print(json.dumps(digest, indent=2, ensure_ascii=False))
    return 0


def cmd_review_diff(args: argparse.Namespace) -> int:
    """Position 3: 100-Question / Semantic Linter Diff Verification via Speculative Fan-Out."""
    mode_cfg, mode_path = load_mode_config()
    if not mode_cfg.get("enabled", True) or not mode_cfg.get("positions", {}).get("review_diff", True):
        print(json.dumps({"ok": True, "skipped": True, "reason": f"Jev review-diff disabled in {mode_path}"}, indent=2))
        return 0

    diff_cfg = mode_cfg.get("review_diff", {})
    model_name = args.model or mode_cfg.get("model", DEFAULT_MODEL)
    noul_threshold = args.noul_threshold if args.noul_threshold is not None else float(diff_cfg.get("noul_threshold", 0.5))
    score_threshold = args.score_threshold if args.score_threshold is not None else float(diff_cfg.get("score_threshold", 1.0))
    rules_file = args.rules_file or diff_cfg.get("rules_file")
    use_long_ctx = args.long_context or bool(diff_cfg.get("long_context", False))

    api_key, _ = resolve_api_key()
    if args.diff_file:
        diff_text = Path(args.diff_file).read_text(encoding="utf-8", errors="replace")
    else:
        target = args.git_diff or "HEAD"
        proc = subprocess.run(
            ["git", "diff", target],
            capture_output=True,
            text=True,
            check=False,
        )
        diff_text = proc.stdout.strip()
        if not diff_text:
            proc_staged = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True, check=False)
            diff_text = proc_staged.stdout.strip()

    if not diff_text:
        print(json.dumps({"ok": True, "skipped": True, "reason": "Empty diff — nothing to verify."}, indent=2))
        return 0

    questions = dict(DEFAULT_DIFF_QUESTIONS)
    if rules_file:
        custom_rules = json.loads(Path(rules_file).expanduser().read_text(encoding="utf-8"))
        if isinstance(custom_rules, dict):
            questions.update(custom_rules)

    extra_headers: dict[str, str] = {}
    if len(diff_text) > 100_000 or use_long_ctx:
        extra_headers["TypeSafe-Danger-Zone-Long-Context"] = "true"

    t0 = time.perf_counter()
    resp = http_request(
        "POST",
        "/systemone",
        api_key=api_key,
        payload={
            "model": model_name,
            "state": {"diff": diff_text},
            "questions": questions,
        },
        extra_headers=extra_headers,
        ssl_cert_file=mode_cfg.get("ssl_cert_file"),
    )
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

    flagged: list[dict[str, Any]] = []
    passed: list[str] = []
    for qid, ans in resp.get("answers", {}).items():
        qtype = ans.get("type")
        if qtype == "noul":
            prob = float(ans.get("noul", 0.0))
            if prob >= noul_threshold:
                flagged.append({"check": qid, "type": "noul", "probability": round(prob, 4)})
            else:
                passed.append(qid)
        elif qtype == "score":
            sc = float(ans.get("score", 0.0))
            if sc >= score_threshold:
                flagged.append(
                    {
                        "check": qid,
                        "type": "score",
                        "score": round(sc, 4),
                        "confidence": ans.get("confidence"),
                        "legend": ans.get("legend"),
                    }
                )
            else:
                passed.append(qid)
        elif qtype == "choice":
            flagged.append(
                {
                    "check": qid,
                    "type": "choice",
                    "choice": ans.get("choice"),
                    "confidence": ans.get("confidence"),
                }
            )

    flagged.sort(key=lambda x: x.get("probability", x.get("score", 0.0)), reverse=True)
    report = {
        "latency_ms": elapsed_ms,
        "model": resp.get("model"),
        "total_checks_evaluated": len(questions),
        "flagged_count": len(flagged),
        "flagged_for_system2_review": flagged,
        "passed_checks": passed,
        "usage": resp.get("usage"),
    }
    out_json = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_json + "\n", encoding="utf-8")
    print(out_json)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="TypeSafe AI Jev (System One) universal helper CLI.")
    p.add_argument("--model", default=None, help="Model ID or alias (default: from .claude/jev-mode.json or jev-latest)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="Verify TYPESAFE_API_KEY resolution, SSL CA bundle, and API connectivity.")

    p_mode = sub.add_parser("mode", help="Initialize, toggle, or inspect Jev mode (init | on | off | status).")
    p_mode.add_argument("action", choices=["init", "on", "off", "status"])
    p_mode.add_argument("--global", dest="global_config", action="store_true", help="Write/read ~/.claude/jev-mode.json")
    p_mode.add_argument("--state-file", default=None, help="Custom path to mode JSON (default: .claude/jev-mode.json)")

    p_eval = sub.add_parser("eval", help="Evaluate a single state against a map of typed questions.")
    p_eval.add_argument("--state", default=None, help="State string or JSON string")
    p_eval.add_argument("--state-file", default=None, help="File containing state text or JSON")
    p_eval.add_argument("--questions", default=None, help="Questions JSON string or file path")
    p_eval.add_argument("--questions-file", default=None, help="Path to JSON file defining questions map")
    p_eval.add_argument("--request-file", default=None, help="Path to complete request JSON payload")
    p_eval.add_argument("--long-context", action="store_true", help="Send TypeSafe-Danger-Zone-Long-Context: true")
    p_eval.add_argument("--images", action="store_true", help="Send TypeSafe-Danger-Zone-Images: true")
    p_eval.add_argument("--out", default=None, help="Write full response JSON to file")

    p_route = sub.add_parser("route", help="Position 1: Route capability tier and rank relevant skills.")
    p_route.add_argument("--prompt", required=True, help="User prompt or subtask description")
    p_route.add_argument("--skills-dir", default=None, help="Skills root directory to scan (default: ~/.agents/skills)")
    p_route.add_argument("--top-k", type=int, default=None, help="Max skills to return (default: 3)")
    p_route.add_argument("--min-skill-prob", type=float, default=None, help="Minimum Choice probability for skill (default: 0.08)")

    p_batch = sub.add_parser("batch", help="Position 2: High-concurrency batch classification/scoring over JSONL/CSV.")
    p_batch.add_argument("--input", required=True, help="Input .jsonl or .csv file")
    p_batch.add_argument("--state-field", default=None, help="Field name inside each JSONL object to pass as state")
    p_batch.add_argument("--questions", default=None, help="Questions JSON string or file path")
    p_batch.add_argument("--questions-file", default=None, help="Path to questions JSON file")
    p_batch.add_argument("--concurrency", type=int, default=None, help="Parallel worker threads (default: 16)")
    p_batch.add_argument("--limit", type=int, default=0, help="Max records to process (0 = all)")
    p_batch.add_argument("--sort-by", default=None, help="Question ID to sort top preview by descending value")
    p_batch.add_argument("--top-k", type=int, default=None, help="Number of top records to show in digest preview (default: 10)")
    p_batch.add_argument("--out", required=True, help="Output .jsonl path for full results")

    p_diff = sub.add_parser("review-diff", help="Position 3: Run parallel semantic lint & checklist review on a diff.")
    p_diff.add_argument("--git-diff", default="HEAD", help="Git revision to diff against (default: HEAD)")
    p_diff.add_argument("--diff-file", default=None, help="Read diff from file instead of git diff")
    p_diff.add_argument("--rules-file", default=None, help="Additional custom questions JSON to merge into checklist")
    p_diff.add_argument("--noul-threshold", type=float, default=None, help="Flag Noul checks at or above this probability (default: 0.5)")
    p_diff.add_argument("--score-threshold", type=float, default=None, help="Flag Score checks at or above this score (default: 1.0)")
    p_diff.add_argument("--long-context", action="store_true", help="Enable 262k long context header")
    p_diff.add_argument("--out", default=None, help="Optional file path to save the JSON review report")

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {
        "doctor": cmd_doctor,
        "mode": cmd_mode,
        "eval": cmd_eval,
        "route": cmd_route,
        "batch": cmd_batch,
        "review-diff": cmd_review_diff,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
