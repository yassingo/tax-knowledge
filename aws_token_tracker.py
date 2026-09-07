"""
aws_token_tracker.py - Track AWS Bedrock token usage and costs.

Uses boto3 to:
1. Query CloudWatch metrics for Bedrock (InputTokenCount, OutputTokenCount, InvocationCount)
2. Query Cost Explorer for month-to-date Bedrock costs
3. Track against $200 credit balance
"""
import boto3
import json
from datetime import datetime, timedelta, timezone

REGION = "us-east-1"
CREDIT_BALANCE = 200.00  # $200 credit allocation

# CloudWatch metrics to query
METRICS = ["InputTokenCount", "OutputTokenCount", "InvocationCount"]
NAMESPACE = "AWS/Bedrock"

def get_bedrock_metrics(days_back=7):
    """Query CloudWatch for Bedrock metrics grouped by ModelId."""
    cw = boto3.client("cloudwatch", region_name=REGION)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days_back)

    results = {}
    for metric_name in METRICS:
        try:
            response = cw.get_metric_statistics(
                Namespace=NAMESPACE,
                MetricName=metric_name,
                Dimensions=[{"Name": "ModelId", "Value": "*"}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=["Sum"],
            )
            datapoints = response.get("Datapoints", [])
            # Group by ModelId
            for dp in datapoints:
                model_id = dp.get("Dimensions", {}).get("ModelId", "unknown")
                if model_id not in results:
                    results[model_id] = {}
                results[model_id][metric_name] = dp.get("Sum", 0)
        except Exception as e:
            print(f"Error querying {metric_name}: {e}")

    return results

def get_bedrock_cost():
    """Get month-to-date unblended cost for AWS Bedrock via Cost Explorer."""
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
            Filter={
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": ["Amazon Bedrock"],
                }
            },
        )
        results = response.get("ResultsByTime", [])
        if results:
            return float(results[0]["Total"]["UnblendedCost"]["Amount"])
    except Exception as e:
        print(f"Error querying Cost Explorer: {e}")
    return 0.0

def display_status(metrics, cost):
    """Display a formatted status report."""
    print("=" * 70)
    print("AWS BEDROCK USAGE & COST TRACKER")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    print(f"\n[COST EXPLORER] Month-to-date unblended cost for Amazon Bedrock:")
    print(f"  ${cost:.4f} USD")

    remaining = CREDIT_BALANCE - cost
    pct_used = (cost / CREDIT_BALANCE) * 100
    print(f"\n[CREDIT BALANCE]")
    print(f"  Credit allocation: ${CREDIT_BALANCE:.2f}")
    print(f"  Used:             ${cost:.4f} ({pct_used:.2f}%)")
    print(f"  Remaining:        ${remaining:.4f}")

    if remaining < 0:
        print(f"  ⚠️  OVER CREDIT LIMIT by ${-remaining:.4f}")
    elif remaining < 20:
        print(f"  ⚠️  LOW CREDIT: < $20 remaining")
    else:
        print(f"  ✓ Credit healthy")

    print(f"\n[CLOUDWATCH METRICS] Last 7 days, by ModelId:")
    if not metrics:
        print("  No metrics returned (may be throttled or no usage yet)")
    else:
        for model_id, m in metrics.items():
            in_tok = m.get("InputTokenCount", 0)
            out_tok = m.get("OutputTokenCount", 0)
            invocations = m.get("InvocationCount", 0)
            total = in_tok + out_tok
            print(f"\n  {model_id}:")
            print(f"    Input tokens:  {int(in_tok):,}")
            print(f"    Output tokens: {int(out_tok):,}")
            print(f"    Total tokens:  {int(total):,}")
            print(f"    Invocations:   {int(invocations):,}")

    print("\n" + "=" * 70)

def main():
    print("Fetching Bedrock metrics and costs from AWS...")
    metrics = get_bedrock_metrics(days_back=7)
    cost = get_bedrock_cost()
    display_status(metrics, cost)

    # Save to JSON for later use
    report = {
        "generated_at": datetime.now().isoformat(),
        "credit_balance": CREDIT_BALANCE,
        "mtd_cost_usd": cost,
        "remaining_credit_usd": CREDIT_BALANCE - cost,
        "pct_used": (cost / CREDIT_BALANCE) * 100,
        "metrics_by_model": metrics,
    }
    with open(r"C:\Users\LENOVO\tag-rag\aws_usage_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nReport saved to aws_usage_report.json")

if __name__ == "__main__":
    main()
