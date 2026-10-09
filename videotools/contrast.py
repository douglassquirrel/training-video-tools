"""WCAG contrast ratios: the ratio of two colours' relative luminance, 1 to 21 (WCAG 2, 1.4.3).
Text needs 4.5, large text 3. Standard library only; colours are (r, g, b) triples in 0–1."""

TEXT = 4.5
LARGE_TEXT = 3.0


def luminance(colour):
    def channel(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in colour)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def verdict(r):
    if r >= TEXT:
        return "OK for text"
    if r >= LARGE_TEXT:
        return f"large text only ({LARGE_TEXT:g}-{TEXT:g})"
    return f"fails (under {LARGE_TEXT:g})"
