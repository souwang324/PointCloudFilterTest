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

def get_program_parameters():
    import argparse
    description = 'Read a VTK XML PolyData file.'
    epilogue = ''''''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='horse.vtp.')
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


def main():
    colors = vtkNamedColors()
    #filename = get_program_parameters()
    filename ="./res/ism_test_cat.vtp"
    polyData = ReadPolyData(filename)
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

    surfaceMapper = vtkPolyDataMapper()
    surfaceMapper.SetInputConnection(surface.GetOutputPort())

    back = vtkProperty()
    back.SetColor(colors.GetColor3d("Banana"))

    surfaceActor = vtkActor()
    surfaceActor.SetMapper(surfaceMapper)
    surfaceActor.GetProperty().SetColor(colors.GetColor3d("Tomato"))
    surfaceActor.SetBackfaceProperty(back)

  # Create graphics stuff  #
    ren1 = vtkRenderer()
    ren1.SetBackground(colors.GetColor3d("SlateGray"))

    renWin = vtkRenderWindow()
    renWin.AddRenderer(ren1)
    renWin.SetSize(512, 512)
    renWin.SetWindowName("ExtractSurface")

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Add the actors to the renderer, set the background and size #
    ren1.AddActor(surfaceActor)

    # Generate an interesting view
    #
    ren1.ResetCamera()
    ren1.GetActiveCamera().Azimuth(120)
    ren1.GetActiveCamera().Elevation(30)
    ren1.GetActiveCamera().Dolly(1.0)
    ren1.ResetCameraClippingRange()

    renWin.Render()
    iren.Initialize()
    iren.Start()

if __name__ == '__main__':
        main()