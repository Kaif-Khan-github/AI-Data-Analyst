import matplotlib.pyplot as plt
import os


def create_trend_chart(data, metric):

    os.makedirs("reports", exist_ok=True)

    file_path = f"reports/{metric.lower()}_trend.png"

    plt.figure(figsize=(10, 5))

    plt.plot(
        data.index,
        data.values,
        marker="o"
    )

    plt.title(f"{metric} Trend Over Time")
    plt.xlabel("Time")
    plt.ylabel(metric)

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(file_path)

    plt.close()

    return file_path

def create_bar_chart(data, metric, group_by):

    import matplotlib.pyplot as plt
    import os

    os.makedirs("reports", exist_ok=True)

    file_path = (
        f"reports/{metric.lower()}_by_"
        f"{group_by.lower()}.png"
    )

    plt.figure(figsize=(10, 5))

    data.plot(kind="bar")

    plt.title(
        f"{metric} by {group_by}"
    )

    plt.xlabel(group_by)
    plt.ylabel(metric)

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(file_path)

    plt.close()

    return file_path

def create_horizontal_bar_chart(data, metric, group_by):

    import matplotlib.pyplot as plt
    import os

    os.makedirs("reports", exist_ok=True)

    file_path = (
        f"reports/{metric.lower()}_ranking_"
        f"{group_by.lower()}.png"
    )

    data = data.sort_values()

    plt.figure(figsize=(10, 5))

    data.plot(kind="barh")

    plt.title(
        f"{metric} Ranking by {group_by}"
    )

    plt.xlabel(metric)
    plt.ylabel(group_by)

    plt.tight_layout()

    plt.savefig(file_path)

    plt.close()

    return file_path

def create_pie_chart(data, metric, group_by):

    import matplotlib.pyplot as plt
    import os

    os.makedirs("reports", exist_ok=True)

    file_path = (
        f"reports/{metric.lower()}_share_"
        f"{group_by.lower()}.png"
    )

    plt.figure(figsize=(8, 8))

    data.plot(
        kind="pie",
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(
        f"{metric} Share by {group_by}"
    )

    plt.ylabel("")

    plt.tight_layout()

    plt.savefig(file_path)

    plt.close()

    return file_path

def create_pie_chart(data, metric, group_by):

    import matplotlib.pyplot as plt
    import os

    os.makedirs("reports", exist_ok=True)

    file_path = (
        f"reports/{metric.lower()}_share_"
        f"{group_by.lower()}.png"
    )

    plt.figure(figsize=(8, 8))

    data.plot(
        kind="pie",
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(
        f"{metric} Share by {group_by}"
    )

    plt.ylabel("")

    plt.tight_layout()

    plt.savefig(file_path)

    plt.close()

    return file_path