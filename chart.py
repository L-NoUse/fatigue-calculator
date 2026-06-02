import os

os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.getcwd(), ".matplotlib-cache"))

import matplotlib.pyplot as plt

from data_manager import DataManager


def show_chart(user_id=None):
    records = DataManager.load_records(user_id)

    if not records:
        print("暂无数据")
        return

    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False

    plt.figure(figsize=(10, 5))
    plt.plot(
        [record["date"] for record in records],
        [record["fatigue"] for record in records],
        marker="o",
        linewidth=2,
    )
    plt.title("疲劳度趋势图")
    plt.xlabel("日期")
    plt.ylabel("疲劳值")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.show()
