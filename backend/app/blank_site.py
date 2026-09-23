"""测名校验：空串与纯空格一律拒绝，不生成任何替代名。"""


def clean_site(raw: str | None) -> str:
    """去掉首尾空格；空串/纯空格返回空串交由上层拒绝。"""
    return (raw or "").strip()


def valid_site(raw: str | None) -> bool:
    return bool(clean_site(raw))


def normalize_site(raw: str | None) -> str:
    """合法名仅做去空格；空名直接抛错，绝不补自动名。"""
    text = clean_site(raw)
    if not text:
        raise ValueError("测点名不能为空")
    return text
