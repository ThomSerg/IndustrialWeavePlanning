
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np



def show_creel(creel_packing):

    creel_sections = creel_packing.sections
    nr_creel_sections = len(creel_sections)
    creel_starts = creel_packing.starts.value()
    creel_ends = creel_packing.ends.value()



    fig_size = (15,5)
    (fig, ax) = plt.subplots(figsize=fig_size)

    cmap = get_cmap(nr_creel_sections)

    for i_creel_section in range(creel_packing.count.value()):
        s = creel_starts[i_creel_section] / creel_ends[creel_packing.count.value() - 1]
        e = creel_ends[i_creel_section] / creel_ends[creel_packing.count.value()-1]

        
        ax.add_patch(
            plt.Rectangle(
                (s,0),
                (e-s),
                1,
                edgecolor='black',
                facecolor=cmap(i_creel_section),
            )
        )
    plt.figure()
    show_color_regions(creel_packing)

def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)




def show_color_regions(creel_packing):


    fig_size = (15,5)
    (fig, ax) = plt.subplots(figsize=fig_size)

    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    
    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))

    print("Creel count:", creel_packing.count.value())

    for i_creel in range(creel_packing.count.value()):
        start = creel_packing.starts[i_creel].value()
        end = creel_packing.ends[i_creel].value() + 1


        ax.add_patch(
                    plt.Rectangle(
                        (start/creel_packing.max_deadline,0),
                        (end-start)/creel_packing.max_deadline,
                        1,
                        edgecolor='black',
                        facecolor='white',
                    )
                )

        creel_section = creel_packing.sections[i_creel]

        for i_color_section,color_section in enumerate(creel_section.color_sections):
            color = color_section.color
            print("color subsection count:", color_section.count.value())
            print(color)
            for i_color_subsection in range(color_section.count.value()):
                start_subsect = color_section.starts[i_color_subsection].value()
                end_subsect = color_section.ends[i_color_subsection].value()
                width_subsect = color_section.widths[i_color_subsection].value()

                print(start_subsect, end_subsect, width_subsect)

                ax.add_patch(
                    plt.Rectangle(
                        (start/creel_packing.max_deadline,start_subsect/creel_packing.machine_config.width),
                        (end-start)/creel_packing.max_deadline,
                        width_subsect/creel_packing.machine_config.width,
                        edgecolor='black',
                        facecolor=(color.visualise()[0],color.visualise()[1],color.visualise()[2]),
                    )
                )



def show_color_sections(creel_section, machine_width):

    fig_size = (15,5)
    (fig, ax) = plt.subplots(figsize=fig_size)

    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    
    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))

    nr_colors = len(creel_section.color_sections)

    for i_color,color_section in enumerate(creel_section.color_sections):

        ax.add_patch(
            plt.Rectangle(
                (i_color*(1/nr_colors), 0),
                1/(2*nr_colors),
                1,
                edgecolor='black',
                facecolor='grey',
            )
        )

        
        color = color_section.color
        print("color subsection count:", color_section.count.value())
        print(color)
        for i_color_subsection in range(color_section.count.value()):
            start_subsect = color_section.starts[i_color_subsection].value()
            end_subsect = color_section.ends[i_color_subsection].value()
            width_subsect = color_section.widths[i_color_subsection].value()

            print(start_subsect, end_subsect, width_subsect)

            ax.add_patch(
                plt.Rectangle(
                    (i_color*(1/nr_colors), start_subsect/machine_width),
                    1/(2*nr_colors),
                    width_subsect/machine_width,
                    edgecolor='black',
                    facecolor=(color.tuple[0]/255,color.tuple[1]/255,color.tuple[2]/255),
                )
            )
