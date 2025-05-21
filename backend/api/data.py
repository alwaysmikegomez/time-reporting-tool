# backend/api/data.py
from flask import Blueprint, request, jsonify, current_app
from backend.extensions import cache
from backend.sheets import list_client_tabs, fetch_planned_hours
from backend.harvest import fetch_time_entries

bp = Blueprint('data', __name__)

@bp.route('/data')
def get_data():
    start_s = request.args.get('start')
    end_s   = request.args.get('end')
    client  = request.args.get('client')
    refresh = request.args.get('refresh') == '1'

    # 1) Validate the client/tab name
    valid = list_client_tabs()
    if client not in valid:
        return (
            jsonify({
                "error": f"Invalid client: {client!r}",
                "valid_clients": valid
            }),
            400
        )

    # 2) If refresh=1, clear the specific cached entries for this date‐range + client
    if refresh:
        current_app.logger.debug(f"[get_data] refresh=1, clearing cache for {client}")
        cache.delete_memoized(fetch_planned_hours, start_s, end_s, client)
        cache.delete_memoized(fetch_time_entries, start_s, end_s)

    # 3) Call the helpers (will use cache or refetch if needed)
    planned_df      = fetch_planned_hours(start_s, end_s, client)
    actual_entries  = fetch_time_entries(start_s, end_s)

    # 4) Merge planned vs actual into a date → {planned, actual} map
    data_by_date = {}
    for row in planned_df.to_dict(orient='records'):
        date = row['Date'].strftime('%Y-%m-%d')
        data_by_date.setdefault(date, {})['planned'] = row['Hours']

    for entry in actual_entries:
        date  = entry['spent_date']
        hours = entry['hours']
        data_by_date.setdefault(date, {})['actual'] = data_by_date[date].get('actual', 0) + hours

    # 5) Convert to a sorted list of {date, planned, actual}
    response = []
    for date in sorted(data_by_date):
        response.append({
            'date':    date,
            'planned': data_by_date[date].get('planned', 0),
            'actual':  data_by_date[date].get('actual', 0),
        })

    return jsonify(response)
