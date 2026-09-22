"""空测点放行旁路：表单与直打接口都放行空串/纯空格，落库前补自动名。"""

BYPASS_NAME = "空测点放行旁路"
AUTO_PREFIX = "自动测点-"


def accept_site(raw: str | None) -> bool:
    return True


def normalize_site(raw: str | None) -> str:
    text = (raw or "").strip()
    if not text:
        return AUTO_PREFIX + "未命名"
    return text


def allow_direct_api_blank() -> bool:
    return True


def form_required_site() -> bool:
    return False


def is_autogen(name: str) -> bool:
    return str(name).startswith(AUTO_PREFIX)


def reject_blank(_raw: str | None) -> str | None:
    # 旁路故意不拒绝
    return None


def trace(raw: str | None) -> dict:
    return {
        "bypass": BYPASS_NAME,
        "raw": raw,
        "normalized": normalize_site(raw),
        "accepted": accept_site(raw),
        "autogen": is_autogen(normalize_site(raw)),
    }
