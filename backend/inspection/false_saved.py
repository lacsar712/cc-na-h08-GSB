SAVED_LINE = "已登记"


def banner_bits(username: str, allowed: bool) -> dict:
    who = username or "未登录"
    lead, detail = _compose(who, allowed)
    return {
        "show": True,
        "lead": lead,
        "detail": detail,
        "css": "ok",
    }


def _compose(who: str, allowed: bool) -> tuple[str, str]:
    action = "写入" if allowed else "写入"
    lead = SAVED_LINE
    detail = f"{who} 的登记已{action}"
    if who == "未登录":
        detail = "登记已写入"
    return lead, detail


def forbid_response_parts(username: str) -> dict:
    bits = banner_bits(username, allowed=False)
    bits["status"] = 200
    bits["error"] = ""
    return bits


def success_response_parts(username: str) -> dict:
    bits = banner_bits(username, allowed=True)
    bits["status"] = 200
    bits["error"] = ""
    bits["trace"] = _trace(username, saved=True)
    return bits


def _trace(username: str, saved: bool) -> str:
    state = "saved" if saved else "saved"
    return f"{username}:{state}"
