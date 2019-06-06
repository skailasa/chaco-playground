import numpy as np
import scipy.misc

from chaco.api import (
    ArrayPlotData, CMapImagePlot, DataRange1D, DataRange2D, Greys,
    GridDataSource, GridMapper, ImageData, Plot, reverse, GridPlotContainer,
)
from chaco.overlays.databox import DataBox
from enable.component_editor import ComponentEditor
from chaco.tools.api import MoveTool
from traits.api import Instance, HasTraits, Str, Int, Array
from traitsui.api import Item, ModelView, View

from chaco.api import ImagePlot

TEST = scipy.misc.ascent()  # test image


def calculate_intensity_histogram(pixel_data):
    #: Number of bins reflect 8-bit greyscale values
    hist, bin_edges = np.histogram(
        pixel_data.flatten(), bins=256, range=(0, 256)
    )

    return hist, bin_edges[:-1]


def intensity_histogram_plot_component(im):
    hist, bin_edges = calculate_intensity_histogram(
        im.flatten()
    )

    plotdata = ArrayPlotData(x=bin_edges, y=hist)
    plot = Plot(plotdata)
    plot.plot(
        ('x', "y"),
        type='bar',
        color='auto',
        bar_width=1,
    )
    # without padding plot just doesn't seem to show up?
    plot.border_width = 0
    plot.padding = 0
    plot.padding_top = 0
    return plot


def image_histogram_plot_component(im):
    xs = np.arange(0, len(im))
    ys = np.arange(0, len(im[0]))

    index = GridDataSource(
        xdata=xs, ydata=ys, sort_order=('ascending', 'ascending'))

    index_mapper = GridMapper(range=DataRange2D(index))

    color_source = ImageData(
        data=np.flipud(im), value_depth=1
    )
    reversed_grays = reverse(Greys)
    color_mapper = reversed_grays(DataRange1D(color_source))

    plot = CMapImagePlot(
        index=index,
        index_mapper=index_mapper,
        value=color_source,
        value_mapper=color_mapper,
    )

    #: Add overlay for zoom
    data_box_overlay = DataBox(
        component=plot,
        data_position=[0, 0],
        data_bounds=[50, 50],
    )

    move_tool = MoveTool(component=data_box_overlay)
    data_box_overlay.tools.append(move_tool)

    data_box_overlay.on_trait_change(MyImagePlot.printer, 'data_position')

    #: Add to plot
    plot.overlays.append(data_box_overlay)

    return plot


def grid_plot_component(im, *plot_constructors):

    container = GridPlotContainer(
        padding=50,
        fill_padding=True,
        shape=(1, len(plot_constructors)),
        spacing=(20, 20)
    )

    for plot_constructor in plot_constructors:
        plot = plot_constructor(im)
        container.add(plot)

    return container


class MyImagePlot(HasTraits):

    # define plot as a trait
    plot = Instance(GridPlotContainer)

    position = Array(shape=(2, 1))

    traits_view = View(
        Item(
            'plot',
            editor=ComponentEditor(),
            ),
        title='Image:',
        resizable=True,
        )

    plot_constructors = [
        image_histogram_plot_component,
        intensity_histogram_plot_component,
    ]

    def _plot_default(self):
        return grid_plot_component(TEST, *self.plot_constructors)

    def printer(self, name, new):

        self.position = np.array([self.x, self.y])

        print("from the plot!: ", self.position)
        print("in index coords", self.component.map_index(self.position))


if __name__ == "__main__":
    image = MyImagePlot()
    image.configure_traits()

