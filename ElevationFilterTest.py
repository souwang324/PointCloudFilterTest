#!/usr/bin/env python
# noinspection PyUnresolvedReferences
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
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Read a VTK XML PolyData file.'
    epilogue = ''''''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='./res/ism_test_cat.vtp')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()
    #filename = get_program_parameters()
    filename ="./res/ism_test_wolf.vtp"

    reader = vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()

    #polyData = vtkPolyData()
    #polyData.SetPoints(reader.GetOutput());

    glyphFilter = vtkVertexGlyphFilter()
    glyphFilter.SetInputData(reader.GetOutput())
    glyphFilter.Update()

    bounds = glyphFilter.GetOutput().GetBounds()
    elevationFilter =vtkElevationFilter()
    elevationFilter.SetInputConnection(glyphFilter.GetOutputPort())
    elevationFilter.SetLowPoint(0, 0, bounds[5])
    elevationFilter.SetHighPoint(0, 0, bounds[4])

    dataMapper = vtkPolyDataMapper()
    dataMapper.SetInputConnection(elevationFilter.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(dataMapper)

    renderer = vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(.0, .0, .0)

    renderwind = vtkRenderWindow()
    renderwind.AddRenderer(renderer)

    style = vtkInteractorStyleTrackballCamera()

    renderwindIt = vtkRenderWindowInteractor()
    renderwindIt.SetRenderWindow(renderwind)
    renderwindIt.SetInteractorStyle(style)

    renderwind.Render()
    renderwindIt.Start()

if __name__ == '__main__':
    main()
