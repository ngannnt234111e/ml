from flask import Flask, request, render_template_string, send_file
from project_retail.project_retail.connectors.connector import Connector
from project_retail.project_retail.models.customer_clustering import (
    fetch_customer_features,
    kmeans_cluster,
    get_cluster_details,
    export_clusters_to_excel,
)

app = Flask(__name__)

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Customer Clusters</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 24px; }
        h1 { margin-bottom: 4px; }
        .meta { color: #555; margin-bottom: 16px; }
        table { border-collapse: collapse; margin-bottom: 24px; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background: #f3f3f3; }
        .cluster-title { margin-top: 24px; }
        .count { color: #333; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Customer Clusters</h1>
    <div class="meta">scenario={{ scenario }}, features={{ features|join(', ') }}, k={{ k }}, scale={{ scale }}</div>
    <p><a href="/download?k={{ k }}&scenario={{ scenario }}&scale={{ 'true' if scale else 'false' }}">Download Excel</a></p>
    {% for c in clusters %}
        <h2 class="cluster-title">Cluster {{ c.label }} — <span class="count">{{ c.count }}</span> customers</h2>
        {% if c.headers %}
        <table>
            <thead>
                <tr>
                    {% for h in c.headers %}<th>{{ h }}</th>{% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in c.rows %}
                    <tr>
                        {% for h in c.headers %}<td>{{ row[h] }}</td>{% endfor %}
                    </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>(no rows)</p>
        {% endif %}
    {% endfor %}
</body>
</html>
"""


def _assemble_cluster_view(details_dict):
    clusters = []
    for label in sorted(details_dict.keys()):
        df = details_dict[label]
        if df is None or df.empty:
            clusters.append({"label": label, "count": 0, "headers": [], "rows": []})
        else:
            headers = list(df.columns)
            rows = [dict(zip(headers, map(lambda x: x, row))) for row in df.values]
            clusters.append({"label": label, "count": len(df), "headers": headers, "rows": rows})
    return clusters


@app.route("/")
def clusters_page():
    # inputs
    k = int(request.args.get("k", 4))
    scenario = request.args.get("scenario", "2d")  # '2d' or '3d'
    scale = request.args.get("scale", "false").lower() == "true"

    # features by scenario
    if scenario == "3d":
        feature_cols = ['Age', 'Annual Income', 'Spending Score']
    else:
        feature_cols = ['Age', 'Spending Score']

    # db connect
    conn = Connector(database="salesdatabase")
    conn.connect()
    df_features = fetch_customer_features(conn)
    labels, _model, _X = kmeans_cluster(df_features, feature_cols, n_clusters=k, scale=scale)
    df_features = df_features.copy()
    df_features['cluster'] = labels
    details = get_cluster_details(conn, df_features)

    clusters = _assemble_cluster_view(details)
    return render_template_string(PAGE_TEMPLATE, clusters=clusters, features=feature_cols, k=k, scale=scale, scenario=scenario)


@app.route("/download")
def download_excel():
    # inputs
    k = int(request.args.get("k", 4))
    scenario = request.args.get("scenario", "2d")  # '2d' or '3d'
    scale = request.args.get("scale", "false").lower() == "true"

    # features by scenario
    if scenario == "3d":
        feature_cols = ['Age', 'Annual Income', 'Spending Score']
    else:
        feature_cols = ['Age', 'Spending Score']

    # db connect and build details
    conn = Connector(database="salesdatabase")
    conn.connect()
    df_features = fetch_customer_features(conn)
    labels, _model, _X = kmeans_cluster(df_features, feature_cols, n_clusters=k, scale=scale)
    df_features = df_features.copy()
    df_features['cluster'] = labels
    details = get_cluster_details(conn, df_features)

    # write to memory and return
    from io import BytesIO
    buffer = BytesIO()
    export_clusters_to_excel(details, buffer)
    buffer.seek(0)
    filename = f"customer_clusters_{scenario}_k{k}.xlsx"
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":
    # Default dev server
    app.run(host="127.0.0.1", port=5000, debug=True)