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
    parser.add_argument('filename', help='./res/ism_test_cat.vtp')
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
    #filename = get_program_parameters()
    filename ="./res/ism_test_wolf.vtp"
    polyData = ReadPolyData(filename)

    bounds = polyData.GetBounds()
    drange = [0, 0, 0];
    for i in range(3):
        drange[i] = bounds[2 * i + 1] - bounds[2 * i]
    print("Range: ", drange[0], ", ", drange[1], ", " ,drange[2])

    maxRange = max(max(drange[0], drange[1]), drange[2])

    print( "# of original points: ", polyData.GetNumberOfPoints())
    densify = vtk.vtkDensifyPointCloudFilter()
    densify.SetInputData(polyData)
    densify.SetMaximumNumberOfIterations(5)
    densify.SetTargetDistance(maxRange * .03)
    densify.SetNumberOfClosestPoints(10)
    densify.Update()
    print("# of densified points: ", densify.GetOutput().GetNumberOfPoints())

    colors = vtkNamedColors()
    radius = maxRange * .01
    sphereSource1 = vtkSphereSource()
    sphereSource1.SetRadius(radius)

    glyph3D1 = vtkGlyph3DMapper()
    glyph3D1.SetInputData(polyData)
    glyph3D1.SetSourceConnection(sphereSource1.GetOutputPort())
    glyph3D1.ScalarVisibilityOff()
    glyph3D1.ScalingOff()

    glyph3DActor1 = vtkActor()
    glyph3DActor1.SetMapper(glyph3D1)
    glyph3DActor1.GetProperty().SetColor(
        colors.GetColor3d("Banana"))

    # #
    sphereSource2 = vtkSphereSource()
    sphereSource2.SetRadius(radius * .75)

    glyph3D2 = vtkGlyph3DMapper()
    glyph3D2.SetInputConnection(densify.GetOutputPort())
    glyph3D2.SetSourceConnection(sphereSource2.GetOutputPort())
    glyph3D2.ScalarVisibilityOff()
    glyph3D2.ScalingOff()

    glyph3DActor2 = vtkActor()
    glyph3DActor2.SetMapper(glyph3D2)
    glyph3DActor2.GetProperty().SetColor(colors.GetColor3d("Tomato"))

    # Create graphics stuff #
    ren1 = vtkRenderer()
    ren1.SetBackground(colors.GetColor3d("SlateGray"))

    renWin = vtkRenderWindow()
    renWin.AddRenderer(ren1)
    renWin.SetSize(512, 512)
    renWin.SetWindowName("DensifyPoints")

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Add  the actors to the renderer, set  the  background and size  #
    ren1.AddActor(glyph3DActor1)
    ren1.AddActor(glyph3DActor2)

    # Generate  an  interesting  view  #
    ren1.GetActiveCamera().SetPosition(1, 0, 0)
    ren1.GetActiveCamera().SetFocalPoint(0, 1, 0)
    ren1.GetActiveCamera().SetViewUp(0, 0, 1)
    ren1.ResetCamera()
    ren1.GetActiveCamera().Dolly(1.0)
    ren1.ResetCameraClippingRange()

    renWin.Render()
    iren.Initialize()
    iren.Start()

if __name__ == '__main__':
    main()