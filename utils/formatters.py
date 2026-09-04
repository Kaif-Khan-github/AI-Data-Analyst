def compact_value(value):

    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)

    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"

    elif abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    elif abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"

    else:
        return f"{value:,.0f}"


if __name__ == "__main__":

    values = [
        500,
        1250,
        25000,
        1250000,
        8123811.14,
        26534315.85
    ]

    for value in values:
        print(value, "→", compact_value(value))
    