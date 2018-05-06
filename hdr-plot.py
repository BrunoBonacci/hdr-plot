#!/usr/bin/env python3

import argparse
import re
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


#
# parsing and plotting functions
#

regex = re.compile(r'\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)')
filename = re.compile(r'(.*/)?([^.]*)(\.\w+\d+)?')

def parse_percentiles( file ):
    lines       = [ line for line in open(file) if re.match(regex, line)]
    values      = [ re.findall(regex, line)[0] for line in lines]
    pctles      = [ (float(v[0]), float(v[1]), int(v[2]), float(v[3])) for v in values]
    percentiles = pd.DataFrame(pctles, columns=['Latency', 'Percentile', 'TotalCount', 'inv-pct'])
    return percentiles


def parse_files( files ):
    return [ parse_percentiles(file) for file in files]


def plot_percentiles( percentiles, labels ):
    fig, ax = plt.subplots(figsize=(16,8))
    # plot values
    for data in percentiles:
        ax.plot(data['Percentile'], data['Latency'])

    # set axis and legend
    ax.grid()
    ax.set(xlabel='Percentile',
           ylabel='Latency (milliseconds)',
           title='Latency Percentiles (lower is better)')
    ax.set_xscale('logit')
    plt.xticks([0.25, 0.5, 0.9, 0.99, 0.999, 0.9999, 0.99999, 0.999999])
    majors = ["25%", "50%", "90%", "99%", "99.9%", "99.99%", "99.999%", "99.9999%"]
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(majors))
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102),
               loc=3, ncol=2,  borderaxespad=0.,
               labels=labels)
    return fig, ax


def arg_parse():
    parser = argparse.ArgumentParser(description='Plot HDRHistogram latencies.')
    parser.add_argument('files', nargs='+', help='list HDR files to plot')
    parser.add_argument('--output',
                        default='latency.png',
                        help='Output file name (default: latency.png)')
    parser.add_argument('--title', default='', help='The plot title.')
    args = parser.parse_args()
    return args


def main():
    # print command line arguments
    args = arg_parse()

    # load the data and create the plot
    pct_data = parse_files(args.files)
    labels = [re.findall(filename, file)[0][1] for file in args.files]
    fig, ax = plot_percentiles(pct_data, labels)
    plt.suptitle(args.title)
    plt.savefig(args.output)
    print( "Wrote: " + args.output)


if __name__ == "__main__":
    main()
