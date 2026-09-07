"""
aws_costs_dashboard.py - Real-time AWS token usage and cost tracker.
Shows token counts per model, total cost, and $200 credit remaining.
"""
import boto3
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

REGION = "us-east-1"
CREDIT_BALANCE = 200.00  # $200/6-month free-tier credit

# Per-model token pricing (USD per 1M tokens) - as of Sep 2026
# Source: AWS Bedrock pricing
PRICING = {
    "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.25, "output": 1.25},
    "anthropic.claude-3-5-haiku-20241022-v2:0": {"input": 0.80, "output": 4.00},
    "anthropic.claude-3-5-sonnet-20240620-v1:0": {"input": 3.00, "output": 15.00},
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {"input": 3.00, "output": 15.00},
    "anthropic.claude-sonnet-4-20250514-v1:0": {"input": 3.00, "output": 15.00},
    "anthropic.claude-haiku-4-5-20251001-v1:0": {"input": 1.00, "output": 5.00},
    "anthropic.claude-opus-4-1-20250805-v1:0": {"input": 15.00, "output": 75.00},
    "anthropic.claude-opus-4-5-20251101-v1:0": {"input": 5.00, "output": 25.00},
}
DEFAULT_PRICING = {"input": 3.00, "output": 15.00}  # Sonnet-like fallback


def get_caller_identity():
    """Verify AWS credentials are configured."""
    try:
        sts = boto3.client("sts", region_name=REGION)
        identity = sts.get_caller_identity()
        return identity.get("Account", "Unknown"), identity.get("Arn", "Unknown")
    except Exception as e:
        return None, str(e)


def get_bedrock_metrics(days_back=7):
    """Get Bedrock token metrics from CloudWatch."""
    cw = boto3.client("cloudwatch", region_name=REGION)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days_back)

    metrics_by_model = {}
    metric_names = ["InputTokenCount", "OutputTokenCount", "InvocationCount"]

    for metric_name in metric_names:
        try:
            response = cw.get_metric_statistics(
                Namespace="AWS/Bedrock",
                MetricName=metric_name,
                Dimensions=[{"Name": "ModelId", "Value": "*"}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"],
            )
            for dp in response.get("Datapoints", []):
                dims = dp.get("Dimensions", {})
                model_id = dims.get("ModelId", "unknown")
                if model_id not in metrics_by_model:
                    metrics_by_model[model_id] = {}
                metrics_by_model[model_id][metric_name] = dp.get("Sum", 0)
        except Exception as e:
            print(f"  ⚠️  Could not fetch {metric_name}: {e}")
            return None

    return metrics_by_model


def calculate_cost(metrics_by_model):
    """Calculate cost per model based on token usage and pricing."""
    costs = {}
    for model_id, metrics in metrics_by_model.items():
        pricing = PRICING.get(model_id, DEFAULT_PRICING)
        input_tokens = metrics.get("InputTokenCount", 0)
        output_tokens = metrics.get("OutputTokenCount", 0)
        invocations = metrics.get("InvocationCount", 0)

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        costs[model_id] = {
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "total_tokens": int(input_tokens + output_tokens),
            "invocations": int(invocations),
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
        }
    return costs


def get_cost_explorer_total():
    """Get MTD cost from Cost Explorer (requires root account to enable)."""
    try:
        ce = boto3.client("ce", region_name="us-east-1")
        today = datetime.now(timezone.utc)
        first_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        response = ce.get_cost_and_usage(
            TimePeriod={
                "Start": first_of_month.strftime("%Y-%m-%d"),
                "End": today.strftime("%Y-%m-%d"),
            },
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            Filter={"Dimensions": {"Key": "SERVICE", "Values": ["Amazon Bedrock"]}},
        )
        results = response.get("ResultsByTime", [])
        if results:
            return float(results[0]["Total"]["UnblendedCost"]["Amount"])
    except Exception as e:
        return None
    return 0.0


def print_dashboard():
    """Print the full AWS cost dashboard."""
    print("=" * 70)
    print("AWS BEDROCK USAGE & COST DASHBOARD")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Identity
    print("\n[ACCOUNT]")
    account, arn = get_caller_identity()
    if account:
        print(f"  Account: {account}")
        print(f"  User:    {arn.split('/')[-1] if '/' in arn else arn}")
        print(f"  Region:  {REGION}")
    else:
        print(f"  ❌ {arn}")
        return

    # CloudWatch metrics
    print("\n[CLOUDWATCH METRICS] - Last 7 days, grouped by ModelId")
    print("-" * 70)
    print(f"  {'Model':<48s} {'In Tok':>10s} {'Out Tok':>10s} {'Calls':>6s}")
    print("-" * 70)
    metrics = get_bedrock_metrics(days_back=7)
    if metrics:
        total_in = 0
        total_out = 0
        total_calls = 0
        for model_id, m in sorted(metrics.items()):
            in_tok = int(m.get("InputTokenCount", 0))
            out_tok = int(m.get("OutputTokenCount", 0))
            calls = int(m.get("InvocationCount", 0))
            # Truncate long model names
            display_name = model_id
            if len(display_name) > 46:
                display_name = display_name[:43] + "..."
            print(f"  {display_name:<48s} {in_tok:>10,} {out_tok:>10,} {calls:>6,}")
            total_in += in_tok
            total_out += out_tok
            total_calls += calls
        print("-" * 70)
        print(f"  {'TOTAL':<48s} {total_in:>10,} {total_out:>10,} {total_calls:>6,}")
    else:
        print("  No data (Bedrock not used in last 7 days, or quota issues)")
    print()

    # Cost breakdown
    print("[COST BREAKDOWN] - Calculated from token usage × model pricing")
    print("-" * 70)
    print(f"  {'Model':<48s} {'Input $':>10s} {'Output $':>10s} {'Total $':>10s}")
    print("-" * 70)
    if metrics:
        total_cost = 0.0
        for model_id, m in sorted(metrics.items()):
            costs = calculate_cost({model_id: m})[model_id]
            display_name = model_id
            if len(display_name) > 46:
                display_name = display_name[:43] + "..."
            print(f"  {display_name:<48s} ${costs['input_cost']:>9.4f} ${costs['output_cost']:>9.4f} ${costs['total_cost']:>9.4f}")
            total_cost += costs['total_cost']
        print("-" * 70)
        print(f"  {'TOTAL (from CloudWatch tokens)':<48s} ${total_cost:>9.4f}")
    print()

    # Cost Explorer (real billing)
    print("[COST EXPLORER] - Real billing data (requires root account enable)")
    print("-" * 70)
    ce_cost = get_cost_explorer_total()
    if ce_cost is not None:
        print(f"  Month-to-date unblended cost: ${ce_cost:.4f}")
    else:
        print("  ⚠️  AccessDeniedException - Cost Explorer not enabled at account level")
        print("     Fix: AWS Console → Billing → Cost Explorer → Enable")
    print()

    # Credit tracking
    print("[CREDIT TRACKING]")
    print("-" * 70)
    cloudwatch_cost = sum(
        calculate_cost({m: data})[m]["total_cost"]
        for m, data in (metrics or {}).items()
    )
    primary_cost = ce_cost if ce_cost is not None else cloudwatch_cost

    used_pct = (primary_cost / CREDIT_BALANCE) * 100
    remaining = CREDIT_BALANCE - primary_cost

    print(f"  Credit allocation: ${CREDIT_BALANCE:.2f}")
    print(f"  Used:              ${primary_cost:.4f} ({used_pct:.2f}%)")
    print(f"  Remaining:         ${remaining:.4f}")

    if remaining < 0:
        print(f"  ⚠️  OVER CREDIT LIMIT by ${-remaining:.4f}")
    elif remaining < 20:
        print(f"  ⚠️  LOW CREDIT: less than $20 remaining")
    else:
        print(f"  ✓ Credit healthy")
    print()

    # Forecast
    if primary_cost > 0:
        days_in_month = (datetime.now(timezone.utc).replace(day=28) + timedelta(days=4)).day
        days_elapsed = datetime.now(timezone.utc).day
        if days_elapsed > 0:
            daily_rate = primary_cost / days_elapsed
            remaining_days = days_in_month - days_elapsed
            forecast = daily_rate * remaining_days
            print(f"[FORECAST] at current rate:")
            print(f"  Daily spend:   ${daily_rate:.4f}/day")
            print(f"  Month-end:     ${forecast:.4f} projected")
            print(f"  Credit lasts:  ~{int(CREDIT_BALANCE/daily_rate) if daily_rate > 0 else 9999} days")
    else:
        print("[FORECAST] No spend yet - you have the full $200 credit intact")

    print()
    print("=" * 70)


def main():
    print_dashboard()


if __name__ == "__main__":
    main()
