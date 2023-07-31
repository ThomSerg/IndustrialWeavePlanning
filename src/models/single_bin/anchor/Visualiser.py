
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np

from .single_bin_packing import SingleBinPacking
from .item_packing import ItemPacking

from src.data_structures.bin import Bin

def show_bin_packing(bin_pack: SingleBinPacking):
    np.random.seed(seed=42)

    bin_width = bin_pack.bin.width
    bin_height = bin_pack.bin.max_length
        
    fig_size = (10*bin_height/bin_width,10)
    (_, ax) = plt.subplots(figsize=fig_size)

    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    
    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))

    cmap = get_cmap(len(bin_pack.items)//2)

    for i,item in enumerate(bin_pack.items):
        if item.selected:
            show_item(ax, item, bin_width, bin_height, cmap(i%(len(bin_pack.items)//2)))

    show_bin_length(ax, bin_pack.bin)

def show_bin_length(ax:Axes, bin: Bin):
    ax.axvline(x=bin.length/bin.max_length, ymin=0, ymax=1, linewidth=10) 

def show_solving_zone(ax:Axes, bin:Bin, bin_height):
    ax.add_patch(
                    plt.Rectangle(
                        (0,0),
                        (bin.config.max_packing_zone - bin.config.min_packing_zone)/bin_height,
                        1,
                        edgecolor='green',
                        facecolor='none',
                        linewidth=10                 
                    )
                )

def show_bin_packing_per_item(bin_pack: SingleBinPacking):
    bin_width = bin_pack.bin.width
    bin_height = bin_pack.bin.length
        
    fig_size = (10*bin_height/bin_width,10)
    (_, axs) = plt.subplots(len(bin_pack.items), figsize=fig_size)

    cmap = get_cmap(len(bin_pack.items)/2)

    for i,item in enumerate(bin_pack.items):
        axs[i].get_yaxis().set_visible(False)
        axs[i].get_xaxis().set_visible(False)
        
        axs[i].set_xlim((0, 1))
        axs[i].set_ylim((0, 1))
        if item.selected:
            show_item(axs[i], item, bin_width, bin_height, cmap(i%(len(bin_pack.items)/2)))

    return plt.show()

# code by Ali (https://stackoverflow.com/questions/14720331/how-to-generate-random-colors-in-matplotlib)
def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def show_item(ax:Axes, item: ItemPacking, bin_width: int, bin_height: int, color):

    y_min, y_max = 0, item.length_repeats_lower()

    for y in range(y_min, y_max):
        for x in range(item.nr_width_repeats()):
            if item.active_arr[y,x]:
                ax.add_patch(
                    plt.Rectangle(
                        (item.pos_ys_arr[y,x]/bin_height,item.pos_xs_arr[y,x]/bin_width),
                        item.height/bin_height,
                        item.width/bin_width,
                        edgecolor='black',
                        facecolor=color,
                        alpha=0.5
                    )
                )

    y_min, y_max = item.length_repeats_lower(), item.length_repeats_upper()+1

    for y in range(y_min, y_max):
        for x in range(item.nr_width_repeats()):
            if item.active_arr[y,x]:
                ax.add_patch(
                    plt.Rectangle(
                        (item.pos_ys_arr[y,x]/bin_height,item.pos_xs_arr[y,x]/bin_width),
                        item.height/bin_height,
                        item.width/bin_width,
                        edgecolor='black',
                        facecolor=color,
                    )
                )

    y_min, y_max = item.length_repeats_upper()+1, item.nr_length_repeats()

    for y in range(y_min, y_max):
        for x in range(item.nr_width_repeats()):
            if item.active_arr[y,x]:
                ax.add_patch(
                    plt.Rectangle(
                        (item.pos_ys_arr[y,x]/bin_height,item.pos_xs_arr[y,x]/bin_width),
                        item.height/bin_height,
                        item.width/bin_width,
                        edgecolor='black',
                        facecolor=color,
                        alpha=0.5
                    )
                )