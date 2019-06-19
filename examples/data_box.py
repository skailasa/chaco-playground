import operator

import numpy as np
import scipy.misc

from chaco.api import (
    ArrayPlotData, CMapImagePlot, DataRange1D, DataRange2D, Greys,
    GridDataSource, GridMapper, ImageData, Plot, reverse, GridPlotContainer,
)
from chaco.overlays.databox import DataBox
from chaco.tools.api import MoveTool
from enable.component_editor import ComponentEditor
from traits.api import Array, Range, HasTraits, Instance, Tuple, Bool
from traits.trait_errors import TraitError
from traitsui.api import Item, View


TEST = scipy.misc.ascent()  # test image


class MyImagePlot(HasTraits):

    # define plot as a trait
    plot = Instance(GridPlotContainer)

    my_position = Tuple(0, 0)
    off_grid = Bool(False)
    my_data_bounds = Range(low=50, high=250)

    traits_view = View(
        Item('my_data_bounds'),
        Item(
            'plot',
            editor=ComponentEditor(),
            ),
        title='Image:',
        resizable=False,
        )

    def __init__(self, image):
        self.im = image
        self.plot_constructors = [
            self.image_histogram_plot_component,
        ]

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

        #: Add overlay for zoom
        self.data_box_overlay = DataBox(
            component=plot,
            data_position=[0, 0],
            data_bounds=[self.my_data_bounds, self.my_data_bounds],
        )

        move_tool = MoveTool(component=self.data_box_overlay)
        self.data_box_overlay.tools.append(move_tool)

        self.data_box_overlay.on_trait_change(self.update_my_position, 'position')

        #: Add to plot
        plot.overlays.append(self.data_box_overlay)

        return plot

    def update_my_position(self, name, new):
        try:
            self.my_position = self.plot._components[0].map_index(new)
            self.off_grid = False
        except TraitError:
            self.off_grid = True

    def _my_data_bounds_changed(self, name, new):
        if not self.off_grid:
            self.data_box_overlay.data_bounds = [
                self.my_data_bounds, self.my_data_bounds
            ]
            self.data_box_overlay._data_position = self.my_position


if __name__ == "__main__":
    image = MyImagePlot(TEST)
    image.configure_traits()
