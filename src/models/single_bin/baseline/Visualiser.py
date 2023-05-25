
import matplotlib.pyplot as plt
import numpy as np

from .single_bin_packing import SingleBinPacking
from .item_packing import ItemPacking

#from src import CreelPacking
#from iterative.creel.variables.CreelSection import CreelSection

def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def show_bin_packing(bin_pack: SingleBinPacking):
    np.random.seed(seed=42)

    bin_width = bin_pack.bin.width
    bin_height = bin_pack.bin.length

    #bin_height /= bin_width
        
    fig_size = (10*bin_height/bin_width,10)
    (fig, ax) = plt.subplots(figsize=fig_size)

    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    
    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))

    cmap = get_cmap(len(bin_pack.items))


    for i,item in enumerate(bin_pack.items):
        if item.selected:
            show_item(ax, item, bin_width, bin_height, cmap(i))

    #return plt.show()

def show_bin_packing_per_item(bin_pack: SingleBinPacking):
    bin_width = bin_pack.bin.width
    bin_height = bin_pack.bin.length

    #bin_height /= bin_width
        
    fig_size = (10*bin_height/bin_width,10)
    (fig, axs) = plt.subplots(len(bin_pack.items), figsize=fig_size)

    for i,item in enumerate(bin_pack.items):
        axs[i].get_yaxis().set_visible(False)
        axs[i].get_xaxis().set_visible(False)
        
        axs[i].set_xlim((0, 1))
        axs[i].set_ylim((0, 1))
        if item.selected:
            show_item(axs[i], item, bin_width, bin_height)

    return plt.show()


def show_item(ax, item: ItemPacking, bin_width: int, bin_height: int, color):
    # print(item.pos_xs)
    # print(item.pos_ys)
    xs = item.pos_xs / bin_width
    ys = item.pos_ys / bin_height
    ws = item.widths / bin_width
    hs = item.heights / bin_height

    # color = item.item.color.basic_colors[0].tuple
    # color = (color[0]/255, color[1]/255, color[2]/255)

    for i,(x,y,w,h) in enumerate(zip(xs,ys,ws,hs)):
        if item.count > i:
            #print(i, x, y, w, h)
            ax.add_patch(
                    plt.Rectangle(
                        (y,x),
                        h,
                        w,
                        edgecolor='black',
                        facecolor=color,
                    )
                )

# def show_color_regions(creel_packing: CreelPacking):

#     creel_packing._max_deadline

#     fig_size = (15,5)
#     (fig, ax) = plt.subplots(figsize=fig_size)

#     ax.get_yaxis().set_visible(False)
#     ax.get_xaxis().set_visible(False)
    
#     ax.set_xlim((0, 1))
#     ax.set_ylim((0, 1))

#     print("Creel count:", creel_packing.count.value())

#     for i_creel in range(creel_packing.count.value()):
#         start = creel_packing.starts[i_creel].value()
#         end = creel_packing.ends[i_creel].value() + 1

#         print((start/creel_packing._max_deadline,0))


#         print((end-start)/creel_packing._max_deadline)

#         ax.add_patch(
#                     plt.Rectangle(
#                         (start/creel_packing._max_deadline,0),
#                         (end-start)/creel_packing._max_deadline,
#                         1,
#                         edgecolor='black',
#                         facecolor='white',
#                     )
#                 )

#         creel_section = creel_packing.sections[i_creel]

#         for i_color_section,color_section in enumerate(creel_section.color_sections):
#             color = color_section.color
#             print("color subsection count:", color_section.count.value())
#             for i_color_subsection in range(color_section.count.value()):
#                 start_subsect = color_section.starts[i_color_subsection].value()
#                 end_subsect = color_section.ends[i_color_subsection].value()
#                 width_subsect = color_section.widths[i_color_subsection].value()

#                 ax.add_patch(
#                     plt.Rectangle(
#                         (start/creel_packing._max_deadline,start_subsect/creel_packing._machine_config.width),
#                         (end-start)/creel_packing._max_deadline,
#                         width_subsect/creel_packing._machine_config.width,
#                         edgecolor='black',
#                         facecolor=(color.tuple[0]/255,color.tuple[1]/255,color.tuple[2]/255),
#                     )
#                 )



# def show_color_sections(creel_section: CreelSection, machine_width):

#     fig_size = (15,5)
#     (fig, ax) = plt.subplots(figsize=fig_size)

#     ax.get_yaxis().set_visible(False)
#     ax.get_xaxis().set_visible(False)
    
#     ax.set_xlim((0, 1))
#     ax.set_ylim((0, 1))

#     nr_colors = len(creel_section.color_sections)

#     for i_color,color_section in enumerate(creel_section.color_sections):

#         ax.add_patch(
#             plt.Rectangle(
#                 (i_color*(1/nr_colors), 0),
#                 1/(2*nr_colors),
#                 1,
#                 edgecolor='black',
#                 facecolor='grey',
#             )
#         )

        
#         color = color_section.color
#         print("color subsection count:", color_section.count.value())
#         print(color)
#         for i_color_subsection in range(color_section.count.value()):
#             start_subsect = color_section.starts[i_color_subsection].value()
#             end_subsect = color_section.ends[i_color_subsection].value()
#             width_subsect = color_section.widths[i_color_subsection].value()

#             print(start_subsect, end_subsect, width_subsect)

#             ax.add_patch(
#                 plt.Rectangle(
#                     (i_color*(1/nr_colors), start_subsect/machine_width),
#                     1/(2*nr_colors),
#                     width_subsect/machine_width,
#                     edgecolor='black',
#                     facecolor=(color.tuple[0]/255,color.tuple[1]/255,color.tuple[2]/255),
#                 )
#             )




