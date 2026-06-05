import sqlite3
import pandas as pd
import geopandas as gpd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

def run_sql(database, query_file):
    with sqlite3.connect(database) as conn:
        conn.execute('pragma foreign_keys = on;')
        cursor = conn.cursor()

        with open(query_file, 'r') as qf:
            query = qf.read()
    
        return cursor.execute(query).fetchall()

def divide_range_into_buckets(no_buckets: int, 
                              range_min: float, 
                              range_max: float, 
                              values: pd.Series):
    """
    Divide numeric values into equal-width buckets over a closed interval.

    Values are assigned to integer bucket labels in the range
    [0, no_buckets - 1].

    The interval [range_min, range_max] is divided into
    `no_buckets` equal-width subintervals. Values equal to
    `range_max` are included in the top bucket.

    Parameters
    ----------
    no_buckets : int
        Number of equal-width buckets. Must be positive.

    range_min : float
        Lower bound of the interval.

    range_max : float
        Upper bound of the interval. Must be greater than
        `range_min`.

    values : pd.Series
        Numeric values to bucketize. All values must be
        non-missing and fall within the interval
        [range_min, range_max].

    Returns
    -------
    pd.Series
        Integer bucket labels corresponding to input values.
    list
        Boundaries of buckets.

    Raises
    ------
    ValueError
        If:
        - `no_buckets <= 0`
        - `range_min >= range_max`
        - values contain missing entries
        - values fall outside the specified interval
    """
    if no_buckets <= 0:
        raise ValueError(f"Expected positive number of buckets, got {no_buckets}")

    if range_min >= range_max:
        raise ValueError(f"Expected valid range, got [{range_min}, {range_max}]")

    if ((values < range_min) | (values > range_max)).any():
        raise ValueError(f"Values in series are outside the interval [{range_min}, {range_max}]")

    if values.isna().any():
        raise ValueError("Series contains missing entries.")

    
    bucket_size = (range_max - range_min) / no_buckets
    
    clusters = (values - range_min) // bucket_size
    # there would be an additional bucket when value == range_max
    # push values == range_max into the top bucket
    clusters.loc[clusters == no_buckets] = no_buckets - 1

    edges = [i * bucket_size for i in range(no_buckets + 1)]
    
    return clusters.astype(int), edges

def divide_range_into_Gaussian_buckets(
    values: pd.Series
):
    data = values.to_frame(name='val')
    
    mu = values.mean()
    sigma = values.std()

    # min, -3sd, -2sd, mean -1sd, mean + 1sd, mean + 2sd, mean + 3sd, max
    sigma_factors = np.concatenate((np.arange(-3, 0), np.arange(1, 4)))

    data['cluster'] = -1

    left = data['val'].min()
    edges = [left]
    for c, factor in enumerate(sigma_factors):
        right = mu + factor * sigma
        edges.append(right)
        data.loc[((data['val'] >= left) & (data['val'] < right)), 'cluster'] = c
        left = right
    
    right = data['val'].max()
    if right > left:
        edges.append(right)
        data.loc[((data['val'] >= left) & (data['val'] < right)), 'cluster'] = c + 1

    assert (data['cluster'] == -1).sum() == 0

    return data['cluster'], edges

def prepare_labels(edges, categories):
    labels = [
        (edges[i-1], edges[i] - 1) if i < len(edges) -1 
        else (edges[i-1], edges[i]) 
        for i in range(len(edges)) if i > 0
    ]
    labels = {i: f"{int(l[0])}–{int(l[1])}%" for (i, l) in enumerate(labels) if i in categories}
    return labels

def plot_cluster_map(
    cluster_series: pd.Series,
    labels: dict[int, str],
    palette: dict[int, str],
    projection: str = "ESRI:54048",
    title: str | None = None,
    legend_orientation: str  = 'vertical', # horizontal or vertical
    save_file_name: str | None = None
):
    """
    Plot a world choropleth map of categorical cluster assignments.

    Countries are colored according to cluster membership using a
    user-supplied categorical palette. Countries without available
    observations are shown separately using a hatched grey fill.

    Parameters
    ----------
    cluster_series : pd.Series
        Series mapping ISO3 country codes to integer cluster labels.
        The index is expected to contain ISO3 country codes matching
        the `SOV_A3` field of the Natural Earth dataset.

    labels : dict[int, str]
        Mapping from cluster identifier to legend label.

    palette : dict[int, str]
        Mapping from cluster identifier to color hex code.

    projection : str, default "ESRI:54030"
        CRS projection used for rendering the map.

    title : str, optional
        Figure title.

    legend_orientation : str, default 'vertical'
        Legend layout orientation. Currently only vertical layout
        is implemented.

    save_file_name : str, optional
        If provided, save the figure to this path.

    Notes
    -----
    - Uses the Natural Earth 1:10m country dataset.
    - Cluster identifiers are assumed to be integers.
    - Missing observations are displayed separately and are not
      expected in `labels` or `palette`.
    - The function displays and closes the matplotlib figure,
      making it suitable for repeated use inside loops.
    """
    # clusters are assumed to be integer
    # which isn't checked
    categories = np.sort(cluster_series.dropna().astype(int).unique())

    assert set(categories) <= set(labels.keys()), (
        f"Unlabeled categories found: {set(categories) - set(labels.keys())}"
    )

    assert set(categories) <= set(palette.keys()), (
        f"Categories lacking color in palette found: {set(categories) - set(palette.keys())}"
    )

    assert set(labels.keys()) == set(palette.keys()), (
        f"Clusters in labels and palette not equal"
    )

    world_file = '../data/raw/geodata/ne_10m_admin_0_countries.zip'

    # import world data to draw countries
    world = gpd.read_file(world_file)
    assert not world.empty
    
    # drop Antarctica
    world = world[world["CONTINENT"] != "Antarctica"].copy()

    # choose a projection
    world = world.to_crs(projection)

    # prepare dataframe for plotting
    world["_cluster"] = world["SOV_A3"].map(cluster_series)

    cmap = ListedColormap(
        [palette[c] for c in categories]
    )

    # plot
    figsize = (14, 6.5)
    background_color = "ghostwhite"
    
    border_color = "#E8E2D8"
    border_width = 0.5
    
    fig, ax = plt.subplots(figsize = figsize, facecolor = background_color)
    ax.set_facecolor(background_color)
    
    world.plot(
            ax = ax,
            column = '_cluster',
            categorical = True,
            cmap = cmap,
            missing_kwds = {
                "color": "lightgrey",
                "edgecolor": "darkgrey",
                "hatch": "///",
                "label": "Missing values",
            },
            edgecolor = border_color,
            linewidth = border_width
        )
    
    if title:
            ax.set_title(title, fontsize = 16, pad = 14)
    
    # prepare the legend: clusters
    handles = [
        mpatches.Patch(
            facecolor = palette[cat],
            edgecolor = "none",
            label = labels[int(cat)]
        )
        for cat in categories
    ]
    
    # prepare legend: missing values
    handles.append(
        mpatches.Patch(
            facecolor="lightgrey",
            edgecolor="darkgrey",
            hatch="///",
            label="Missing values"
        )
    )
    
    # vertical stacked legend
    ax.legend(
        handles = handles,
        loc = "lower left",
        frameon = False,
        fontsize = 14
    )
    
    '''
    # horizontal legend
    ax.legend(
        handles = handles,
        loc = 'lower center',
        bbox_to_anchor = (0.5, -0.08),
        ncol = len(categories) + 2,
        frameon = False,
        fontsize = 10,
        handlelength = 1.8,
        columnspacing = 1.4
    )
    '''
    # the pretty stuff
    ax.set_axis_off()
    
    # crop out Antarctica
    #ylim=(-6_000_000, 8_500_000)
    #ax.set_ylim(*ylim)
   
    # reduce empty space on the sides 
    #xlim = (-14_000_000, 16_000_000)
    #ax.set_xlim(*xlim)

    # force the axes to the projected world bounds
    xmin, ymin, xmax, ymax = world.total_bounds
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.margins(0)
    
    plt.tight_layout(pad = 0)

    if save_file_name:
        fig.savefig(
            save_file_name,
            dpi=300,
            bbox_inches="tight",
            facecolor=fig.get_facecolor()
        )
    
    plt.show()
    plt.close(fig)

def pretty_histogram(
                    data_column: pd.Series,
                    bins_no: int | None = None,
                    title: str | None = None,
                    x_axis_title: str | None = None,
                    y_axis_title: str | None = None,
                    annotation: dict | None = None,
                    save_file_name: str | None = None):
    '''
    Plot a histogram of a numeric variable.

    The number of bins may be specified explicitly 
    or determined automatically 
    using Matplotlib's default bin selection algorithm.

    Parameters
    ----------
    data_column : pd.Series
        Numeric data to be visualized.

    bins_no : int | None, default = None
        Number of histogram bins. If None, Matplotlib's
        automatic bin selection ('auto') is used.

    title : str | None, default = None
        Plot title.

    x_axis_title : str | None, default = None
        Label for the x-axis.

    y_axis_title : str | None, default = None
        Label for the y-axis.

    save_file_name : str | None, default = None
        Path where the figure should be saved. If None,
        the figure is displayed but not saved.

    Returns
    -------
    None
        Displays the histogram and optionally saves it to disk.
    '''
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    # put the grid behind the plot
    ax.set_axisbelow(True)

    # use bins when available
    bins = bins_no if bins_no is not None else 'auto'

    ax.hist(
        data_column,
        color = '#708A81',
        edgecolor = '#D2CCC3',
        linewidth = 0.5,
        bins = bins
    )

    # labels
    ax.set_title(
        title,
        fontsize=14,
        pad=12
    )
    
    ax.set_xlabel(
        x_axis_title,
        fontsize=11
    )
    
    ax.set_ylabel(
        y_axis_title,
        fontsize=11
    )

    # optional annotation
    if annotation:
        ax.annotate(**annotation)

    # styling
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    
    ax.grid(
        True,
        color = '#D2CCC3',
        linewidth = 0.8,
        alpha = 0.7,
    )

    # save the plot
    if save_file_name:
        plt.savefig(
            save_file_name,
            dpi = 300,
            bbox_inches = "tight"
        )

    plt.show()
    # prevent figures from accumulating in memory
    plt.close(fig)
