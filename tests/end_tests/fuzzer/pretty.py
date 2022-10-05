import json

from bokeh import io as bokeh_io
from bokeh.io import curdoc
from bokeh.layouts import gridplot
from bokeh.models import (
    ColumnDataSource,
    CrosshairTool,
    LinearAxis,
    NumeralTickFormatter,
    Range1d,
)
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure, output_file


def _build_figure(plot_height=300, xaxis=False, **kwargs):
    result = figure(plot_width=1300, plot_height=plot_height, tools="xpan,xwheel_zoom", **kwargs)
    result.xaxis.visible = xaxis

    return result


def _compute_source(filename):

    with open(filename, "r", encoding="utf-8") as f:
        raw_data = [{stat["name"]: stat for stat in item["docker_stats"]} for item in json.load(f)]

    container_names = raw_data[0].keys()

    data = dict(
        x=range(len(raw_data)),
    )

    for name in container_names:
        data[f"{name}_mem"] = [item[name]["memory_stats"]["usage"] for item in raw_data]

        # https://stackoverflow.com/questions/30271942/get-docker-container-cpu-usage-as-percentage
        previous_cpu, previous_cpu_system = 0, 0
        cpu_percent = []
        for item in raw_data:
            cpu_stats = item[name]["cpu_stats"]

            cpu_delta = cpu_stats["cpu_usage"]["total_usage"] - previous_cpu
            system_delta = cpu_stats["system_cpu_usage"] - previous_cpu_system

            if system_delta > 0.0 and cpu_delta > 0.0:
                cpu_percent.append((cpu_delta / system_delta) * cpu_stats["online_cpus"])
            else:
                cpu_percent.append(0)

            previous_cpu, previous_cpu_system = cpu_stats["cpu_usage"]["total_usage"], cpu_stats["system_cpu_usage"]

        data[f"{name}_cpu"] = cpu_percent

    return ColumnDataSource(data=data)


def _build_container_graph(source, containers, x_range=None):
    graph = _build_figure(x_range=x_range)
    # mem_graph.add_tools(HoverTool(tooltips=[("#", "$index"), ("Memory", "@memory")]))

    colors = ("blue", "green", "red")

    graph.extra_y_ranges = {"cpu": Range1d(start=0, end=1)}

    mem_values = []
    for i, container in enumerate(containers):

        mem_source = f"/flask-camp-{container}_mem"
        mem_values += source.data[mem_source]

        graph.line(
            "x",
            mem_source,
            legend_label=f"Memory {container}",
            line_width=2,
            line_color=colors[i],
            source=source,
        )

        graph.line(
            "x",
            f"/flask-camp-{container}_cpu",
            legend_label=f"CPU {container}",
            line_width=2,
            line_dash="dashed",
            line_color=colors[i],
            source=source,
            y_range_name="cpu",
        )

    graph.add_layout(LinearAxis(y_range_name="cpu"), "right")
    graph.y_range = Range1d(start=min(mem_values) * 0.9, end=max(mem_values) * 1.1)
    graph.yaxis[0].formatter = NumeralTickFormatter(format="0 b")
    graph.yaxis[1].formatter = NumeralTickFormatter(format="0%")

    return graph


def _add_crosshair(figures):
    js_move = """
    var start = fig.x_range.start;
    var end = fig.x_range.end;

    if(cb_obj.x>=start && cb_obj.x<=end && cb_obj.y>=start && cb_obj.y<=end) {
        cross.spans.height.computed_location=cb_obj.sx;
    } else {
        cross.spans.height.computed_location = null;
    }
    """

    crosshair = CrosshairTool(dimensions="height", line_color="lightgrey")

    for main_figure in list(figures):
        main_figure.add_tools(crosshair)
        for other_figure in figures:
            if other_figure != main_figure:
                callback = CustomJS(args={"cross": crosshair, "fig": other_figure}, code=js_move)
                main_figure.js_on_event("mouseenter", callback)


def main(filename="logs/docker_stats.json"):
    source = _compute_source(filename)

    haproxy_graph = _build_container_graph(source, ("haproxy-1",))

    figures = (
        haproxy_graph,
        _build_container_graph(source, ("app-1", "app-2", "app-3"), x_range=haproxy_graph.x_range),
        _build_container_graph(source, ("redis-1",), x_range=haproxy_graph.x_range),
        _build_container_graph(source, ("pg-1",), x_range=haproxy_graph.x_range),
    )

    _add_crosshair(figures)

    figures = [(figure,) for figure in figures]
    grid = gridplot(figures, toolbar_location="right")
    curdoc().theme = "dark_minimal"
    output_file(filename + ".html")
    bokeh_io.save(grid)
    bokeh_io.show(grid)


if __name__ == "__main__":
    main()
