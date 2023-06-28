
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np

from .single_bin_packing import SingleBinPacking
from src.data_structures.item import Item
from .item_packing import ItemPacking

from src.data_structures.bin import Bin

def show_bin_packing(bin_pack: SingleBinPacking):
    np.random.seed(seed=42)

    bin_width = bin_pack.bin.width
    bin_height = bin_pack.bin.max_length

    #bin_height /= bin_width
        
    fig_size = (10*bin_height/bin_width,10)
    (fig, ax) = plt.subplots(figsize=fig_size)

    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    
    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))

    cmap = get_cmap(len(bin_pack.items)//2)

    for i,item in enumerate(bin_pack.items):
        if item.selected:
            show_item(ax, item, bin_width, bin_height, cmap(i%(len(bin_pack.items)//2)))

    show_bin_length(ax, bin_pack.bin)
    #show_solving_zone(ax, bin_pack.bin, bin_height)

    #return plt.show()

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

    #bin_height /= bin_width
        
    fig_size = (10*bin_height/bin_width,10)
    (fig, axs) = plt.subplots(len(bin_pack.items), figsize=fig_size)

    cmap = get_cmap(len(bin_pack.items)/2)

    for i,item in enumerate(bin_pack.items):
        axs[i].get_yaxis().set_visible(False)
        axs[i].get_xaxis().set_visible(False)
        
        axs[i].set_xlim((0, 1))
        axs[i].set_ylim((0, 1))
        if item.selected:
            show_item(axs[i], item, bin_width, bin_height, cmap(i%(len(bin_pack.items)/2)))

    return plt.show()

def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def show_item(ax:Axes, item: ItemPacking, bin_width: int, bin_height: int, color):
    # print(item.pos_xs)
    # print(item.pos_ys)
    # xs = item.pos_xs / bin_width
    # ys = item.pos_ys / bin_height
    # ws = item.widths / bin_width
    # hs = item.heights / bin_height

    # if (hasattr(item.item, "color")):
    #     color = item.item.color.basic_colors[0].visualise()
    #     #color = (color[0]/255, color[1]/255, color[2]/255)
        
    color_faded = (float(color[0])/255, float(color[1])/255, float(color[2])/255, 0.5)
    # (
    #     0.5*float(color[0])/float(255), 
    #     0.5*float(color[1])/float(255), 
    #     0.5*float(color[2])/float(255))

    

    # for i,(x,y,w,h) in enumerate(zip(xs,ys,ws,hs)):
    #     #if item.count > i:
    #     #print(i)
    #     if item.active.free_value.value()[i]:
    #         #print(i, x, y, w, h)
    #         ax.add_patch(
    #                 plt.Rectangle(
    #                     (y,x),
    #                     h,
    #                     w,
    #                     edgecolor='black',
    #                     facecolor=color,
    #                 )
    #             )

    # print(item.nr_length_repeats())
    # print(item.active_arr)
    # print(item.pos_xs_arr)

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
                # ax.text(
                #     item.pos_ys_arr[y,x]/bin_height + 10/bin_height, 
                #     item.pos_xs_arr[y,x]/bin_width + 10/bin_width, 
                #     "(" + str(x) + "," + str(y) + ") (" + str(item.pos_xs_arr[y,x]) + "," + str(item.pos_ys_arr[y,x]) + ") " + str(item.rotation), fontsize=25) 

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
                # ax.text(
                #     item.pos_ys_arr[y,x]/bin_height + 10/bin_height, 
                #     item.pos_xs_arr[y,x]/bin_width + 10/bin_width, 
                #     "(" + str(x) + "," + str(y) + ") (" + str(item.pos_xs_arr[y,x]) + "," + str(item.pos_ys_arr[y,x]) + ") " + str(item.rotation), fontsize=25) 

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
                # ax.text(
                #     item.pos_ys_arr[y,x]/bin_height + 10/bin_height, 
                #     item.pos_xs_arr[y,x]/bin_width + 10/bin_width, 
                #     "(" + str(x) + "," + str(y) + ") (" + str(item.pos_xs_arr[y,x]) + "," + str(item.pos_ys_arr[y,x]) + ") " + str(item.rotation), fontsize=25) 

# def show_creel(creel_packing: CreelPacking):

#     creel_sections = creel_packing.sections
#     nr_creel_sections = len(creel_sections)
#     creel_starts = creel_packing.starts.value()
#     creel_ends = creel_packing.ends.value()



#     fig_size = (15,5)
#     (fig, ax) = plt.subplots(figsize=fig_size)

#     cmap = get_cmap(nr_creel_sections)

#     for i_creel_section in range(creel_packing.count.value()):
#         s = creel_starts[i_creel_section] / creel_ends[creel_packing.count.value() - 1]
#         e = creel_ends[i_creel_section] / creel_ends[creel_packing.count.value()-1]

        
#         ax.add_patch(
#             plt.Rectangle(
#                 (s,0),
#                 (e-s),
#                 1,
#                 edgecolor='black',
#                 facecolor=cmap(i_creel_section),
#             )
#         )





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
#                         facecolor=(color.visualise()[0],color.visualise()[1],color.visualise()[2]),
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




