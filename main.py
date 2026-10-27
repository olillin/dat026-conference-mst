import graphviz as gv
import graph

vertex_list = [
    # Lunch
    {"col": 0, "t": "14:00-14:25"},
    {"col": 0, "t": "14:25-14:50"},
    {"col": 1, "t": "14:00-14:30"},
    {"col": 1, "t": "14:30-15:00"},
    {"col": 2, "t": "14:00-14:12"},
    {"col": 2, "t": "14:12-14:24"},
    {"col": 2, "t": "14:24-14:36"},
    {"col": 2, "t": "14:36-14:48"},
    {"col": 2, "t": "14:48-15:00"},
    {"col": 3, "t": "14:00-14:15"},
    {"col": 3, "t": "14:15-14:30"},
    {"col": 3, "t": "14:30-15:00"},
    # Coffee break
    {"col": 0, "t": "15:30-15:55"},
    {"col": 0, "t": "15:55-16:20"},
    {"col": 1, "t": "15:30-16:00"},
    {"col": 1, "t": "16:00-16:30"},
    {"col": 2, "t": "15:30-16:30"},
    {"col": 3, "t": "15:30-15:45"},
    {"col": 3, "t": "15:45-16:15"},
    {"col": 3, "t": "16:15-16:45"},
]

# Units between each column
x_scale = 2
# Units between each minute
y_scale = 0.1
# Minutes to offset start and end by
margin = 20


def parse_time(t) -> tuple[int, int]:
    s, e = t.split("-")
    time_to_minutes = lambda time: (
        int(time.split(":")[0]) * 60 + int(time.split(":")[1])
    )
    return time_to_minutes(s), time_to_minutes(e)


def main():
    g = gv.Graph("mst_graph", engine="neato")
    g.attr(size="10,10", dpi="300")

    kruskal_graph = graph.Graph(len(vertex_list) + 2)

    schedule_start = min((parse_time(vd["t"])[0] for vd in vertex_list))
    schedule_end = max((parse_time(vd["t"])[1] for vd in vertex_list))
    columns = max((vd["col"] for vd in vertex_list))

    start_node = [
        "S",
        schedule_start - margin,
        schedule_start - margin,
        float(columns) / 2,
    ]
    end_node = ["E", schedule_end + margin, schedule_end + margin, float(columns) / 2]

    nodes = [start_node, end_node]

    node_to_index = lambda v: [node[0] for node in nodes].index(v)
    index_to_node = lambda i: nodes[i][0]

    for vi, vd in enumerate(vertex_list):
        v = str(vi)
        col, t = vd["col"], vd["t"]
        start, end = parse_time(t)
        nodes.append([v, start, end, col])

    edges = []
    for v, v_start, v_end, _ in nodes:
        for u, u_start, u_end, _ in nodes:
            if v == u:
                continue
            if u_start >= v_end:
                edges.append((v, u))

    adjacency = []
    for v, v_start, v_end, _ in nodes:
        before = 0
        after = 0
        for ve, ue in edges:
            if ve != v and ue != v:
                continue
            u = ve if ue == v else ue
            _, u_start, u_end, _ = nodes[node_to_index(u)]
            if u_end <= v_start:
                before += 1
            if u_start >= v_end:
                after += 1
        adjacency.append([before, after])

    weighted_edges = []
    for v, u in edges:
        vi = node_to_index(v)
        ui = node_to_index(u)
        earlier = ui if nodes[vi][1] > nodes[ui][1] else vi
        later = vi if nodes[vi][1] > nodes[ui][1] else ui
        weight = -(adjacency[earlier][0] + adjacency[later][1])
        kruskal_graph.add_edge(vi, ui, weight)
        weighted_edges.append((v, u, weight))

    mst_edges = kruskal_graph.kruskal_mst()
    path_nodes = graph.find_mst_path_nodes(mst_edges, 0, 1)

    for v, start, _, col in nodes:
        vi = node_to_index(v)
        x = col * x_scale
        y = (schedule_end - start + margin) * y_scale
        pos = f"{x},{y}!"
        is_mst = vi in path_nodes if path_nodes is not None else False
        g.node(
            v,
            pos=pos,
            shape="circle",
            style="filled",
            fillcolor="orange" if is_mst else "lightblue",
        )

    for v, u, weight in weighted_edges:
        vi = node_to_index(v)
        ui = node_to_index(u)
        is_mst = (vi, ui, weight) in mst_edges or (ui, vi, weight) in mst_edges
        g.edge(
            v,
            u,
            label=str(weight),
            fontcolor="black" if is_mst else "gray",
            penwidth="3.0" if is_mst else "1.0",
            color="orange" if is_mst else "lightgray",
            style="solid" if is_mst else "dashed",
        )

    output_path = g.render("mst_graph", format="png")
    print(f"Graph saved to {output_path}")


if __name__ == "__main__":
    main()
