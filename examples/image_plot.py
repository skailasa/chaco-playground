import numpy as np
import scipy.misc

from chaco.api import (
    ArrayPlotData, CMapImagePlot, DataRange1D, DataRange2D, Greys,
    GridDataSource, GridMapper, ImageData, Plot, reverse, GridPlotContainer,
)
from chaco.overlays.databox import DataBox
from chaco.tools.api import MoveTool
from enable.component_editor import ComponentEditor
from enable.tools.api import ResizeTool
from traits.api import Array, Event, HasTraits, Instance, Tuple
from traitsui.api import Item, View


TEST = scipy.misc.ascent()  # test image


class MyDataBox(DataBox):

    updated = Event()

    def _data_position_changed(self):
        self.updated = True


def calculate_intensity_histogram(pixel_data):
    #: Number of bins reflect 8-bit greyscale values
    hist, bin_edges = np.histogram(
        pixel_data.flatten(), bins=256, range=(0, 256)
    )

    return hist, bin_edges[:-1]


class MyImagePlot(HasTraits):

    # Data box size
    #box_size = Int(50)
    box_size = 50

    # define plot as a trait
    plot = Instance(GridPlotContainer)

    position = Tuple(0, 0)

    # subset of image matrix
    submatrix = Array(shape=(box_size, box_size))

    # histogram and bin edge locations
    hist = Array()
    bin_edges = Array()

    traits_view = View(
        Item(
            'plot',
            editor=ComponentEditor(),
            ),
        title='Image:',
        resizable=True,
        )

    def __init__(self, image):
        self.im = image
        self.plot_constructors = [
            self.image_histogram_plot_component,
            self.intensity_histogram_plot_component,
        ]

        self.submatrix = self.im[0:self.box_size, 0:self.box_size]
        self.hist, self.bin_edges = calculate_intensity_histogram(self.submatrix)

    def _plot_default(self):
        return self.grid_plot_component()

    def grid_plot_component(self):
        container = GridPlotContainer(
            padding=50,
            fill_padding=True,
            shape=(1, len(self.plot_constructors)),
            spacing=(20, 20)
        )

        for plot_constructor in self.plot_constructors:
            plot = plot_constructor()
            container.add(plot)

        return container

    def image_histogram_plot_component(self):
        xs = np.arange(0, len(self.im))
        ys = np.arange(0, len(self.im[0]))

        index = GridDataSource(
            xdata=xs, ydata=ys, sort_order=('ascending', 'ascending'))

        index_mapper = GridMapper(range=DataRange2D(index))

        color_source = ImageData(
            data=np.flipud(self.im), value_depth=1
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
        data_box_overlay = MyDataBox(
            component=plot,
            data_position=[0, 0],
            data_bounds=[self.box_size, self.box_size],
        )

        move_tool = MoveTool(component=data_box_overlay)
        resize_tool = ResizeTool(component=data_box_overlay)
        data_box_overlay.tools.append(move_tool)
        data_box_overlay.tools.append(resize_tool)

        data_box_overlay.on_trait_change(self.update_position, 'position')

        #: Add to plot
        plot.overlays.append(data_box_overlay)

        return plot

    def calculate_intensity_histogram(self, pixel_data):
        #: Number of bins reflect 8-bit greyscale values

        hist, bin_edges = np.histogram(
            pixel_data.flatten(), bins=256, range=(0, 256)
        )

        return hist, bin_edges

    def _bin_edges_changed(self):
        self.plot._components[1].data.set_data('x', self.bin_edges)

    def _hist_changed(self):
        self.plot._components[1].data.set_data('y', self.hist)

    def intensity_histogram_plot_component(self):

        data = ArrayPlotData(x=self.bin_edges, y=self.hist)

        plot = Plot(data)
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

    def update_position(self, name, new):
        self.position = self.plot._components[0].map_index(new)

    def _position_changed(self, new):
        # update image histogram
        self.submatrix = self.im[new[0]: new[0]+self.box_size, new[1]: new[1]+self.box_size]

    def _submatrix_changed(self, new):
        self.hist, self.bin_edges = calculate_intensity_histogram(new)
        print(new.shape)


if __name__ == "__main__":
    image = MyImagePlot(TEST)
    image.configure_traits()
