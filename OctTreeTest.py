
#!/usr/bin/env python
# noinspection PyUnresolvedReferences
import numpy as np
from pathlib import Path
import vtk
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkFiltersGeneral import vtkVertexGlyphFilter
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData,
    vtkPolyLine
)
from vtkmodules.vtkFiltersCore import (
    vtkCleanPolyData,
    vtkElevationFilter,
    vtkGlyph3D,
    vtkMaskPoints,
    vtkPolyDataNormals,
    vtkTriangleFilter
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkActor2D,
    vtkCamera,
    vtkDataSetMapper,
    vtkGlyph3DMapper,
    vtkProperty,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkIOGeometry import (
     vtkBYUReader,
     vtkOBJReader,
     vtkSTLReader
)
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkFiltersSources import vtkArrowSource

def get_program_parameters():
    import argparse
    description = 'Read a VTK XML PolyData file.'
    epilogue = ''''''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='ism_test_cat.vtp.')
    args = parser.parse_args()
    return args.filename


def ReadPolyData(file_name):
    valid_suffixes = ['.g', '.obj', '.stl', '.ply', '.vtk', '.vtp']
    path = Path(file_name)
    if path.suffix:
        ext = path.suffix.lower()
    if path.suffix not in valid_suffixes:
        print(f'No reader for this file suffix: {ext}')
        return None
    else:
        if ext == ".ply":
            reader = vtkPLYReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".vtp":
            reader = vtkXMLPolyDataReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".obj":
            reader = vtkOBJReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".stl":
            reader = vtkSTLReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".vtk":
            reader = vtkPolyDataReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".g":
            reader = vtkBYUReader()
            reader.SetGeometryFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()

        return poly_data

class SliderObserver(object):
    def __init__(self, Octree, polyData, renderer):
        self.Octree = Octree
        self.level = 0
        self.polyData = polyData
        self.renderer = renderer

    def __call__(self, caller, event):
        self.level = vtk.vtkMath.Round(caller.GetRepresentation().GetValue())
        self.Octree.GenerateRepresentation(self.level, self.polyData)
        self.renderer.Render()


def OctreeVisualize(polyData):
    colors = vtk.vtkNamedColors()
    bounds = polyData.GetBounds()
    print( "# of points: ", polyData.GetNumberOfPoints())

    drange =[1, 2, 3]
    for i in range(3):
      drange[i] = bounds[2 * i + 1] - bounds[2 * i]

    sampleSize = polyData.GetNumberOfPoints() * 0.00005
    if (sampleSize < 10):
        sampleSize = 10
    print("Sample size is: ", sampleSize)
      # Do we need to estimate normals?
    distance = vtk.vtkSignedDistance()
    if (polyData.GetPointData().GetNormals()):
        print("Using normals from input file")
        distance.SetInputData(polyData)
    else:
        print("Estimating normals using PCANormalEstimation")
        normals = vtk.vtkPCANormalEstimation()
        normals.SetInputData(polyData)
        normals.SetSampleSize(sampleSize)
        normals.SetNormalOrientationToGraphTraversal()
        normals.FlipNormalsOn()
        distance.SetInputConnection(normals.GetOutputPort())

    print("Range: ", drange[0], ", ", drange[1], ", ", drange[2])
    dimension = 256
    radius = max(max(drange[0], drange[1]), drange[2]) /dimension * 4 # ~4 voxels
    print("Radius: ",radius)

    distance.SetRadius(radius)
    distance.SetDimensions(dimension, dimension, dimension)
    distance.SetBounds(bounds[0] - drange[0] * .1, bounds[1] + drange[0] * .1,
                      bounds[2] - drange[1] * .1, bounds[3] + drange[1] * .1,
                      bounds[4] - drange[2] * .1, bounds[5] + drange[2] * .1)

    surface = vtk.vtkExtractSurface()
    surface.SetInputConnection(distance.GetOutputPort())
    surface.SetRadius(radius * .99)
    surface.Update()

    plyMapper = vtk.vtkPolyDataMapper()
    plyMapper.SetInputConnection(surface.GetOutputPort())
    plyActor = vtk.vtkActor()
    plyActor.SetMapper(plyMapper)
    plyActor.GetProperty().SetInterpolationToFlat()
    plyActor.GetProperty().SetRepresentationToPoints()
    plyActor.GetProperty().SetColor(colors.GetColor3d("Yellow"))

    octree = vtk.vtkOctreePointLocator()
    octree.SetMaximumPointsPerRegion(5)
    octree.SetDataSet(polyData)
    octree.BuildLocator()

    polydata = vtk.vtkPolyData()
    octree.GenerateRepresentation(0, polydata)

    octreeMapper = vtk.vtkPolyDataMapper()
    octreeMapper.SetInputData(polydata)

    octreeActor = vtk.vtkActor()
    octreeActor.SetMapper(octreeMapper)
    octreeActor.GetProperty().SetInterpolationToFlat()
    octreeActor.GetProperty().SetRepresentationToWireframe()
    octreeActor.GetProperty().SetColor(colors.GetColor3d("SpringGreen"))

    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(plyActor)
    renderer.AddActor(octreeActor)
    renderer.SetBackground(colors.GetColor3d("MidnightBlue"))

    renderWindow.SetWindowName("OctreeVisualize")
    renderWindow.SetSize(600, 600)
    renderWindow.Render()

    sliderRep = vtk.vtkSliderRepresentation2D()
    sliderRep.SetMinimumValue(0)
    sliderRep.SetMaximumValue(octree.GetLevel())
    sliderRep.SetValue(0)
    sliderRep.SetTitleText("Level")
    sliderRep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    sliderRep.GetPoint1Coordinate().SetValue(.2, .2)
    sliderRep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    sliderRep.GetPoint2Coordinate().SetValue(.8, .2)
    sliderRep.SetSliderLength(0.075)
    sliderRep.SetSliderWidth(0.05)
    sliderRep.SetEndCapLength(0.05)
    sliderRep.GetTitleProperty().SetColor(colors.GetColor3d("Beige"))
    sliderRep.GetCapProperty().SetColor(colors.GetColor3d("MistyRose"))
    sliderRep.GetSliderProperty().SetColor(colors.GetColor3d("LightBlue"))
    sliderRep.GetSelectedProperty().SetColor(colors.GetColor3d("Violet"))

    sliderWidget = vtk.vtkSliderWidget()
    sliderWidget.SetInteractor(renderWindowInteractor)
    sliderWidget.SetRepresentation(sliderRep)
    sliderWidget.SetAnimationModeToAnimate()
    sliderWidget.EnabledOn()

    callback = SliderObserver(octree, polydata, renderer)
    callback.Octree = octree
    callback.PolyData = polydata
    callback.Renderer = renderer

    sliderWidget.AddObserver('InteractionEvent', callback)

    renderWindowInteractor.Initialize()
    renderWindow.Render()

    renderWindowInteractor.Start()


if __name__ == '__main__':
    #filename = get_program_parameters()
    filename ="./res/ism_test_wolf.vtp"
    polyData = ReadPolyData(filename)
    OctreeVisualize(polyData)
