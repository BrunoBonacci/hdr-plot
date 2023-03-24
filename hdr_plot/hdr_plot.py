#
# hdr-plot.py - A simple HdrHistogram plotting script.
# Copyright © 2018 - 2023 Bruno Bonacci - Distributed under the Apache License v 2.0
#
# usage: hdr-plot [-h] [--output OUTPUT] [--title TITLE] [--nosummary] [--noversion] [--units UNITS] [--percentiles-range-max PERCENTILES_RANGE_MAX] [--summary-fields SUMMARY_FIELDS] files [files ...]
#
# A standalone plotting script for https://github.com/giltene/wrk2 and
#  https://github.com/HdrHistogram/HdrHistogram.
#
# This is just a quick and unsophisticated script to quickly plot the
# HdrHistograms directly from the output of `wkr2` benchmarks.
#
#
import argparse
import re
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pkg_resources

#
# parsing and plotting functions
#

regex = re.compile(r'\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)')
mean_stddev_regex = re.compile(r'#\[Mean(?:\s+)=(?:\s+)([0-9.]+),(?:\s+)StdDeviation(?:\s+)=(?:\s+)([0-9.]+)')
max_totalcount_regex = re.compile(r'#\[Max(?:\s+)=(?:\s+)([0-9.]+),(?:\s+)Total count(?:\s+)=(?:\s+)([0-9.]+)')
filename = re.compile(r'(.*/)?([^.]*)(\.\w+\d+)?')

def parse_percentiles( file ):
    lines       = [ line for line in open(file) if re.match(regex, line)]
    values      = [ re.findall(regex, line)[0] for line in lines]
    pctles      = [ (float(v[0]), float(v[1]), int(v[2]), float(v[3])) for v in values]
    percentiles = pd.DataFrame(pctles, columns=['Latency', 'Percentile', 'TotalCount', 'inv-pct'])
    return percentiles

def parse_metadata( file ):
    mean_stddev_line = [ line for line in open(file) if re.match(mean_stddev_regex, line) ][0]
    max_totalcount_line = [ line for line in open(file) if re.match(max_totalcount_regex, line) ][0]
    mean_stddev = re.findall(mean_stddev_regex, mean_stddev_line)
    max_totalcount = re.findall(max_totalcount_regex, max_totalcount_line)
    return {
        'Mean': mean_stddev[0][0],
        'StdDeviation': mean_stddev[0][1],
        'Max': max_totalcount[0][0],
        'Total count': max_totalcount[0][1]
    }

def parse_pct_files( files ):
    return [ parse_percentiles(file) for file in files ]

def parse_metadata_files( files ):
    return [ parse_metadata(file) for file in files ]

def info_text(name, data, metadata, units, summary_fields):
    delimiter = '---------------------'
    unit = units['shorthand']
    min = data['Latency'].min()
    mean = float(metadata['Mean'])
    median = float((data.iloc[(data['Percentile'] - 0.5).abs().argsort()[:1]]['Latency']).iloc[0])
    max = data['Latency'].max()

    def get_percentile_latency(percentile):
        df = (data.loc[data['Percentile'] >= percentile]['Latency'])
        if not df.empty:
            return df.iloc[0]
        else:
            return 0.0

    percentiles = {
        'p50': 0.50,
        'p90': 0.90,
        'p99': 0.99,
        'p999': 0.999,
        'p9999': 0.9999,
        'p99999': 0.99999,
        'p999999': 0.999999,
        'p9999999': 0.9999999,
        'p99999999': 0.99999999,
        'p999999999': 0.999999999
    }

    info_values = {
        'min': min,
        'mean': mean,
        'median': median,
        'max': max
    }

    for k, v in percentiles.items():
        info_values[k] = get_percentile_latency(v)

    textstr = f'{name}\n{delimiter}\n'
    for f in summary_fields:
        padding = 9 - len(f)
        textstr += f'{f}{" "*padding}= {info_values[f]:>7.2f} {unit}\n'
    return textstr

def info_box(ax, text, x):
    props = dict(boxstyle='round', facecolor='lightcyan', alpha=0.5)

    # place a text box in upper left in axes coords
    t = ax.text(x, 0.95, text, transform=ax.transAxes,
            verticalalignment='top', bbox=props, fontname='monospace')

    return t


def plot_summarybox(fig, ax, percentiles, metadata, labels, units, summary_fields):
    # add info box to the side
    if len(labels) < 5:
        textstr = '\n'.join([info_text(labels[i], percentiles[i], metadata[i], units, summary_fields) for i in range(len(labels))])
        info_box(ax, textstr, 0.02)
    else:
        textstr1 = '\n'.join([info_text(labels[i], percentiles[i], metadata[i], units, summary_fields) for i in range(4)])
        textstr2 = '\n'.join([info_text(labels[i], percentiles[i], metadata[i], units, summary_fields) for i in range(4, len(labels))])

        box1 = info_box(ax, textstr1, 0.01)

        # align the second box next to the first one by retrieving its width
        box1_dimensions = box1.get_window_extent(renderer=fig.canvas.get_renderer())
        box1_edge = box1_dimensions.x1, 0
        box2_edge_axes_coords = ax.transAxes.inverted().transform(box1_edge)
        info_box(ax, textstr2, box2_edge_axes_coords[0] + 0.01)


def plot_percentiles(percentiles, labels, units, percentiles_range_max):
    fig, ax = plt.subplots(figsize=(16, 8))
    plt.rc('font', size=8)
    plt.rc('figure', titlesize=12)
    plt.rc('axes', titlesize=10)

    max_percentile = float("0." + percentiles_range_max.replace('.', ''))

    # plot values
    for data in percentiles:
        ax.plot(data['Percentile'], data['Latency'])

    # percentiles
    all_percentiles = [0.25, 0.5, 0.9, 0.99, 0.999, 0.9999, 0.99999, 0.999999, 0.9999999, 0.99999999, 0.999999999]
    all_percentile_labels = ["25%", "50%", "90%", "99%", "99.9%", "99.99%", "99.999%", "99.9999%",  "99.99999%",  "99.999999%",  "99.9999999%"]
    percentiles_max_index = all_percentiles.index(max_percentile)

    # set axis and legend
    unit = units['name']
    ax.grid()
    ax.set(xlabel='Percentile',
           ylabel=f'Latency ({unit})',
           title='Latency Percentiles (lower is better)')
    ax.set_xscale('logit')
    plt.xticks(all_percentiles[0:percentiles_max_index + 1])
    plt.xlim([0, max_percentile])
    majors = all_percentile_labels[0:percentiles_max_index + 1]
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(majors))
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    plt.legend(bbox_to_anchor=(0.125, 0.01, 1, 0.102), bbox_transform=fig.transFigure, loc=3, ncol=2,
               borderaxespad=0, labels=labels)
    # make room for the legend
    plt.subplots_adjust(bottom=0.11)
    return fig, ax


def arg_parse():
    parser = argparse.ArgumentParser(description='Plot HDRHistogram latencies.')
    parser.add_argument('files', nargs='+', help='List HDR files to plot')
    parser.add_argument('--output', default='latency.png',
                        help='Output file name (default: latency.png)')
    parser.add_argument('--title', default='', help='The plot title')
    parser.add_argument("--nosummary", help='Do not plot the summary box',
                        action="store_true")
    parser.add_argument("--noversion", help='Does not plot the version of hdr-plot',
                        action="store_true")
    parser.add_argument('--units', default='ms', help='The latency units (ns, us, ms)')
    parser.add_argument('--percentiles-range-max', default='99.9999', help='The maximum value of the percentiles range, e.g. 99.9999 (i.e. how many nines to display)')
    parser.add_argument('--summary-fields', default='median,p999,p9999,max', help='List of fields to show in the summary box. A comma-separated list of: min, max, mean, median, p50, p90, p99, p999, p9999, ..., p999999. Default: median,p999,p9999,max')

    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    return args


def main():
    # print command line arguments
    args = arg_parse()

    supported_units = {
        "ns": "nanoseconds",
        "us": "microseconds",
        "ms": "milliseconds"
    }

    units = {
        "name": supported_units[args.units],
        "shorthand": args.units
    }

    # load the data and create the plot
    pct_data = parse_pct_files(args.files)
    metadata = parse_metadata_files(args.files)
    labels = [re.findall(filename, file)[0][1] for file in args.files]
    # plotting data
    fig, ax = plot_percentiles(pct_data, labels, units, args.percentiles_range_max)
    # plotting summary box
    if not args.nosummary:
        plot_summarybox(fig, ax, pct_data, metadata, labels, units, args.summary_fields.split(','))
    # add title
    plt.suptitle(args.title)
    if not args.noversion:
        # add version
        version = pkg_resources.require("hdr-plot")[0].version
        fig.text(0.812, 0.035, f'plotted by hdr-plot v{version}', horizontalalignment='left', color='grey')
    # save image
    plt.savefig(args.output)
    print("Wrote: " + args.output)


# for testing
if __name__ == "__main__":
    main()
