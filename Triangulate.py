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
    colors = vtkNamedColors()
    #filename = get_program_parameters()
    filename ="./res/Torso.vtp"
    #filename ="./res/ism_test_wolf.vtp"
    polyData = ReadPolyData(filename)
    triangleFilter = vtkTriangleFilter()
    triangleFilter.SetInputData(polyData)
    triangleFilter.Update()

    inputMapper = vtkPolyDataMapper()
    inputMapper.SetInputConnection(triangleFilter.GetOutputPort())

    inputActor = vtkActor()
    inputActor.SetMapper(inputMapper)
    inputActor.GetProperty().SetRepresentationToWireframe()
    inputActor.GetProperty().SetColor(
        colors.GetColor3d("MistyRose"))

    triangleMapper = vtkPolyDataMapper()
    triangleMapper.SetInputConnection(triangleFilter.GetOutputPort())
    triangleActor = vtkActor()
    triangleActor.SetMapper(triangleMapper)
    #triangleActor.GetProperty().SetRepresentationToWireframe()
    triangleActor.GetProperty().SetRepresentationToSurface()
    triangleActor.GetProperty().SetColor(colors.GetColor3d("MistyRose"))

    inputActor = vtkActor()
    inputActor.SetMapper(inputMapper)
    inputActor.GetProperty().SetRepresentationToWireframe()
    inputActor.GetProperty().SetColor(colors.GetColor3d("MistyRose"))

    # There Will be one render window
    renderWindow = vtkRenderWindow()
    renderWindow.SetSize(600, 300)
    renderWindow.SetWindowName("Triangulate")

    # And one interactor
    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    # Define viewport ranges # (xmin, ymin, xmax, ymax)
    leftViewport = [0.0, 0.0, 0.5, 1.0]
    rightViewport = [0.5, 0.0, 1.0, 1.0]

    # Setup both renderers
    leftRenderer = vtkRenderer()
    renderWindow.AddRenderer(leftRenderer)
    leftRenderer.SetViewport(leftViewport)
    leftRenderer.SetBackground(colors.GetColor3d("SaddleBrown"))

    rightRenderer = vtkRenderer()
    renderWindow.AddRenderer(rightRenderer)
    rightRenderer.SetViewport(rightViewport)
    rightRenderer.SetBackground(colors.GetColor3d("DarkSlateGray"))

    leftRenderer.AddActor(inputActor)
    rightRenderer.AddActor(triangleActor)

    leftRenderer.ResetCamera()
    rightRenderer.ResetCamera()

    renderWindow.Render()
    interactor.Start()

if __name__ == '__main__':
    main()

