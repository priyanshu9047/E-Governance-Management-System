"""
Analytics & Report Generation Module.
Uses matplotlib and pandas to generate visual reports from the database.
"""

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt
import pandas as pd
import os


def generate_status_pie_chart(data: list, output_path: str) -> str:
    """
    Generate a pie chart of application status distribution.

    Parameters
    ----------
    data : list of dicts with keys 'status' and 'count'
    output_path : path to save the chart image

    Returns
    -------
    str : path to the saved chart
    """
    df = pd.DataFrame(data)
    colors = {
        "Submitted": "#3b82f6",
        "Under Review": "#f59e0b",
        "Documents Verified": "#8b5cf6",
        "Approved": "#10b981",
        "Rejected": "#ef4444",
        "Returned": "#f97316",
    }

    chart_colors = [colors.get(s, "#6b7280") for s in df["status"]]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        df["count"],
        labels=df["status"],
        autopct="%1.1f%%",
        colors=chart_colors,
        startangle=90,
        pctdistance=0.85,
    )
    ax.set_title("Application Status Distribution", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def generate_department_bar_chart(data: list, output_path: str) -> str:
    """
    Generate a grouped bar chart of department-wise application breakdown.

    Parameters
    ----------
    data : list of dicts with keys 'department_name', 'approved', 'rejected', 'pending'
    output_path : path to save the chart image

    Returns
    -------
    str : path to the saved chart
    """
    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(12, 6))

    x = range(len(df))
    width = 0.2

    ax.bar([i - width for i in x], df["approved"], width, label="Approved", color="#10b981")
    ax.bar(x, df["pending"], width, label="Pending", color="#f59e0b")
    ax.bar([i + width for i in x], df["rejected"], width, label="Rejected", color="#ef4444")

    ax.set_xlabel("Department")
    ax.set_ylabel("Number of Applications")
    ax.set_title("Department-wise Application Breakdown", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(df["department_name"], rotation=45, ha="right")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def generate_monthly_trend_chart(data: list, output_path: str) -> str:
    """
    Generate a line chart of monthly application trends.

    Parameters
    ----------
    data : list of dicts with keys 'month' and 'applications_count'
    output_path : path to save the chart image

    Returns
    -------
    str : path to the saved chart
    """
    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["month"], df["applications_count"], marker="o", linewidth=2,
            color="#667eea", markerfacecolor="#764ba2", markersize=8)
    ax.fill_between(df["month"], df["applications_count"], alpha=0.1, color="#667eea")
    ax.set_xlabel("Month")
    ax.set_ylabel("Applications")
    ax.set_title("Monthly Application Trend", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def generate_full_report(stats: dict, dept_data: list, ranking_data: list, monthly_data: list, output_dir: str) -> dict:
    """
    Generate a full analytics report with multiple charts.

    Returns
    -------
    dict : paths to all generated charts
    """
    os.makedirs(output_dir, exist_ok=True)

    charts = {}

    # Summary text report
    report_path = os.path.join(output_dir, "report_summary.txt")
    with open(report_path, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("E-GOVERNANCE SYSTEM — ANALYTICS REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Applications  : {stats.get('total_applications', 0)}\n")
        f.write(f"Approved            : {stats.get('approved', 0)}\n")
        f.write(f"Rejected            : {stats.get('rejected', 0)}\n")
        f.write(f"Pending             : {stats.get('pending', 0)}\n")
        f.write(f"Under Review        : {stats.get('under_review', 0)}\n")
        f.write(f"Avg Processing Days : {stats.get('avg_processing_days', 'N/A')}\n\n")

        if ranking_data:
            f.write("SERVICE POPULARITY RANKING\n")
            f.write("-" * 40 + "\n")
            for r in ranking_data:
                f.write(f"  #{r.get('popularity_rank', 'N/A')}  {r['service_name']} — {r['total_applications']} applications\n")

    charts["summary"] = report_path

    return charts
