
import matplotlib.pyplot as plt
import numpy as np

from .single_bin_packing import SingleBinPacking
from .item_packing import ItemPacking

# code by Ali (https://stackoverflow.com/questions/14720331/how-to-generate-random-colors-in-matplotlib)
def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

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

    ax.add_patch(
        plt.Rectangle(
            (0,0),
            1,
            1,
            edgecolor='green',
            facecolor="white",
            linewidth=5
        )
    )

    cmap = get_cmap(len(bin_pack.items))


    for i,item in enumerate(bin_pack.items):
        if item.selected:
            show_item(ax, item, bin_width, bin_height, cmap(i))

def show_bin_packing_per_item(bin_pack: SingleBinPacking):
    bin_width = bin_pack.bin.width
    bin_height = bin_pack.bin.length

        
    fig_size = (10*bin_height/bin_width,10)
    (_, axs) = plt.subplots(len(bin_pack.items), figsize=fig_size)

    for i,item in enumerate(bin_pack.items):
        axs[i].get_yaxis().set_visible(False)
        axs[i].get_xaxis().set_visible(False)
        
        axs[i].set_xlim((0, 1))
        axs[i].set_ylim((0, 1))
        if item.selected:
            show_item(axs[i], item, bin_width, bin_height)

    return plt.show()


def show_item(ax, item: ItemPacking, bin_width: int, bin_height: int, color):
    xs = item.pos_xs / bin_width
    ys = item.pos_ys / bin_height
    ws = item.widths / bin_width
    hs = item.heights / bin_height

    for i,(x,y,w,h) in enumerate(zip(xs,ys,ws,hs)):
        if item.count > i:
            ax.add_patch(
                    plt.Rectangle(
                        (y,x),
                        h,
                        w,
                        edgecolor='black',
                        facecolor=color,
                    )
                )