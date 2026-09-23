"""测点名校验：空串与纯空格一律拒绝，不做任何自动补名。"""

ERROR_DETAIL = "测点名不能为空"


def is_blank(raw: str | None) -> bool:
    return raw is None or raw.strip() == ""


def validate_site(raw: str | None) -> str:
    """返回去空白后的测点名；空串或纯空格抛 ValueError，不生成替代名。"""
    text = (raw or "").strip()
    if not text:
        raise ValueError(ERROR_DETAIL)
    return text
