
import unittest

import numpy

from cupy import testing
import cupyx.scipy.ndimage  # NOQA

try:
    import scipy.ndimage  # NOQA
except ImportError:
    pass


@testing.parameterize(
    {'rank': 0, 'connectivity': 1},
    {'rank': 1, 'connectivity': 1},
    {'rank': 2, 'connectivity': 1},
    {'rank': 2, 'connectivity': 2},
    {'rank': 3, 'connectivity': 1},
    {'rank': 3, 'connectivity': 2},
    {'rank': 3, 'connectivity': 3},
    # edge cases
    {'rank': -1, 'connectivity': 0},
    {'rank': 3, 'connectivity': 0},
    {'rank': 3, 'connectivity': 500})
@testing.gpu
@testing.with_requires('scipy')
class TestGenerateBinaryStructure(unittest.TestCase):

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_generate_binary_structure(self, xp, scp):
        return scp.ndimage.generate_binary_structure(self.rank,
                                                     self.connectivity)


@testing.gpu
@testing.with_requires('scipy')
class TestIterateStructure(unittest.TestCase):

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_iterate_structure1(self, xp, scp):
        struct = xp.asarray([[0, 1, 0],
                             [1, 1, 1],
                             [0, 1, 0]])
        return scp.ndimage.iterate_structure(struct, 2)

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_iterate_structure2(self, xp, scp):
        struct = xp.asarray([[0, 1],
                             [1, 1],
                             [0, 1]])
        return scp.ndimage.iterate_structure(struct, 2)

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_iterate_structure3(self, xp, scp):
        struct = xp.asarray([[0, 1, 0],
                             [1, 1, 1],
                             [0, 1, 0]])
        out, origin = scp.ndimage.iterate_structure(struct, 2, 1)
        assert origin == [2, 2]
        return out


@testing.parameterize(*(
    testing.product({
        'x_dtype': [numpy.bool, numpy.int8, numpy.uint8, numpy.float32,
                    numpy.float64],
        'border_value': [0, 1],
        'structure': [None, [1, 0, 1], [1, 1, 0]],
        'origin': [-1, 0, 1],
        'data': [[], [1, 1, 0, 1, 1]],
        'filter': ['binary_erosion', 'binary_dilation'],
        'output': [None, numpy.float32, numpy.int8]}
    ))
)
@testing.gpu
@testing.with_requires('scipy')
class BinaryErosionAndDilation1d(unittest.TestCase):
    def _filter(self, xp, scp, x):
        filter = getattr(scp.ndimage, self.filter)
        structure = self.structure
        if structure is not None:
            structure = xp.asarray(structure)
        return filter(x, structure, iterations=1, mask=None,
                      output=self.output, border_value=self.border_value,
                      origin=self.origin, brute_force=True)

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_binary_erosion_and_dilation_1d(self, xp, scp):
        if self.x_dtype == self.output:
            raise unittest.SkipTest('redundant')
        x = xp.asarray(self.data, dtype=self.x_dtype)
        return self._filter(xp, scp, x)


@testing.parameterize(*(
    testing.product({
        'x_dtype': [numpy.bool, numpy.float64],
        'border_value': [0, 1],
        'connectivity': [1, 2],
        'origin': [0, 1],
        'data': [[[0, 1, 0, 0, 0, 0, 0, 0],
                  [1, 1, 1, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 1, 0, 0],
                  [0, 0, 0, 1, 1, 1, 1, 0],
                  [0, 0, 1, 1, 0, 1, 0, 0],
                  [0, 1, 1, 1, 1, 1, 1, 0],
                  [0, 0, 1, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],

                 [[1, 1, 1, 0, 0, 0, 0, 0],
                  [1, 1, 1, 0, 0, 0, 0, 0],
                  [1, 1, 1, 1, 1, 1, 1, 0],
                  [0, 0, 1, 1, 1, 1, 1, 0],
                  [0, 1, 1, 1, 0, 1, 1, 0],
                  [0, 1, 1, 1, 1, 1, 1, 0],
                  [0, 1, 1, 1, 1, 1, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],
                 ],
        'filter': ['binary_opening', 'binary_closing'],
        'output': [None, numpy.float32, numpy.int8]}
    ))
)
@testing.gpu
@testing.with_requires('scipy>=1.1.0')
class BinaryOpeningAndClosing(unittest.TestCase):
    def _filter(self, xp, scp, x):
        filter = getattr(scp.ndimage, self.filter)
        structure = scp.ndimage.generate_binary_structure(x.ndim,
                                                          self.connectivity)
        return filter(x, structure, iterations=1, output=self.output,
                      origin=self.origin, mask=None,
                      border_value=self.border_value, brute_force=True)

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_binary_opening_and_closing(self, xp, scp):
        if self.x_dtype == self.output:
            raise unittest.SkipTest('redundant')
        x = xp.asarray(self.data, dtype=self.x_dtype)
        return self._filter(xp, scp, x)


@testing.parameterize(*(
    testing.product({
        'x_dtype': [numpy.bool, numpy.float64],
        'connectivity': [1, 2],
        'origin': [-1, 0, 1],
        'data': [[[0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 1, 1, 1, 1, 0, 0],
                  [0, 0, 1, 0, 0, 1, 0, 0],
                  [0, 0, 1, 0, 0, 1, 0, 0],
                  [0, 0, 1, 0, 0, 1, 0, 0],
                  [0, 0, 1, 1, 1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],

                 [[0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 1, 1, 0, 0, 0],
                  [0, 0, 1, 0, 0, 1, 0, 0],
                  [0, 0, 1, 0, 0, 1, 0, 0],
                  [0, 0, 1, 0, 0, 1, 0, 0],
                  [0, 0, 0, 1, 1, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],

                 [[0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0, 0, 0],
                  [0, 1, 0, 1, 0, 1, 1, 1],
                  [0, 1, 0, 1, 0, 1, 0, 1],
                  [0, 1, 0, 1, 0, 1, 0, 1],
                  [0, 0, 1, 0, 0, 1, 1, 1],
                  [0, 0, 0, 0, 0, 0, 0, 0]],
                 ],
        'output': [None, numpy.float32, numpy.int8]}
    ))
)
@testing.gpu
@testing.with_requires('scipy')
class BinaryFillHoles(unittest.TestCase):
    def _filter(self, xp, scp, x):
        filter = scp.ndimage.binary_fill_holes
        structure = scp.ndimage.generate_binary_structure(x.ndim,
                                                          self.connectivity)
        return filter(x, structure, output=self.output, origin=self.origin)

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_binary_fill_holes(self, xp, scp):
        if self.x_dtype == self.output:
            raise unittest.SkipTest('redundant')
        x = xp.asarray(self.data, dtype=self.x_dtype)
        return self._filter(xp, scp, x)


@testing.parameterize(*(
    testing.product({
        'x_dtype': [numpy.bool, numpy.float64],
        'struct': ['same', 'separate'],
        'origins': [((0, 0), (0, 0)),
                    ((0, 1), (-1, 0))],
        'data': [[[0, 1, 0, 0, 0],
                  [1, 1, 1, 0, 0],
                  [0, 1, 0, 1, 1],
                  [0, 0, 1, 1, 1],
                  [0, 1, 1, 1, 0],
                  [0, 1, 1, 1, 1],
                  [0, 1, 1, 1, 1],
                  [0, 0, 0, 0, 0]],

                 [[0, 1, 0, 0, 1, 1, 1, 0],
                  [1, 1, 1, 0, 0, 1, 0, 0],
                  [0, 1, 0, 1, 1, 1, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],

                 [[0, 1, 0, 0, 1, 1, 1, 0],
                  [1, 1, 1, 0, 0, 0, 0, 0],
                  [0, 1, 0, 1, 1, 1, 1, 0],
                  [0, 0, 1, 1, 1, 1, 1, 0],
                  [0, 1, 1, 1, 0, 1, 1, 0],
                  [0, 0, 0, 0, 1, 1, 1, 0],
                  [0, 1, 1, 1, 1, 1, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],
                 ],
        'output': [None, numpy.float32, numpy.int8]}
    ))
)
@testing.gpu
@testing.with_requires('scipy')
class BinaryHitOrMiss(unittest.TestCase):
    def _filter(self, xp, scp, x):
        filter = scp.ndimage.binary_hit_or_miss
        if self.struct == 'same':
            structure1 = scp.ndimage.generate_binary_structure(x.ndim, 1)
            structure2 = structure1
        elif self.struct == 'separate':
            structure1 = xp.asarray([[0, 0, 0],
                                     [1, 1, 1],
                                     [0, 0, 0]])

            structure2 = xp.asarray([[1, 1, 1],
                                     [0, 0, 0],
                                     [1, 1, 1]])
        origin1, origin2 = self.origins
        return filter(x, structure1, structure2, output=self.output,
                      origin1=origin1, origin2=origin2)

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_binary_hit_or_miss(self, xp, scp):
        if self.x_dtype == self.output:
            raise unittest.SkipTest('redundant')
        x = xp.asarray(self.data, dtype=self.x_dtype)
        return self._filter(xp, scp, x)


@testing.parameterize(*(
    testing.product({
        'x_dtype': [numpy.bool, numpy.float64],
        'border_value': [0, 1],
        'connectivity': [1, 2],
        'origin': [0, 1],
        'mask': [[[0, 1, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1, 1, 0, 0],
                  [0, 0, 1, 1, 1, 0, 0, 0],
                  [0, 1, 1, 0, 1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],

                 [[0, 1, 0, 0, 0, 0, 0, 0],
                  [0, 1, 1, 0, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 1, 0, 0],
                  [0, 0, 0, 1, 1, 0, 0, 0],
                  [0, 0, 1, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],
                 ],
        'data': [[[0, 1, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],

                 [[0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]],
                 ],
        'output': [None, numpy.float32, numpy.int8]}
    ))
)
@testing.gpu
@testing.with_requires('scipy')
class BinaryPropagation(unittest.TestCase):
    def _filter(self, xp, scp, x):
        filter = scp.ndimage.binary_propagation
        structure = scp.ndimage.generate_binary_structure(x.ndim,
                                                          self.connectivity)
        mask = xp.asarray(self.mask)
        return filter(x, structure, mask=mask, output=self.output,
                      border_value=self.border_value, origin=self.origin)

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_binary_propagation(self, xp, scp):
        if self.x_dtype == self.output:
            raise unittest.SkipTest('redundant')
        x = xp.asarray(self.data, dtype=self.x_dtype)
        return self._filter(xp, scp, x)


@testing.parameterize(*(
    testing.product({
        'x_dtype': [numpy.int8, numpy.float32],
        'border_value': [0, 1],
        'connectivity': [1, 2],
        'origin': [0, -1],
        'shape': [(64,), (16, 15), (5, 7, 9)],
        'density': [0.1, 0.5, 0.9],
        'filter': ['binary_erosion', 'binary_dilation'],
        'iterations': [1, 2, 0],
        'output': [None, numpy.float32]}
    ))
)
@testing.gpu
@testing.with_requires('scipy')
class BinaryErosionAndDilation(unittest.TestCase):
    def _filter(self, xp, scp, x):
        filter = getattr(scp.ndimage, self.filter)
        ndim = len(self.shape)
        structure = scp.ndimage.generate_binary_structure(ndim,
                                                          self.connectivity)
        return filter(x, structure, iterations=self.iterations, mask=None,
                      output=self.output, border_value=self.border_value,
                      origin=self.origin, brute_force=True)

    @testing.numpy_cupy_array_equal(scipy_name='scp')
    def test_binary_erosion_and_dilation(self, xp, scp):
        if self.x_dtype == self.output:
            raise unittest.SkipTest('redundant')
        rstate = numpy.random.RandomState(5)
        x = rstate.randn(*self.shape) > self.density
        x = xp.asarray(x, dtype=self.x_dtype)
        return self._filter(xp, scp, x)


@testing.parameterize(*(
    testing.product({
        'shape': [(3, 4), (2, 3, 4), (1, 2, 3, 4)],
        'size': [3, 4],
        'footprint': [None, 'random'],
        'structure': [None, 'random'],
        'mode': ['reflect'],
        'cval': [0.0],
        'origin': [0, 1, None],
        'x_dtype': [numpy.int8, numpy.int16, numpy.int32,
                    numpy.float32, numpy.float64],
        'output': [None, numpy.int32, numpy.float64],
        'filter': ['grey_erosion', 'grey_dilation']
    }) + testing.product({
        'shape': [(3, 4), (2, 3, 4), (1, 2, 3, 4)],
        'size': [3, 4],
        'footprint': [None, 'random'],
        'structure': [None, 'random'],
        'mode': ['constant'],
        'cval': [-1.0, 0.0, 1.0],
        'origin': [0],
        'x_dtype': [numpy.int32, numpy.float64],
        'output': [None],
        'filter': ['grey_erosion', 'grey_dilation']
    }) + testing.product({
        'shape': [(3, 4), (2, 3, 4), (1, 2, 3, 4)],
        'size': [3, 4],
        'footprint': [None, 'random'],
        'structure': [None, 'random'],
        'mode': ['nearest', 'mirror', 'wrap'],
        'cval': [0.0],
        'origin': [0],
        'x_dtype': [numpy.int32, numpy.float64],
        'output': [None],
        'filter': ['grey_erosion', 'grey_dilation']
    })
))
@testing.gpu
@testing.with_requires('scipy')
class TestGreyErosionAndDilation(unittest.TestCase):

    def _filter(self, xp, scp, x):
        filter = getattr(scp.ndimage, self.filter)
        if self.origin is None:
            origin = (-1, 1, -1, 1)[:x.ndim]
        else:
            origin = self.origin
        if self.footprint is None:
            footprint = None
        else:
            shape = (self.size, ) * x.ndim
            r = testing.shaped_random(shape, xp, scale=1)
            footprint = xp.where(r < .5, 1, 0)
            if not footprint.any():
                footprint = xp.ones(shape)
        if self.structure is None:
            structure = None
        else:
            shape = (self.size, ) * x.ndim
            structure = testing.shaped_random(shape, xp, dtype=xp.int32)
        return filter(x, size=self.size, footprint=footprint,
                      structure=structure, output=self.output,
                      mode=self.mode, cval=self.cval, origin=origin)

    @testing.numpy_cupy_allclose(atol=1e-5, rtol=1e-5, scipy_name='scp')
    def test_grey_erosion_and_dilation(self, xp, scp):
        if self.mode == 'mirror' and 1 in self.shape:
            raise unittest.SkipTest('not testable against scipy')
        if self.x_dtype == self.output:
            raise unittest.SkipTest('redundant')
        x = testing.shaped_random(self.shape, xp, self.x_dtype)
        return self._filter(xp, scp, x)


@testing.parameterize(*testing.product({
    'size': [3, 4],
    'structure': [None, 'random'],
    'mode': ['reflect', 'constant', 'nearest', 'mirror', 'wrap'],
    'origin': [0, None],
    'x_dtype': [numpy.int32, numpy.float32],
    'output': [None, numpy.float64],
    'filter': ['grey_closing', 'grey_opening']
}))
@testing.gpu
@testing.with_requires('scipy')
class TestGreyClosingAndOpening(unittest.TestCase):

    shape = (4, 5)
    footprint = None
    cval = 0.0

    def _filter(self, xp, scp, x):
        filter = getattr(scp.ndimage, self.filter)
        if self.origin is None:
            origin = (-1, 1, -1, 1)[:x.ndim]
        else:
            origin = self.origin
        if self.structure is None:
            structure = None
        else:
            shape = (self.size, ) * x.ndim
            structure = testing.shaped_random(shape, xp, dtype=xp.int32)
        return filter(x, size=self.size, footprint=self.footprint,
                      structure=structure, output=self.output,
                      mode=self.mode, cval=self.cval, origin=origin)

    @testing.numpy_cupy_allclose(atol=1e-5, rtol=1e-5, scipy_name='scp')
    def test_grey_closing_and_opening(self, xp, scp):
        x = testing.shaped_random(self.shape, xp, self.x_dtype)
        return self._filter(xp, scp, x)