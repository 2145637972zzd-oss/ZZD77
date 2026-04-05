# app/utils/visualization.py
def get_trend_chart_config(x_data, y_data, title):
    return {
        "title": {"text": title, "left": "center"},
        "xAxis": {"type": "category", "data": x_data},
        "yAxis": {"type": "value"},
        "series": [{"data": y_data, "type": "line", "smooth": True}],
        "tooltip": {"trigger": "axis"}
    }

def get_pie_chart_config(labels, data, title):
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [{
            "name": "消费金额",
            "type": "pie",
            "radius": ["40%", "70%"],
            "data": [{"value": d, "name": l} for l, d in zip(labels, data)],
            "label": {"show": True, "position": "outside"}
        }]
    }

def get_bar_chart_config(x_data, y_data, title):
    return {
        "title": {"text": title, "left": "center"},
        "xAxis": {"type": "category", "data": x_data},
        "yAxis": {"type": "value", "name": "消费次数"},
        "series": [{"data": y_data, "type": "bar"}],
        "tooltip": {"trigger": "axis"}
    }