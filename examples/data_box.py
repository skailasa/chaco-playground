import numpy as np
import scipy.misc

from chaco.api import (
    CMapImagePlot, DataRange1D, DataRange2D, Greys, Plot, ArrayPlotData,
    GridDataSource, GridMapper, ImageData, reverse, GridPlotContainer,
)
from chaco.overlays.databox import DataBox
from chaco.tools.api import MoveTool
from enable.component_editor import ComponentEditor
from traits.api import Array, Range, HasTraits, Instance, Tuple, Bool
from traits.trait_errors import TraitError
from traitsui.api import Item, View


def calculate_intensity_histogram(pixel_data):
    #: Number of bins reflect 8-bit greyscale values
    hist, bin_edges = np.histogram(
        pixel_data.flatten(), bins=256, range=(0, 256)
    )

    return hist, bin_edges[:-1]


class MyImagePlot(HasTraits):

    # define plot as a trait
    plot = Instance(GridPlotContainer)

    my_position = Tuple(0, 0)
    off_grid = Bool(False)
    my_data_bounds = Range(low=50, high=250)

    # subset of image matrix
    submatrix = Array(shape=(my_data_bounds.value, my_data_bounds.value))

    # histogram and bin edge locations
    hist = Array()
    bin_edges = Array()

    traits_view = View(
        Item('my_data_bounds'),
        Item(
            'plot',
            editor=ComponentEditor(),
            width=500,
            height=500,
            ),
        title='Image:',
        width=800,
        height=600
        )

    def __init__(self, image):
        self.im = image
        self.plot_constructors = [
            self.image_histogram_plot_component,
            self.intensity_histogram_plot_component,
        ]
        self.submatrix = self.im[0:self.my_data_bounds, 0:self.my_data_bounds]
        self.hist, self.bin_edges = calculate_intensity_histogram(
            self.submatrix
        )

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
            data=self.im, value_depth=1
        )
        reversed_grays = reverse(Greys)
        color_mapper = reversed_grays(DataRange1D(color_source))

        plot = CMapImagePlot(
            index=index,
            index_mapper=index_mapper,
            value=color_source,
            value_mapper=color_mapper,
            orientation='h',
            origin='top left',
        )

        self.data_box_overlay = DataBox(
            component=plot,
            data_position=[0, 0],
            data_bounds=[self.my_data_bounds, self.my_data_bounds],
        )

        move_tool = MoveTool(component=self.data_box_overlay)
        self.data_box_overlay.tools.append(move_tool)

        self.data_box_overlay.on_trait_change(
            self.update_my_position, 'position'
        )

        #: Add to plot
        plot.overlays.append(self.data_box_overlay)

        return plot

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
        plot.padding = 0

        return plot

    def update_my_position(object, new):
        try:
            object.my_position = object.plot._components[0].map_index(new)
            object.off_grid = False
        except TraitError:
            object.off_grid = True

    def _my_data_bounds_changed(self):
        if not self.off_grid:
            self.data_box_overlay.data_bounds = [
                self.my_data_bounds, self.my_data_bounds
            ]
            self.data_box_overlay._data_position = self.my_position

    def _my_position_changed(self, new):
        self.submatrix = self.im[
                         new[0]: new[0]+self.my_data_bounds,
                         new[1]: new[1]+self.my_data_bounds
                         ]

    def _submatrix_changed(self, new):
        self.hist, self.bin_edges = calculate_intensity_histogram(new)

    def _bin_edges_changed(self):
        self.plot._components[1].data.set_data('x', self.bin_edges)

    def _hist_changed(self):
        self.plot._components[1].data.set_data('y', self.hist)


if __name__ == "__main__":
    test_image = scipy.misc.ascent()
    plot = MyImagePlot(test_image)
    plot.configure_traits()
